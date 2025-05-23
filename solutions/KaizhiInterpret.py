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
class Interpreter:
    bytecode: list
    locals: list
    stack: list
    objects: list
    pc: int = 0
    done: Optional[str] = None

    def interpet(self, limit=41):
        for i in range(limit):
            next = self.bytecode[self.pc]
            l.debug(f"len of bytecode: {len(self.bytecode)}")
            l.debug(f"STEP {i}:")
            l.debug(f"  PC: {self.pc} {next}")
            l.debug(f"  LOCALS: {self.locals}")
            l.debug(f"  STACK: {self.stack}")
            l.debug(f"  OBJECTS: {self.objects}")

            # if fn := getattr(self, "step_" + next["opr"], None):
            #     fn(next)
            # else:
            #     return f"can't handle {next['opr']!r}"
            if "opr" in next:
                 if fn := getattr(self, "step_" + next["opr"], None):
                    fn(next)
            elif "condition" in next:
                 if fn := getattr(self, "condition_" + next["condition"], None):
                    fn(next)


            if self.done:
                break
        else:
            self.done = "out of time"

        l.debug(f"DONE {self.done}")
        l.debug(f"  LOCALS: {self.locals}")
        l.debug(f"  STACK: {self.stack}")
        l.debug(f"  OBJECTS: {self.objects}")

        return self.done

    def step_push(self, bc):
        val = bc["value"]
        if val is not None:
            if val["type"] == "integer":
                print(val["value"])

                # self.stack.insert(0, val["value"])
                # return IntValue(val["value"])
            # raise ValueError(f"Currently unknown value {bc}")

        self.stack.append(val["value"])
        self.pc += 1

    def step_newarray(self, bc):
        if bc["dim"] == 1:
            print("new array")
            self.stack.append([])
            self.objects.append([])
        self.pc += 1

    def step_dup(self, bc):
        # mylist is the first element in the stack
        mylist = self.stack.pop(-1)
        self.stack.append(mylist)
        self.stack.append(mylist)
        self.pc += 1

    def step_array_store(self, bc):
        value = self.stack.pop(-1)
        index = self.stack.pop(-1)
        newarray = self.stack.pop(-1)
        newarray.insert(index, value)
        print(newarray)
        self.objects[0] = newarray
        # self.objects[index].append(value)
        self.pc += 1

    def step_store(self, bc):
        index = bc["index"]
        self.locals.insert(index,self.stack.pop(-1))
        self.pc += 1

    def step_load(self, bc):
        index = bc["index"]
        value = self.locals[index]
        print(index)
        print(value)
        self.stack.append(value)
        self.pc += 1

    def step_arraylength(self, bc):
        mylist = self.stack.pop(-1)
        length = len(mylist)
        self.stack.append(length)
        self.pc += 1

    def step_invoke(self, bc):
        methodid = MethodId.parse(bc["method"])
        m = methodid.load()
        i = Interpreter(m["code"]["bytecode"], self.stack, self.locals, self.objects)
        self.stack = []
        self.done = i.interpet()

    def step_throw(self, bc):
        raise ValueError("throw")

    def step_incrr(self, bc):
        index = bc["index"]
        self.locals[index] += 1
        self.pc += 1

    def step_goto(self, bc):
        self.pc = bc["target"]

    def step_if(self, bc):
        a = self.stack.pop(-1)
        b = self.stack.pop(-1)
        if a == b:
            self.pc = bc["target"]
        else :
            self.pc += 1

    def step_get(self, bc):
        index = bc["index"]
        self.stack.append(self.locals[index])
        self.pc += 1


    def step_return(self, bc):
        if bc["type"] is not None:
            self.stack.pop(0)
        self.done = "ok"

    def condition_ge(self, bc):
        a = self.stack.pop(0)
        b = self.stack.pop(0)
        self.stack.insert(0, IntValue(1) if a >= b else IntValue(0))
        self.pc += 1

    def condition_ne(self, bc):
        a = self.stack.pop(0)
        b = self.stack.pop(0)
        self.stack.insert(0, IntValue(1) if a != b else IntValue(0))
        self.pc += 1

    def condition_gt(self, bc):
        a = self.stack.pop(0)
        b = self.stack.pop(0)
        self.stack.insert(0, IntValue(1) if a > b else IntValue(0))
        self.pc += 1

    def condition_new(self, bc):
        a = self.stack.pop(0)
        self.stack.insert(0, IntValue(1) if a > 0 else IntValue(0))
        self.pc += 1


if __name__ == "__main__":
    methodid = MethodId.parse(sys.argv[1])
    # inputs = InputParser.parse(sys.argv[2])
    m = methodid.load()
    # print(m["code"]["bytecode"])
    # i = Interpreter(m["code"]["bytecode"], [i.tolocal() for i in inputs], [])
    i = Interpreter(m["code"]["bytecode"],[],[],[])
    print(i.interpet())
