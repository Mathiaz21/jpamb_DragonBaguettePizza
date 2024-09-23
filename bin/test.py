#!/usr/bin/env python3
""" The jpamb tester
"""

import os
import click
from pathlib import Path
from utils import *


WORKFOLDER = Path(os.path.abspath(__file__)).parent.parent


@click.command()
@click.option(
    "--timeout",
    show_default=True,
    default=2.0,
    help="timeout in seconds.",
)
@click.option("-v", "--verbose", count=True)
@click.option(
    "--fail-fast / --no-fail-fast",
    default=True,
    help="if this option is set the test will fail with the first non-zero exitcode",
)
@click.option(
    "-o",
    "--report",
    type=click.Path(allow_dash=True),
)
@click.option(
    "--filter-methods",
    help="only take methods that matches the regex.",
    callback=re_parser,
)
@click.argument("cmd", nargs=-1, type=click.Path())
def test(
    filter_methods,
    verbose,
    cmd,
    timeout,
    report,
    fail_fast,
):
    logger = setup_logger(verbose)
    suite = Suite(WORKFOLDER, QUERIES, logger)

    if report:
        fp: TextIO = click.open_file(report, "w")  # type: ignore
        logger.add(
            fp,
            filter=(lambda record: record["extra"]["process"] != "main"),
            format="{extra[process][0]}{extra[process][1]}> {message}",
            level="DEBUG",
        )

    for case in sorted(suite.cases()):
        if filter_methods and not filter_methods.search(str(case.methodid)):
            logger.trace(f"{case} did not match {filter_methods}")
            continue
        logger.info(f"Running {case}")

        result: str
        try:
            (result, _) = run_cmd(
                cmd + (str(case.methodid), str(case.input)),
                logger=logger,
                timeout=timeout,
            )
        except subprocess.CalledProcessError as e:
            logger.error(e)
            result = e.stdout
            if fail_fast:
                for i in e.stderr.splitlines():
                    logger.warning(i)
                for i in e.stdout.splitlines():
                    logger.warning(i)
                logger.error("Failing fast")
                sys.exit(-1)

        test = r[-1] if (r := result.splitlines()) else ""
        logger.info(f"Returned {test!r}")
        if test == case.result:
            logger.success(f"Mathed {case}: {case.result!r}")
        else:
            logger.error(f"Failed {case}: {test!r} != {case.result!r}")


if __name__ == "__main__":
    test()
