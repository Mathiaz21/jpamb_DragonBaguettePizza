from solutions.jbinary import jbinary

def getDivisionByZeroProbability(m):
    simulated_stack = []
    probability = 1;
    for instruction in m[jbinary.CODE][jbinary.BYTECODE]:
        treat_instruction(instruction, simulated_stack,probability)
    return probability

def treat_instruction(instruction, simulated_stack,probability):
    match instruction[jbinary.OPERATION]:
        case jbinary.PUSH:
            treat_push(instruction, simulated_stack)
        case jbinary.LOAD:
            treat_load(instruction, simulated_stack)
        case jbinary.BINARY_EXPR:
            treat_binary_operator(instruction, simulated_stack,probability)
        # case jbinary.INVOKE:
        #     treat_invoke_operator(instruction, simulated_stack)

def treat_push(instruction, simulated_stack):
    simulated_stack.append(instruction["value"])    

def treat_load(instruction, simulated_stack):
    simulated_stack.append(instruction["type"])

def treat_binary_operator(instruction, simulated_stack,probability):
    if instruction["operant"] == jbinary.DIVISION:
            return calculateProbability(simulated_stack,probability)

def calculateProbability(simulated_stack,probability):
    if 'value' in simulated_stack[-1]:
        if simulated_stack[-1]["value"] == 0:
            probability = probability * 1
    else:
        
        probability = (1 + 3*probability) / 4

