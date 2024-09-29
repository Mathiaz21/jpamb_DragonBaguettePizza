from solutions.jbinary import jbinary
import json
from analyzers.semantic_node import Semantic_node

class Interpreter:

    __bytecodeInstructions = []
    __method = ""
    __stack = []
    __bookmark_stack = []
    __semantic_tree = []


    def __init__(self, jsonFile, method):
        __method = method

        __bytecodeInstructions = (json.load(jsonFile))[jbinary.CODE][jbinary.BYTECODE]

        for i,instruction in __bytecodeInstructions:
            match instruction[jbinary.OPERATION]:
                case jbinary.PUSH:
                    self.addToTree(Semantic_node(instruction), i+1)
                case jbinary.LOAD:
                    self.addToTree(Semantic_node(instruction), i+1)
                case jbinary.BINARY_EXPR:
                    self.addToTree(Semantic_node(instruction), i+1)
                case jbinary.INVOKE:
                    self.addToTree(Semantic_node(instruction), instruction.target)
                case jbinary.IF_ZERO:
                    self.addToTree(Semantic_node(instruction), i+1, instruction.target)
                case jbinary.RETURN:
                    self.addToTree(Semantic_node(instruction), -1)
        
        # TODO: Semantic_node find the best way to do it, if its only with index or with all the child. 
        # in the second case with a class we have to use recursion inside of a constructor which is not ideal.
        # IDEA 1: the init of semantic node takes only an index of the bytecode array.
        # IDEA 2: don't do it in the init but while reading the bytecode array.

        # TODO:Compose the tree, we say that the tree is gonna be like this:
        # {
        #     index:
        #     child
        #     [
        #         {
        #             index:
        #             child:[]
        #         }

        #     ]
        # }

    def addToTree(self,node,index1,index2=-1):

            if index1 < 0:
                return

            if index1 > len(self.__bytecodeInstructions):
                return
            
            node.child.append(self.__bytecodeInstructions[index1])
            if(index2 != -1):
                node.child.append(self.__bytecodeInstructions[index2])
        
    def getIndex(self,):
        #TODO         
    

