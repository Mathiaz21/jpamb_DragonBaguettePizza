import os
import sys, logging
import re
import json
from pathlib import Path
from solutions.jbinary import jbinary
import tree_sitter
import tree_sitter_java

def getAssertProbability(query,node,probability=1) -> int:
    for node, t in query.captures(node).items():
        if node == "assert":
            return 70
    else:
        return 20
def getDivisionByZeroProbability(query,node,probability=1) -> int:
    for t,node in query.captures(node).items():
        if t == "division":
            if node[0].child_by_field_name("right").text.decode() == "0":
                return 80 * probability;
            else:
                return 15 * probability;
    else:
        return 1;
def getArrayAccessProbability(query,node,probability=1) -> int:
    for t,node in query.captures(node).items():
        if t == "arr":
            return 60
    else:
        return 1
def getInfiniteLoopProbability(query,node,probability=1) -> int:
    for t,node in query.captures(node).items():
        if t == "ex":
            return 60
    else:
        return 1
def print_probabilities(probabilities):
    print(f"divide by 0;{probabilities['div_by_zero'] * 100}%")
    print(f"assertion error;{probabilities['assertion_error'] * 100}%")
    print(f"array out of bounds;{probabilities['array_out_of_bounds'] * 100}%")
    print(f"*;{probabilities['infinite_loop'] * 100}%")
    print(f"ok;{probabilities['ok_non_error'] * 100}%")
def evaluate_probabilities(probabilities):
    simulated_stack = []
    l.debug("Trying to find a division operator")
    for instruction in m[jbinary.CODE][jbinary.BYTECODE]:
        l.debug("instruction:" + str(instruction))
        treat_instruction(instruction, simulated_stack)
def treat_instruction(instruction, simulated_stack):
    match instruction[jbinary.OPERATION]:
        case jbinary.PUSH:
            l.debug("instruction: push")
            treat_push(instruction, simulated_stack)
        case jbinary.LOAD:
            l.debug("instruction: load")
            treat_load(instruction, simulated_stack)
        case jbinary.BINARY_EXPR:
            l.debug("instruction: binary")
            treat_operator(instruction, simulated_stack)
def treat_push(instruction, simulated_stack):
    simulated_stack.append(instruction["value"])    
def treat_load(instruction, simulated_stack):
    simulated_stack.append(instruction["type"])
def treat_operator(instruction, simulated_stack):
    if instruction["operant"] == "div":
            treat_division(instruction, simulated_stack)
def treat_division(instruction, simulated_stack):
    l.debug("Division instruction found")
    l.debug(simulated_stack)
    if 'value' in simulated_stack[-1]:

        if simulated_stack[-1]["value"] == 0:
            l.debug("Division by zero found")
            probabilities["div_by_zero"] = 1
    else:

        l.debug("No defined dividend")
        probabilities["div_by_zero"] = (1 + 3*probabilities["div_by_zero"]) / 4

l = logging
l.basicConfig(level=logging.DEBUG)

(name,) = sys.argv[1:]

# Read the method_name
RE = r"(?P<class_name>.+)\.(?P<method_name>.*)\:\((?P<params>.*)\)(?P<return>.*)"
if not (i := re.match(RE, name)):
    l.error("invalid method name: %r", name)
    sys.exit(-1)

TYPE_LOOKUP = {
    "Z": "boolean",
    "I": "int",
}


srcfile = (Path("src/main/java") / i["class_name"].replace(".", "/")).with_suffix(
    ".java"
)

JAVA_LANGUAGE = tree_sitter.Language(tree_sitter_java.language())
parser = tree_sitter.Parser(JAVA_LANGUAGE)

with open(srcfile, "rb") as f:
    l.debug("parse sourcefile %s", srcfile)
    tree = parser.parse(f.read())

simple_classname = i["class_name"].split(".")[-1]

# To figure out how to write these you can consult the
# https://tree-sitter.github.io/tree-sitter/playground
class_q = JAVA_LANGUAGE.query(
    f"""
    (class_declaration 
        name: ((identifier) @class-name 
               (#eq? @class-name "{simple_classname}"))) @class
"""
)

for node in class_q.captures(tree.root_node)["class"]:
    break
else:
    l.error(f"could not find a class of name {simple_classname} in {srcfile}")
    sys.exit(-1)

l.debug("Found class %s", node.range)

method_name = i["method_name"]

method_q = JAVA_LANGUAGE.query(
    f"""
    (method_declaration name: 
      ((identifier) @method-name (#eq? @method-name "{method_name}"))
    ) @method
"""
)

for node in method_q.captures(node)["method"]:
    if not (p := node.child_by_field_name("parameters")):
        l.debug(f"Could not find parameteres of {method_name}")
        continue

    params = [c for c in p.children if c.type == "formal_parameter"]

    if len(params) == len(i["params"]) and all(
        (tp := t.child_by_field_name("type")) is not None
        and tp.text is not None
        and TYPE_LOOKUP[tn] == tp.text.decode()
        for tn, t in zip(i["params"], params)
    ):
        break
else:
    l.warning(f"could not find a method of name {method_name} in {simple_classname}")
    sys.exit(-1)

l.debug("Found method %s %s", method_name, node.range)

body = node.child_by_field_name("body")
assert body and body.text
for t in body.text.splitlines():
    l.debug("line: %s", t.decode())


################## SYNTAXER ##################

################## ASSERTION ##################
assert_q = JAVA_LANGUAGE.query(f"""(assert_statement) @assert""")
assertChances = getAssertProbability(assert_q,node)
print("assertion error;" + str(assertChances) + "%")
#####################################################

################## ARRAY OUT OF BOUND ##################
arrayOutOfBound_q = JAVA_LANGUAGE.query(f"""(array_access) @arr""")
arrayOutOfBoundChances = getArrayAccessProbability(arrayOutOfBound_q,node)
print("out of bounds;" + str(arrayOutOfBoundChances) + "%")
#######################################################

################## ARRAY OUT OF BOUND ##################
infiniteLoop_q = JAVA_LANGUAGE.query(f"""(while_statement)@ex""")
infiniteLoopChances = getInfiniteLoopProbability(infiniteLoop_q,node)
print("*;" + str(infiniteLoopChances) + "%")
#######################################################

#######################################################


################## BYTECODE ##################

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


probabilities = {
    "div_by_zero": 1,
    "assertion_error": 1,
    "array_out_of_bounds": 1,
    "infinite_loop": 1,
    "ok_non_error": 1
}

evaluate_probabilities(probabilities)
print("divide by zero;" + str(probabilities["div_by_zero"]) + "%")


#############################################

sys.exit(0)