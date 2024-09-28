from semantic_node import Semantic_node
from solutions.jbinary import jbinary
from instruction_printer import Instruction_printer

import json


class Mathias_interpreter:

  file_path: str = ''
  method_name: str = ''
  bytecode: list = []
  semantic_tree: list[Semantic_node] = []
  stack: list[int] = []
  memory: list[int] = []
  tree_cursor: int = 0
  step_count: int = 0


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


  # --------- ANALYSIS FUNCTIONS ---------


  def follow_program(self) -> None:

    while( self.tree_cursor < len(self.bytecode)):

      self.step_count += 1
      self.process_node()


  

  def process_node(self) -> None:

    Instruction_printer.print_step_title(self.step_count)
    current_index: int = self.semantic_tree[self.tree_cursor].index
    current_byte = self.bytecode[ current_index ]
    initial_cursor: int = self.tree_cursor
    match current_byte[jbinary.OPERATION]:

      case jbinary.PUSH:
        self.process_push(current_byte)
        Instruction_printer.print_push(current_byte, self.stack, self.step_count)
      case jbinary.LOAD:
        self.process_load()
      case jbinary.STORE:
        self.process_store()
      case jbinary.DUPPLICATION:
        self.process_dupplication()
        Instruction_printer.print_dup(self.stack, self.step_count)
      case jbinary.IF_ZERO:
        self.process_if_zero(current_byte)
        Instruction_printer.print_ifz(current_byte, self.stack[-1])
      case jbinary.GO_TO:
        self.process_goto(current_byte)
      case jbinary.GET:
        self.process_get()
        Instruction_printer.print_get(self.stack, self.step_count)
      case jbinary.INVOKE:
        self.process_invoke()
        Instruction_printer.print_invoke(current_byte)
      case jbinary.THROW:
        self.process_throw()
        Instruction_printer.print_throw()
      case jbinary.BINARY_EXPR:
        self.process_division()
        Instruction_printer.print_division(self.stack, self.step_count)
      case jbinary.NEW:
        self.process_new()
        Instruction_printer.print_new(current_byte)
      case jbinary.RETURN:
        self.process_return()
        Instruction_printer.print_return(self.stack, self.step_count, self.memory)
        

    



  def process_push(self, current_byte) -> None:
    self.stack.append( current_byte['value']['value'])
    self.increment_tree_cursor()


  def process_load(self) -> None:
    self.stack.append( self.stack[-1] )
    self.increment_tree_cursor()
  

  def process_store(self) -> None:
    self.memory.append( self.stack[-1] )
    self.increment_tree_cursor()


  def process_dupplication(self) -> None:

    if len( self.stack ) != 0:
      self.stack.append( self.stack[-1] )
    self.increment_tree_cursor()


  def process_if_zero(self, current_byte) -> None:
    
    value: int = self.stack[-1]
    target: int = current_byte[jbinary.TARGET]
    comparison_type: str = current_byte[jbinary.CONDITION]
    evaluation: bool = self.evaluate_if_zero(value, comparison_type)
    self.update_cursor_after_if(evaluation, target)
    
  

  def process_goto(self, current_byte) -> None:
    target: int = current_byte[jbinary.TARGET]
    Instruction_printer.print_goto(target)
    self.tree_cursor = target
  
  def process_get(self) -> None:
    # always pushes true (1) because in our case get 
    # is only used to check if assertions are enabled
    self.stack.append(1) 
  
  def process_invoke(self) -> None:
    self.increment_tree_cursor()
  
  def process_throw(self) -> None:
    self.increment_tree_cursor()
  
  def process_division(self) -> None:
    if self.stack[-1] == 0:
      self.stack.append( 666 )
    else:
      self.stack.append( self.stack[-2] / self.stack[-1] )
    self.increment_tree_cursor()

  def process_new(self) -> None:
    self.increment_tree_cursor()
  
  def process_return(self) -> None:
    self.increment_tree_cursor()


  def increment_tree_cursor(self) -> None:
    self.tree_cursor += 1

  def evaluate_if_zero(self, value, comparison_type):

    match comparison_type:

      case jbinary.LARGER_OR_EQUAL:
        return value >= 0
      case jbinary.NOT_EQUAL:
        return value != 0
      
  
  def update_cursor_after_if(self, evaluation, target):

    if evaluation:
      self.increment_tree_cursor()
    else:
      self.tree_cursor = target
