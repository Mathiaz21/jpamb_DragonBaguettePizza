import collections
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import TextIO, TypeVar
import re
import subprocess
import sys
import csv
import json

from jpamb_utils import InputParser, JvmType, JvmValue, MethodId

import loguru

W = TypeVar("W", bound=TextIO)

QUERIES = [
    "*",
    "assertion error",
    "divide by zero",
    "null pointer",
    "ok",
    "out of bounds",
]


def re_parser(ctx_, parms_, expr):
    import re

    if expr:
        return re.compile(expr)


def build_c(input_file, logger):
    """Build a C file (hopefully platform independent)"""
    from os import environ
    import platform
    import shutil

    compiler = shutil.which(environ.get("CC", "gcc"))

    if not compiler:
        logger.error("Could not find $CC or gcc compiler on PATH")
        raise Exception("Could not find $CC or gcc compiler on PATH")

    output_file = input_file.with_suffix("")

    if platform.system() == "Windows":
        output_file = output_file.with_suffix(".exe")
    subprocess.check_call([compiler, "-o", output_file, input_file, "-lm"])

    return output_file


def setup_logger(verbose):
    LEVELS = ["SUCCESS", "INFO", "DEBUG", "TRACE"]
    from loguru import logger

    lvl = LEVELS[verbose]

    if lvl == "TRACE":
        logger.remove()
        logger.add(
            sys.stderr,
            format="<green>{elapsed}</green> | <level>{level: <8}</level> | <red>{extra[process]:<8}</red> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=LEVELS[verbose],
        )
    else:
        logger.remove()
        logger.add(
            sys.stderr,
            format="<red>{extra[process]:<8}</red>: <level>{message}</level>",
            level=LEVELS[verbose],
        )

    return logger.bind(process="main")


@dataclass(frozen=True, order=True)
class Input:
    val: tuple[JvmType, ...]

    @staticmethod
    def parse(string: str) -> "Input":
        parsed_args = InputParser(string).parse_inputs()
        input = Input(tuple(parsed_args))
        assert string == str(input), f"{input} should formatted as {string}"
        return input

    def __str__(self) -> str:
        return self.print(StringIO()).getvalue()

    def print(self, file: W = sys.stdout) -> W:
        open, close = "()"
        file.write(open)
        file.write(", ".join(map(str, self.val)))
        file.write(close)
        return file


def summary64(cmd):
    import base64
    import hashlib

    return base64.b64encode(hashlib.sha256(str(cmd).encode()).digest()).decode()[:8]


def run_cmd(cmd: list[str], /, timeout, logger, **kwargs):
    import shlex
    import threading
    from time import monotonic, perf_counter_ns

    logger = logger.bind(process=summary64(cmd))
    cp = None
    stdout = []
    stderr = []
    tout = None
    try:
        start = monotonic()
        start_ns = perf_counter_ns()

        if timeout:
            end = start + timeout
        else:
            end = None

        logger.debug(f"starting: {shlex.join(map(str, cmd))}")

        cp = subprocess.Popen(
            cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, **kwargs
        )
        assert cp and cp.stdout and cp.stderr

        def log_lines(cp):
            assert cp.stderr
            with cp.stderr:
                for line in iter(cp.stderr.readline, ""):
                    stderr.append(line)
                    logger.debug(line[:-1])

        def save_result(cp):
            assert cp.stdout
            with cp.stdout:
                stdout.append(cp.stdout.read())

        terr = threading.Thread(target=log_lines, args=(cp,), daemon=True)
        terr.start()
        tout = threading.Thread(target=save_result, args=(cp,), daemon=True)
        tout.start()

        terr.join(end and end - monotonic())
        tout.join(end and end - monotonic())
        exitcode = cp.wait(end and end - monotonic())
        end_ns = perf_counter_ns()

        if exitcode != 0:
            raise subprocess.CalledProcessError(
                cmd=cmd,
                returncode=exitcode,
                stderr="\n".join(stderr),
                output=stdout[0].strip(),
            )

        logger.debug("done")
        return (stdout[0].strip(), end_ns - start_ns)
    except subprocess.CalledProcessError as e:
        if tout:
            tout.join()
        e.stdout = stdout[0].strip()
        raise e
    except subprocess.TimeoutExpired:
        logger.debug("process timed out, terminating")
        if cp:
            cp.terminate()
            if cp.stdout:
                cp.stdout.close()
            if cp.stderr:
                cp.stderr.close()
        raise


def runtime(*args, enable_assertions=False, **kwargs):
    pargs = ["java", "-cp", "target/classes/"]

    if enable_assertions:
        pargs += ["-ea"]

    pargs += ["jpamb.Runtime"]
    pargs += args

    return subprocess.check_output(pargs, text=True, **kwargs)


@dataclass(frozen=True, order=True)
class Case:
    methodid: MethodId
    input: Input
    result: str

    @staticmethod
    def from_spec(line):
        if not (m := re.match(r"([^ ]*) +(\([^)]*\)) -> (.*)", line)):
            raise ValueError(f"Unexpected line: {line!r}")
        return Case(MethodId.parse(m.group(1)), Input.parse(m.group(2)), m.group(3))

    def __str__(self) -> str:
        return f"{self.methodid.class_name}.{self.methodid.method_name}:{self.input} -> {self.result}"

    @staticmethod
    def by_methodid(iterable) -> list[tuple[MethodId, list["Case"]]]:
        cases_by_id = collections.defaultdict(list)

        for c in iterable:
            cases_by_id[c.methodid].append(c)

        return sorted(cases_by_id.items())


@dataclass(frozen=True)
class Prediction:
    wager: float

    @staticmethod
    def parse(string: str) -> "Prediction":
        if m := re.match(r"([^%]*)\%", string):
            p = float(m.group(1)) / 100
            return Prediction.from_probability(p)
        else:
            return Prediction(float(string))

    @staticmethod
    def from_probability(p: float) -> "Prediction":
        negate = False
        if p < 0.5:
            p = 1 - p
            negate = True
        if p == 1:
            x = float("inf")
        else:
            x = (1 - 2 * p) / (-1 + p) / 2
        return Prediction(-x if negate else x)

    def to_probability(self) -> float:
        if self.wager == float("-inf"):
            return 0
        if self.wager == float("inf"):
            return 0
        w = abs(self.wager) * 2
        r = (w + 1) / (w + 2)
        return r if self.wager > 0 else 1 - r

    def score(self, happens: bool):
        wager = (-1 if not happens else 1) * self.wager
        if wager > 0:
            if wager == float("inf"):
                return 1
            else:
                return 1 - 1 / (wager + 1)
        else:
            return wager

    def __str__(self):
        return f"{self.to_probability():0.2%}"


@dataclass(frozen=True)
class Suite:
    workfolder: Path
    queries: list[str]
    logger: loguru._logger.Logger

    @property
    def classfiles(self) -> Path:
        return self.workfolder / "target/classes"

    def decompiled(self, create=True) -> Path:
        decompiled = self.workfolder / "decompiled"
        if create:
            decompiled.mkdir(parents=True, exist_ok=True)
        return decompiled

    def stats_folder(self, create=True) -> Path:
        stats_folder = self.workfolder / "stats"
        if create:
            stats_folder.mkdir(parents=True, exist_ok=True)
        return stats_folder

    def build(self):
        self.logger.info("Building the benchmark suite")
        subprocess.call(["mvn", "compile"], cwd=self.workfolder)
        self.logger.info("Done")

    def update_cases(self):
        stats = self.stats_folder()
        self.logger.info("Writing the cases to file")
        with open(stats / "cases.txt", "w") as f:
            lines = runtime(cwd=self.workfolder).splitlines(keepends=True)
            f.write("".join(sorted(lines)))

        self.logger.info("Updating the distribution")

        with open(stats / "distribution.csv", "w") as f:
            w = csv.writer(f, dialect="unix")
            w.writerow(["method"] + self.queries)

            sums = collections.Counter()
            total = 0

            for mid, cases in Case.by_methodid(self.cases()):
                occ = []
                total += 1
                for t in self.queries:
                    if any(c.result == t for c in cases):
                        occ.append(1)
                        sums[t] += 1
                    else:
                        occ.append(0)

                w.writerow([mid] + occ)

            w.writerow(["-"] + [f"{sums[t] / total:0.4%}" for t in self.queries])

        self.logger.info("Done")

    def cases(self):
        with open(self.stats_folder() / "cases.txt", "r") as f:
            for r in f.readlines():
                yield Case.from_spec(r[:-1])

    def check(self):
        self.logger.info("Checking cases")
        failed = []

        for case in self.cases():
            self.logger.debug(f"Testing {case!s:<74}")
            cmd = ["java", "-cp", self.classfiles, "-ea"]
            cmd += ["jpamb.Runtime", str(case.methodid), str(case.input)]
            timeout = 0.5
            try:
                result, time = run_cmd(
                    cmd,
                    timeout=timeout,
                    logger=self.logger,
                )
                self.logger.debug(f"Got {result!r} in {time/10**9}s")
            except subprocess.CalledProcessError:
                result = None
                self.logger.debug(f"Process failed.")
            except subprocess.TimeoutExpired:
                result = "*"
                self.logger.debug(f"Timed out after {timeout}.")

            outcome = "SUCCESS"
            if case.result != result:
                outcome = "FAILED"
                failed.append(case)

            self.logger.info(f"Testing {case!s:<74}: {outcome}")

        if failed:
            self.logger.error("Failed checks:")
            for f in failed:
                self.logger.error(f)
            return False
        else:
            self.logger.success("Successfully verified all cases.")
            return True

    def decompile(self):
        self.logger.info("Decompiling classfiles")
        decompiled = self.decompiled()
        for clazz in self.classfiles.glob("**/*.class"):
            jsonclazz = decompiled / clazz.relative_to(self.classfiles).with_suffix(
                ".json"
            )
            self.logger.info(
                f"Converting {clazz.relative_to(self.workfolder)} to {jsonclazz.relative_to(self.workfolder)}"
            )
            jsonclazz.parent.mkdir(parents=True, exist_ok=True)
            cmd = ["jvm2json", f"-s{clazz}"]
            res, _ = run_cmd(cmd, timeout=None, logger=self.logger)
            if not res:
                self.logger.warning(f"jvm2json: {res}")
            self.logger.trace(res)
            encoding = json.loads(res)
            with open(jsonclazz, "w") as f:
                json.dump(encoding, f, indent=2, sort_keys=True)
        self.logger.success("Done decompiling classfiles")
