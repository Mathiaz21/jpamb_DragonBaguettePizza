import json
import logging

l = logging

class Semantic_node:

  index:int
  children: list[int]

  def __init__(self, index:int, bytecode):

    self.index = index
    self.children = self.get_children_indices(self.index, bytecode)


  def print_node(self) -> None:

    print('Node : ')
    print('Index : ', self.index)
    print('Children : ')
    for child in self.children:
      print('   ', child)

  
  def get_children_indices(self, current_index: int, bytecode):

    children: list[int] = []
    match bytecode[current_index]['opr']:

      case 'ifz':
        children = self.get_if_instruction_children(current_index, bytecode)
      case _ : children = [current_index + 1]
      
    return children



  def get_if_instruction_children(self, current_index, bytecode) -> list[int]:
  
    children: list[int] = [current_index + 1]
    target : int = bytecode[current_index]['target']
    children.append( self.find_target_index(self, bytecode, target))
    return children



  def find_target_index(self, bytecode: list, target: int) -> int:

    for i in range(len(bytecode)):
      
      byte_instruction = bytecode[i]
      if byte_instruction['offset'] == target:
        return i
    
    return




class Mathias_interpreter:

  bytecode:list
  semantic_tree:list[Semantic_node]
  file_path: str 
  method_name: str


  def __init__(self, file_path: str, method_name: str) -> None:
    
    self.file_path = file_path
    self.method_name = method_name
    self.bytecode = self.get_method_bytecode_from_file()
    self.semantic_tree = self.build_tree()



  def build_tree(self) -> list[Semantic_node]:

    semantic_tree: list[Semantic_node] = []
    for current_index in range(len(self.bytecode)):
      
      new_node = Semantic_node(current_index, self.bytecode)
      semantic_tree.append(new_node)

    return semantic_tree
  

  def print_tree_nodes(self) -> None:

    print('Seamantic Tree : ')
    for node in self.semantic_tree:
      node.print_node()


  def get_method_bytecode_from_file(self) -> list:
    
    file = open(self.file_path)
    file_to_json = json.load(file)
    file.close()
    return self.find_method_bytecode_in_json(file_to_json)
  


  def find_method_bytecode_in_json(self, jsoned_file) -> list:

    for whole_method_instance in jsoned_file['methods']:

      if whole_method_instance['name'] == self.method_name:
        return whole_method_instance['code']['bytecode']
      
    return




main_file_path: str = '../decompiled/jpamb/cases/Simple.json'
main_method_name: str = 'divideByZero'

main_interpreter: Mathias_interpreter = Mathias_interpreter(main_file_path, main_method_name)

main_interpreter.print_tree_nodes()