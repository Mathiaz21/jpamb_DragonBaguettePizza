#!/usr/bin/env python3
""" The skeleton for writing an interpreter given the bytecode.
"""

from dataclasses import dataclass
import sys, logging
from typing import Optional

from jpamb_utils import InputParser, IntValue, MethodId

l = logging
l.basicConfig(level=logging.DEBUG, format="%(message)s")


@dataclass
class SimpleInterpreter:
    bytecode: list
    locals: list
    stack: list
    pc: int = 0
    done: Optional[str] = None

    def interpet(self, limit=10):
        for i in range(limit):
            next = self.bytecode[self.pc]
            l.debug(f"STEP {i}:")
            l.debug(f"  PC: {self.pc} {next}")
            l.debug(f"  LOCALS: {self.locals}")
            l.debug(f"  STACK: {self.stack}")

            if fn := getattr(self, "step_" + next["opr"], None):
                fn(next)
            else:
                return f"can't handle {next['opr']!r}"

            if self.done:
                break
        else:
            self.done = "out of time"

        l.debug(f"DONE {self.done}")
        l.debug(f"  LOCALS: {self.locals}")
        l.debug(f"  STACK: {self.stack}")

        return self.done

    def step_push(self, bc):
        val = bc["value"]
        if val is not None:
            if bc["type"] == "integer":
                return IntValue(bc["value"])
            raise ValueError(f"Currently unknown value {bc}")

        self.stack.insert(0, val)
        self.pc += 1

    def step_return(self, bc):
        if bc["type"] is not None:
            self.stack.pop(0)
        self.done = "ok"


if __name__ == "__main__":
    methodid = MethodId.parse(sys.argv[1])
    inputs = InputParser.parse(sys.argv[2])
    m = methodid.load()
    i = SimpleInterpreter(m["code"]["bytecode"], [i.tolocal() for i in inputs], [])
    print(i.interpet())
