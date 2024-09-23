#!/usr/bin/env python3
""" A very stupid syntatic analysis, that only checks for assertion errors.
"""

import sys, logging
from jpamb_utils import MethodId
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

JAVA_LANGUAGE = tree_sitter.Language(tree_sitter_java.language())
parser = tree_sitter.Parser(JAVA_LANGUAGE)

l = logging
l.basicConfig(level=logging.DEBUG)

(name,) = sys.argv[1:]
method = MethodId.parse(name)

srcfile = method.sourcefile()

with open(srcfile, "rb") as f:
    l.debug("parse sourcefile %s", srcfile)
    tree = parser.parse(f.read())

simple_classname = method.class_name.split(".")[-1]

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

method_name = method.method_name

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

    if len(params) == len(method.params) and all(
        (tp := t.child_by_field_name("type")) is not None
        and tp.text is not None
        and tn == tp.text.decode()
        for tn, t in zip(method.params, params)
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






l.debug("Found assertion")

################## ASSERTION ##################
assert_q = JAVA_LANGUAGE.query(f"""(assert_statement) @assert""")
assertChances = getAssertProbability(assert_q,node)
print("assertion error;" + str(assertChances) + "%")
#####################################################

################## DIVSION BY ZERO ##################
divisionByZero_q = JAVA_LANGUAGE.query(f"""(binary_expression operator:"/") @division""")
divisionByZeroChances = getDivisionByZeroProbability(divisionByZero_q,node)
print("divide by zero;" + str(divisionByZeroChances) + "%")
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

################## OKAY ###############################
# okayChances = 150 - (assertChances + divisionByZeroChances + arrayOutOfBoundChances + infiniteLoopChances)
# print("ok;" + str(okayChances) + "%")
#######################################################

sys.exit(0)

# # def enterIfScope(if_block, probability=100):

# def searchForIfStatemements(probability=100):

#     print("If detection called")
#     if_query = JAVA_LANGUAGE.query(f"""(if_statement)""")
#     print("If detected")
#     print(if_query)

# searchForIfStatemements()