#!/usr/bin/env python3
""" The jpamb evaluator
"""

from collections import defaultdict
from datetime import datetime
from pathlib import Path
import click
import math
import os
import subprocess
from time import perf_counter_ns

from utils import *


def add_timeout(m):
    return m


WORKFOLDER = Path(os.path.abspath(__file__)).parent.parent


def tool_parser(ctx_, parms_, tools):
    resulting_tools = []
    for tool in tools:
        nameandtool = tool.split("=")
        if len(nameandtool) > 1:
            name, tool = nameandtool
            tool = Path(tool).absolute()
        else:
            tool = Path(nameandtool[0]).absolute()
            name = tool.with_suffix("").name
        resulting_tools.append((name, tool))
    return resulting_tools


def experiment_parser(ctx_, parms_, experiment):
    import yaml

    with open(experiment) as f:
        experiment = yaml.safe_load(f)

    context = "badly formated experiment: "
    if not "group_name" in experiment:
        raise click.UsageError(context + "no 'group_name'")

    if not "tools" in experiment:
        raise click.UsageError(context + "no 'tools'")

    if not isinstance(experiment["tools"], dict):
        raise click.UsageError(context + "'tools' should be a dictionary")

    for tn, t in experiment["tools"].items():
        if not ("technologies" in t and isinstance(t["technologies"], list)):
            raise click.UsageError(
                context + f"'tools.{tn}.technologies' should be a list"
            )

        if not ("executable" in t) or not (
            isinstance(t["executable"], list) or isinstance(t["executable"], str)
        ):
            raise click.UsageError(
                context
                + f"'tools.{tn}.executable should be an executable or a list of arguments"
            )
        elif isinstance(t["executable"], str):
            t["executable"] = [t["executable"]]

    if not "machine" in experiment:
        raise click.UsageError(context + "no 'machine'")

    for k in ["os", "processor", "memory"]:
        if not experiment["machine"][k]:
            raise click.UsageError(context + f"no 'machine.{k}'")

    if not "for_science" in experiment:
        raise click.UsageError(context + "no 'for_science'")

    if not isinstance(experiment["for_science"], bool):
        raise click.UsageError(context + "'for_science' should be true or false")

    return experiment


def calibrate(sieve_exe, log_calibration):
    calibrators = [100_000, 100_000]
    calibration = 0
    for count in calibrators:
        start = perf_counter_ns()
        subprocess.check_output([sieve_exe, str(count)])
        end = perf_counter_ns()
        diff = end - start
        calibration += diff
        log_calibration(count=count, time=diff)

    calibration /= len(calibrators)
    return calibration


@click.command()
@click.option(
    "--timeout",
    show_default=True,
    default=2.0,
    help="timeout in seconds.",
)
@click.option(
    "--filter-tools",
    help="only take tools that matches the regex.",
    callback=re_parser,
)
@click.option(
    "--filter-methods",
    help="only take methods that matches the regex.",
    callback=re_parser,
)
@click.option(
    "-N",
    "--iterations",
    show_default=True,
    default=1,
    help="number of iterations.",
)
@click.option("-v", "--verbose", count=True)
@click.option("-o", "--output", show_default=True, default=WORKFOLDER / "result.json")
@click.argument("EXPERIMENT", callback=experiment_parser)
def evaluate(
    experiment, timeout, iterations, verbose, filter_methods, filter_tools, output
):
    """Given an command check if it can predict the results."""
    import random, itertools

    logger = setup_logger(verbose)
    suite = Suite(WORKFOLDER, QUERIES, logger)
    tools = experiment["tools"]
    by_tool = defaultdict(list)

    with open(WORKFOLDER / "CITATION.cff") as f:
        import yaml

        version = yaml.safe_load(f)["version"]

    logger.info(f"Version {version}")

    sieve = WORKFOLDER / "timer" / "sieve.c"

    logger.info(f"Building timer from {sieve}")
    sieve_exe = build_c(sieve, logger)

    for i in range(iterations):
        calibration = calibrate(sieve_exe, lambda **kwargs: ())
        logger.info(f"Base calibrated {i}: {calibration/1_000_000:0.0f}ms")

    for m, cases in Case.by_methodid(suite.cases()):
        if filter_methods and not filter_methods.search(str(m)):
            logger.trace(f"{m} did not match {filter_methods}")
            continue

        for n, (tool_name, tool) in itertools.product(
            range(iterations), random.sample(sorted(tools.items()), k=len(tools))
        ):
            if filter_tools and not filter_tools.search(tool_name):
                logger.trace(f"{tool_name} did not match {filter_tools}")
                continue

            logger.debug(f"Testing {tool_name!r}")
            try:
                fpred, time_ns = run_cmd(
                    tool["executable"] + [str(m)],
                    timeout=timeout,
                    logger=logger,
                )
            except subprocess.CalledProcessError as e:
                logger.warning(f"Tool {tool_name!r} failed with {e}")
                fpred, time_ns = "", float("NaN")
            except subprocess.TimeoutExpired:
                logger.warning(f"Tool {tool_name!r} timed out")
                fpred, time_ns = "", float("NaN")

            total = 0
            time = time_ns / 1_000_000_000
            calibrations = []
            calibration = calibrate(
                sieve_exe,
                lambda **kwarg: calibrations.append(kwarg),
            )
            relative = time_ns / calibration

            predictions = {}
            for line in fpred.splitlines():
                try:
                    query, pred = line.split(";")
                    logger.debug(f"response: {line}")
                except ValueError:
                    logger.warning(f"Tool {tool_name!r} produced bad output")
                    logger.warning(line)
                    continue
                if not query in QUERIES:
                    logger.warning(f"{query!r} not a known query")
                    continue
                prediction = Prediction.parse(pred)
                predictions[query] = prediction
                sometimes = any(query == c.result for c in cases)
                score = prediction.score(sometimes)
                logger.debug(
                    f"Check query {query!r} ({sometimes}): waged {prediction.wager:0.3f}"
                    f" and predicted {prediction.to_probability():0.3%}, got {score:0.3f}"
                )
                total += score

            pretty = ", ".join(
                f"{k} ({str(p)})" for k, p in sorted(predictions.items())
            )
            logger.info(
                f"{tool_name!r} scored {total:0.2f} in {time:0.3}s/{relative:0.3}x with {pretty}"
            )

            by_tool[tool_name].append(
                {
                    "method": str(m),
                    "iteration": n,
                    "wagers": {k: p.wager for k, p in predictions.items()},
                    "time": time_ns,
                    "relative": relative,
                    "score": total,
                    "calibration": calibration,
                    "calibrations": calibrations,
                }
            )

        logger.success(f"Ran {m}")

    for k, t in sorted(by_tool.items()):
        if not t:
            logger.warning(f"No experiments for {k}")
            continue
        score = sum(r["score"] for r in t) / iterations
        time = sum(r["time"] for r in t) / len(t)
        relative = math.exp(sum(math.log(r["relative"]) for r in t) / len(t))
        tools[k]["results"] = t
        tools[k]["score"] = score
        tools[k]["time"] = time
        tools[k]["relative"] = relative

        logger.success(
            f"Tested {k}: score {score:0.2f} in avg {time/1_000_000:0.0f}ms/{relative:0.3f}x"
        )

    experiment["timestamp"] = int(datetime.now().timestamp() * 1000)
    experiment["version"] = version

    with open(output, "w", encoding="utf-8") as fp:
        json.dump(experiment, fp)

    logger.success(f"Written results to {output!r}")


if __name__ == "__main__":
    evaluate()
