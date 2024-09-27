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

    def composeTree(self,methodName):
        method = self.getMethod(methodName) 
        bytecodeInstructions = method[jbinary.CODE][jbinary.BYTECODE]

        #This is used because we have offset and not the index in the bytecode array
        #this allows me to not look for the index each time and increase the complexity
        fromOffsetToIndexHashMap = self.get_fromOffsetToIndexHashMap(bytecodeInstructions)
        if(len(bytecodeInstructions) == 0):
            return
        
        node = Semantic_node(bytecodeInstructions[0],fromOffsetToIndexHashMap)
        self.addToTree(node,bytecodeInstructions,fromOffsetToIndexHashMap)

    def addToTree(self,node,bytecodeInstructions,fromOffsetToIndexHashMap,invokedMethod=None):
         
        if(node is None or node.id >= len(bytecodeInstructions)):
            return

        match node.operationKind:
            case jbinary.INVOKE: 
                self.addToMethodsTree(node.methodToInvoke)
            case jbinary.IF_ZERO | jbinary.IF:
                childNodeNoJump = Semantic_node(bytecodeInstructions[node.next],fromOffsetToIndexHashMap)
                childNodeJump = Semantic_node(bytecodeInstructions[node.target],fromOffsetToIndexHashMap)
                self.addToTree(childNodeNoJump,bytecodeInstructions,fromOffsetToIndexHashMap,invokedMethod)
                self.addToTree(childNodeJump,bytecodeInstructions,fromOffsetToIndexHashMap,invokedMethod)
            case jbinary.RETURN:
                pass
            case jbinary.GOTO:
                targetNode = Semantic_node(bytecodeInstructions[node.target],fromOffsetToIndexHashMap)
                self.addToTree(targetNode,bytecodeInstructions,fromOffsetToIndexHashMap,invokedMethod)
            case _:
                nextNode = Semantic_node(bytecodeInstructions[node.next],fromOffsetToIndexHashMap)
                self.addToTree(nextNode,bytecodeInstructions,fromOffsetToIndexHashMap,invokedMethod)
        
        if(invokedMethod):
            self.__invokedMethodsSemanticTree[invokedMethod][node.id] = node
            return
        
        self.__semantic_tree[node.id] = node

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

    def addToMethodsTree(self,jsonFile,name):
        name = MethodId.parse(name)
        self.composeTree(name)

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
        

        def __init__(self,instruction,_fromOffsetToIndexHashMap):

            if not _fromOffsetToIndexHashMap.get(instruction['offset']):
               self.id = None
               
            self.id = _fromOffsetToIndexHashMap[instruction['offset']]
            self.next = self.id + 1
            if instruction.get("target"):
                self.target = instruction["target"]

            self.operationKind = instruction[jbinary.OPERATION]

            if(self.operationKind == jbinary.INVOKE):
                methodToInvoke=self.compose_method_name(instruction) 

        def compose_method_name(instruction : object):
            # Translate Java types to type descriptors
            type_descriptors = {
                "boolean": "Z", "int": "I", "void": "V", "long": "J", "double": "D",
                "float": "F", "char": "C", "short": "S", "byte": "B", "Object": "Ljava/lang/Object;"
            }
            
            # Helper function to handle array types and other complex types
            def get_descriptor(type_name):
                if type_name.startswith("["):  # If it's an array type
                    return "[" + type_descriptors.get(type_name[1:], "Ljava/lang/Object;")
                return type_descriptors.get(type_name, "Ljava/lang/Object;")  # Default to Object descriptor

            # Extract class name and convert slashes to dots (Java's fully qualified name format)
            class_name = instruction.method.ref.name.replace("/", ".")

            # Extract method name
            method_name = instruction["method"]["name"]

            # Handle method arguments (if present)
            arg_types = instruction["method"]["args"]
            arg_descriptor = "(" + "".join(get_descriptor(arg) for arg in arg_types) + ")"

            # Extract and translate return type
            return_type = instruction["method"]["returns"]
            return_descriptor = get_descriptor(return_type)

            # Compose the method signature string
            method_signature = f"{class_name}.{method_name}:{arg_descriptor}{return_descriptor}"
            
            return method_signature



        
