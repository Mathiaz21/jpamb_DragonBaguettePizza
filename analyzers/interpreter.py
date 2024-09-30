from analyzers.jbinary import jbinary
import json
from jpamb_utils import MethodId

class Interpreter:
    __jsonFile = ""
    __stack = []
    __bookmark_stack = []
    __semantic_tree = {}
    __tree_root = {}
    __invokedMethodsSemanticTree = {}


    def __init__(self, jsonFile, methodName):
        self.__jsonFile = jsonFile
        self.composeTree(methodName)
        self.__tree_root = self.__semantic_tree[0]

        for node in self.__semantic_tree:
            print(node)

    def composeTree(self,methodName,tree = None):
        method = self.getMethod(methodName) 
        bytecodeInstructions = method[jbinary.CODE][jbinary.BYTECODE]

        #This is used because we have offset and not the index in the bytecode array
        #this allows me to not look for the index each time and increase the complexity
        fromOffsetToIndexHashMap = self.get_fromOffsetToIndexHashMap(bytecodeInstructions)
        if(len(bytecodeInstructions) == 0):
            return
        
        node = Semantic_node(bytecodeInstructions[0],fromOffsetToIndexHashMap)
        if(tree is None):
            self.addToTree(node,self.__semantic_tree,bytecodeInstructions,fromOffsetToIndexHashMap)
            return

        self.addToTree(node,tree,bytecodeInstructions,fromOffsetToIndexHashMap)
        self.__invokedMethodsSemanticTree[methodName] = tree

    def addToTree(self,node,tree,bytecodeInstructions,fromOffsetToIndexHashMap,invokedMethod=None):
        
        if(node.id is None or node.id >= len(bytecodeInstructions)):
            return
        
        match node.operationKind:
            case jbinary.INVOKE:
                if(jbinary.ASSERTION_ERROR_SIGNATURE not in node.methodToInvoke):
                    if(node.methodToInvoke not in self.__invokedMethodsSemanticTree):
                        self.addToMethodsTree(node.methodToInvoke)
                    
            case jbinary.IF_ZERO | jbinary.IF:
                childNodeNoJump = Semantic_node(bytecodeInstructions[node.next],fromOffsetToIndexHashMap)
                childNodeJump = Semantic_node(bytecodeInstructions[node.target],fromOffsetToIndexHashMap)
                self.addToTree(childNodeNoJump,tree,bytecodeInstructions,fromOffsetToIndexHashMap,invokedMethod)
                self.addToTree(childNodeJump,tree,bytecodeInstructions,fromOffsetToIndexHashMap,invokedMethod)
            case jbinary.RETURN:
                pass
            case jbinary.GOTO:
                targetNode = Semantic_node(bytecodeInstructions[node.target],fromOffsetToIndexHashMap)
                self.addToTree(targetNode,tree,bytecodeInstructions,fromOffsetToIndexHashMap,invokedMethod)
            case _:
                nextNode = Semantic_node(bytecodeInstructions[node.next],fromOffsetToIndexHashMap)
                tree = self.addToTree(nextNode,tree,bytecodeInstructions,fromOffsetToIndexHashMap,invokedMethod)
        
        tree[node.id] = node

    import json

    def getMethod(self, methodName):
        with open(self.__jsonFile, 'r') as file:
            json_data = json.load(file)
        
        allMethods = json_data.get("methods", [])
        
        for method in allMethods:
            if method.get("name") == methodName:
                return method
        
        return None

    def getInvokedMethodKey(self,instruction) -> str:
        pass

    def addToMethodsTree(self,name):
        if(':' in name):
            name = MethodId.parse(name)
        
        self.composeTree(name,{})

    def get_fromOffsetToIndexHashMap(self, bytecodeInstructions):
        hashmap = {}
        for i, instruction in enumerate(bytecodeInstructions):
            hashmap[instruction["offset"]] = i
        return hashmap

    def find_target_index(self, bytecode: list, target: int) -> int:
        #TODO: build an hasmap of index and offset to access the byteinstruction array
        pass


class Semantic_node:
        id = -1
        operationKind = jbinary.GENERIC
        methodToInvoke = None
        next = None
        target = None
        
        def __str__(self):
            return (
                f"\nSemantic Node Information:\n"
                f"----------------------------\n"
                f"ID:              {self.id}\n"
                f"Operation Kind:  {self.operationKind}\n"
                f"Method:          {self.methodToInvoke}\n"
                f"Next Node:       {self.next}\n"
                f"Target:          {self.target}\n"
            )

        def __init__(self,instruction,_fromOffsetToIndexHashMap):

            if _fromOffsetToIndexHashMap.get(instruction['offset']) is None:
               self.id = None
               return
               
            self.id = _fromOffsetToIndexHashMap[instruction['offset']]
            if(self.id + 1 < len(_fromOffsetToIndexHashMap)):
                self.next = self.id + 1
            if instruction.get("target"):
                self.target = instruction["target"]

            self.operationKind = instruction[jbinary.OPERATION]

            if(self.operationKind == jbinary.INVOKE):
                self.methodToInvoke = instruction['method']['name']

        def compose_method_name(self, instruction : object):
            # Translate Java types to type descriptors
            type_descriptors = {
                "boolean": "Z", "int": "I", "void": "V", "long": "J", "double": "D",
                "float": "F", "char": "C", "short": "S", "byte": "B", "Object": "Ljava/lang/Object;"
            }
            
            # Helper function to handle array types and other complex types
            def get_descriptor(type_name):
                if(type_name is None):
                    return ""
                
                if isinstance(type_name, dict):
                    kind = type_name.get('kind')
                    base_type = type_name.get('type')
                    array_length = type_name.get('len', 0)
                    
                    # Initialize the descriptor
                    descriptor = ""
                    
                    # If it's an array, add '[' for each dimension
                    if kind == 'array':
                        descriptor += "[" * array_length
                    
                    # Recursively handle the base type (if the base type itself is another dictionary)
                    descriptor += get_descriptor(base_type)
                    return descriptor

                if type_name.startswith("["):  # If it's an array type
                    return "[" + type_descriptors.get(type_name[1:], "Ljava/lang/Object;")
                
                return type_descriptors.get(type_name, "Ljava/lang/Object;")  # Default to Object descriptor

            # Extract class name and convert slashes to dots (Java's fully qualified name format)
            method_name = instruction["method"]["ref"]["name"].replace("/", ".")

            # Handle method arguments (if present)
            arg_types = instruction["method"]["args"]
            arg_descriptor = "(" + "".join(get_descriptor(arg) for arg in arg_types) + ")"

            # Extract and translate return type
            return_type = instruction["method"]["returns"]
            return_descriptor = get_descriptor(return_type)

            # Compose the method signature string
            method_signature = f"{method_name}:{arg_descriptor}{return_descriptor}"
            
            return method_signature

        def isAssertionError(self):
            return self.methodToInvoke == jbinary.ASSERTION_ERROR_SIGNATURE


        
