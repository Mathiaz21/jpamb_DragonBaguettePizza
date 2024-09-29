from solutions.jbinary import jbinary
import json


class Slave:

  slave_id: int = 0

  bytecode: list = []
  instruction_pointer: int = 0
  stack: list[int] = []
  memory: list[int] = []

  error_interruption: bool = False

  analysis_results: dict = {
    'divisions_by_zero': 0,
    'unsure_divisions': 0,
    'loop': 0,
    'assertion_error': 0,
    'array_out_of_bounds': 0,
  }


  def __init__(self, file_path: str, method_name: str) -> None:
    
    self.file_path = file_path
    self.method_name = method_name
    self.bytecode = self.get_method_bytecode_from_file()


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

    while( self.tree_cursor < len(self.bytecode) and not self.error_interruption):
      self.process_node()


  def process_node(self) -> None:

    current_byte = self.bytecode[ self.instruction_pointer ]
    match current_byte[jbinary.OPERATION]:

      case jbinary.PUSH:
        self.process_push(current_byte)
      case jbinary.LOAD:
        self.process_load()
      case jbinary.STORE:
        self.process_store()
      case jbinary.DUPPLICATION:
        self.process_dupplication()
      case jbinary.IF_ZERO:
        self.process_if_zero(current_byte)
      case jbinary.GO_TO:
        self.process_goto(current_byte)
      case jbinary.GET:
        self.process_get()
      case jbinary.INVOKE:
        self.process_invoke()
      case jbinary.THROW:
        self.process_throw()
      case jbinary.BINARY_EXPR:
        self.process_division()
      case jbinary.NEW:
        self.process_new()
      case jbinary.RETURN:
        self.process_return()
        

    



  def process_push(self, current_byte) -> None:
    self.stack.append( current_byte['value']['value'])
    self.increment_instructions_pointer()


  def process_load(self) -> None:
    self.stack.append( self.stack[-1] )
    self.increment_instructions_pointer()
  

  def process_store(self) -> None:
    self.memory.append( self.stack[-1] )
    self.increment_instructions_pointer()


  def process_dupplication(self) -> None:

    if len( self.stack ) != 0:
      self.stack.append( self.stack[-1] )
    self.increment_instructions_pointer()


  def process_if_zero(self, current_byte) -> None:
    
    value: int = self.stack[-1]
    target: int = current_byte[jbinary.TARGET]
    comparison_type: str = current_byte[jbinary.CONDITION]
    evaluation: bool = self.evaluate_if_zero(value, comparison_type)
    self.update_cursor_after_if(evaluation, target)
    
  

  def process_goto(self, current_byte) -> None:
    target: int = current_byte[jbinary.TARGET]
    self.tree_cursor = target
  
  def process_get(self) -> None:
    # always pushes true (1) because in our case get 
    # is only used to check if assertions are enabled
    self.stack.append(1) 
  
  def process_invoke(self) -> None:
    self.increment_instructions_pointer()
  
  def process_throw(self) -> None:
    self.increment_instructions_pointer()
  
  def process_division(self) -> None:
    if self.stack[-1] == 0:
      self.stack.append( 'div_by_zero' )
      self.process_error()
    else:
      self.stack.append( self.stack[-2] / self.stack[-1] )
    self.increment_instructions_pointer()

  def process_new(self) -> None:
    self.increment_instructions_pointer()
  
  def process_return(self) -> None:
    self.increment_instructions_pointer()

  def process_error(self) -> None:
    self.error_interruption = True


  def increment_instructions_pointer(self) -> None:
    self.instruction_pointer += 1

  def evaluate_if_zero(self, value, comparison_type):

    match comparison_type:

      case jbinary.LARGER_OR_EQUAL:
        return value >= 0
      case jbinary.NOT_EQUAL:
        return value != 0
      
  
  def update_cursor_after_if(self, evaluation, target):

    if evaluation:
      self.increment_instructions_pointer()
    else:
      self.instruction_pointer = target
