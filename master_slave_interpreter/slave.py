import json
import sys
# sys.path.append('../')
from utils.jbinary import jbinary
from utils.instruction_printer import Instruction_printer


class Slave:

  slave_id: int = 0

  bytecode: list = []
  instruction_pointer: int = 0
  stack: list[int] = []
  memory: list[int] = []
  json_file = {}

  error_interruption: bool = False

  analysis_results: dict = {
    'divisions_by_zero': 0,
    'unsure_divisions': 0,
    'loop': 0,
    'assertion_error': 0,
    'array_out_of_bounds': 0,
  }
  reports_from_slaves: list[dict]


  def __init__(self, file_path: str, method_name: str, reports_from_slaves: list[dict]) -> None:
    
    self.file_path = file_path
    self.method_name = method_name
    self.bytecode = self.get_method_bytecode_from_file()
    self.reports_from_slaves = reports_from_slaves


  def get_method_bytecode_from_file(self) -> list:
    
    file = open(self.file_path)
    self.json_file = json.load(file)
    file.close()
    return self.find_method_bytecode_in_json(self.json_file)
  

  def find_method_bytecode_in_json(self, json_file=None, method_name = None) -> list:

    if(method_name is None):
      method_name = self.method_name

    if(json_file is None):
      json_file = self.jsoned_file

    for whole_method_instance in json_file['methods']:

      if whole_method_instance['name'] == method_name:
        return whole_method_instance['code']['bytecode']
      
    return []


  # --------- ANALYSIS FUNCTIONS ---------


  def follow_program(self) -> None:

    while( self.instruction_pointer < len(self.bytecode) and not self.error_interruption):
      self.process_node()

  def follow_method(self,method_name):
    
    method_bytecode = self.find_method_bytecode_in_json(self.json_file,method_name)
    if(not method_bytecode):
      return 
    
    while(self.instruction_pointer < len(self.bytecode) and not self.error_interruption):
      self.process_node()
      if self.error_interruption:

        Instruction_printer.print_error(self.stack, self.instruction_pointer, self.memory)


  def process_node(self) -> None:

    current_byte = self.bytecode[ self.instruction_pointer ]
    match current_byte[jbinary.OPERATION]:

      case jbinary.PUSH:
        self.process_push(current_byte)
        Instruction_printer.print_push(current_byte, self.stack, self.instruction_pointer)
      case jbinary.LOAD:
        self.process_load()
      case jbinary.STORE:
        self.process_store()
      case jbinary.DUPPLICATION:
        self.process_dupplication()
        Instruction_printer.print_dup(self.stack, self.instruction_pointer)
      case jbinary.IF_ZERO:
        self.process_if_zero(current_byte)
        Instruction_printer.print_ifz(current_byte, self.stack[-1])
      case jbinary.GO_TO:
        self.process_goto(current_byte)
      case jbinary.GET:
        self.process_get()
        Instruction_printer.print_get(self.stack, self.instruction_pointer)
      case jbinary.INVOKE:
        self.process_invoke(current_byte)
        Instruction_printer.print_invoke(current_byte)
      case jbinary.THROW:
        self.process_throw()
        Instruction_printer.print_throw()
      case jbinary.BINARY_EXPR:
        self.process_division()
        Instruction_printer.print_division(self.stack, self.instruction_pointer)
      case jbinary.NEW:
        self.process_new()
        Instruction_printer.print_new(current_byte)
      case jbinary.RETURN:
        self.process_return()
        Instruction_printer.print_return(self.stack, self.instruction_pointer, self.memory)
        

    



  def process_push(self, current_byte) -> None:
    self.stack.append( current_byte['value']['value'])
    self.increment_instructions_pointer()


  def process_load(self) -> None:
    if(self.stack):
      self.stack.append( self.stack[-1] )
    else:
      arg = "parameter to define"
      self.stack.append(arg)

    self.increment_instructions_pointer()
  

  def process_store(self) -> None:
    if(self.stack):
      self.memory.append( self.stack[-1] )
    self.increment_instructions_pointer()


  def process_dupplication(self) -> None:

    if self.stack:
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
    self.instruction_pointer = target
  
  def process_get(self) -> None:
    # always pushes true (1) because in our case get 
    # is only used to check if assertions are enabled
    self.stack.append(1) 
  
  def process_invoke(self,invoke_instruction) -> None:
     method_prefix = invoke_instruction["method"]["ref"]["name"] + "/"
     method_to_invoke = invoke_instruction["method"]["name"]
                         

     if(method_prefix + method_to_invoke is jbinary.ASSERTION_ERROR_METHOD_SIGNATURE):
       return
     
     instruction_pointer_before_invoke = self.instruction_pointer 
     self.instruction_pointer = 0 
     self.follow_method(method_to_invoke)
     self.instruction_pointer =  instruction_pointer_before_invoke
    
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
