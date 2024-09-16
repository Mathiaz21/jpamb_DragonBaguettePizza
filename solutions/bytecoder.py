#!/usr/bin/env python3
""" A very stupid syntatic bytecode analysis, that only checks for assertion errors.
"""

import sys, logging

l = logging
l.basicConfig(level=logging.DEBUG)

(name,) = sys.argv[1:]

l.debug("check assertion")

import json, re
from pathlib import Path

l.debug("read the method name")

# Read the method_name
RE = r"(?P<class_name>.+)\.(?P<method_name>.*)\:\((?P<params>.*)\)(?P<return>.*)"
if not (i := re.match(RE, name)):
    l.error("invalid method name: %r", name)
    sys.exit(-1)

TYPE_LOOKUP = {
    "Z": "boolean",
    "I": "int",
}

classfile = (Path("decompiled") / i["class_name"].replace(".", "/")).with_suffix(
    ".json"
)

with open(classfile) as f:
    l.debug("read decompiled classfile %s", classfile)
    classfile = json.load(f)

l.debug("looking up method")
# Lookup method
for m in classfile["methods"]:
    if (
        m["name"] == i["method_name"]
        and len(i["params"]) == len(m["params"])
        and all(
            TYPE_LOOKUP[tn] == t["type"]["base"]
            for tn, t in zip(i["params"], m["params"])
        )
    ):
        break
else:
    print("Could not find method")
    sys.exit(-1)

##########################################################

######### ANALYSIS OF THE METHOD INSTR BY INSTR ##########

##########################################################

simulated_stack = []

# TODO  : write a function that detects divisions by zero and by n
# Using the simulated_stack




l.debug("trying to find an assertion error being created")
# Look if the method contains an assertion error:
for inst in m["code"]["bytecode"]:

    if (

        inst["opr"] == "invoke"
        and inst["method"]["ref"]["name"] == "java/lang/AssertionError"
    ):

        l.debug("Found an assertion error")
        print("assertion error;80%")
        
    else:

        l.debug("Did not find an assertion error")
        print("assertion error;20%")
        sys.exit(0)


