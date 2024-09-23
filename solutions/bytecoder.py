#!/usr/bin/env python3
""" A very stupid syntatic bytecode analysis, that only checks for assertion errors.
"""

import sys, logging
from jbinary import jbinary
from jpamb_utils import MethodId

l = logging
l.basicConfig(level=logging.DEBUG)

(name,) = sys.argv[1:]

l.debug("check assertion")
l.debug("read the method name")
method = MethodId.parse(name)

l.debug("looking up method")
m = method.load()

l.debug("trying to find an assertion error being created")
for inst in m["code"]["bytecode"]:
    if (
        inst["opr"] == "invoke"
        and inst["method"]["ref"]["name"] == "java/lang/AssertionError"
    ):
        break
else:
    # I'm pretty sure the answer is no
    l.debug("did not find it")
    print("assertion error;20%")
    sys.exit(0)

l.debug("Found it")
# I'm kind of sure the answer is yes.
print("assertion error;80%")
##########################################################

######### ANALYSIS OF THE METHOD INSTR BY INSTR ##########

##########################################################



# TODO  : write a function that detects divisions by zero and by n
# Using the simulated_stack

probabilities = {
    "div_by_zero": 0,
    "assertion_error": 0,
    "array_out_of_bounds": 0,
    "infinite_loop": 0,
    "ok_non_error": 0
}


def print_probabilities(probabilities):

    print(f"divide by 0;{probabilities['div_by_zero'] * 100}%")
    print(f"assertion error;{probabilities['assertion_error'] * 100}%")
    print(f"array out of bounds;{probabilities['array_out_of_bounds'] * 100}%")
    print(f"*;{probabilities['infinite_loop'] * 100}%")
    print(f"ok;{probabilities['ok_non_error'] * 100}%")


def evaluate_probabilities(probabilities):

    simulated_stack = []
    for instruction in m[jbinary.CODE][jbinary.BYTECODE]:

        treat_instruction(instruction, simulated_stack)
                    
def treat_instruction(instruction, simulated_stack):
    match instruction[jbinary.OPERATION]:
        case jbinary.PUSH:
            treat_push(instruction, simulated_stack)
        case jbinary.LOAD:
            treat_load(instruction, simulated_stack)
        case jbinary.BINARY_EXPR:
            treat_binary_operator(instruction, simulated_stack)
        case jbinary.INVOKE:
            treat_invoke_operator(instruction, simulated_stack)

def treat_push(instruction, simulated_stack):

    simulated_stack.append(instruction["value"])    



def treat_load(instruction, simulated_stack):

    simulated_stack.append(instruction["type"])

    

def treat_binary_operator(instruction, simulated_stack):

    if instruction["operant"] == "div":

            treat_division(instruction, simulated_stack)





def treat_invoke_operator(instruction, simulated_stack):

    if instruction["method"]["ref"]["name"] == jbinary.ASSERTION_ERROR:

        treat_assertion(instruction, simulated_stack)


def treat_division(instruction, simulated_stack):

    if 'value' in simulated_stack[-1]:
        
        if simulated_stack[-1]["value"] == 0:

            probabilities["div_by_zero"] = 1
    else:

        probabilities["div_by_zero"] = (1 + 3*probabilities["div_by_zero"]) / 4



def treat_assertion(instruction, simulated_stack):
    l.debug("Found an assertion call")



##########################################################

################## CALLING THE FUNCTION ##################

##########################################################

evaluate_probabilities(probabilities)
print_probabilities(probabilities)




# l.debug("trying to find an assertion error being created")
# # Look if the method contains an assertion error:
# for inst in m["code"]["bytecode"]:

#     if (

#         inst["opr"] == "invoke"
#         and inst["method"]["ref"]["name"] == "java/lang/AssertionError"
#     ):


        
#     else:

#         l.debug("Did not find an assertion error")
#         print("assertion error;20%")
#         sys.exit(0)


