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
  heap: list[ list[int] ] = []
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
      Instruction_printer.print_byte_index(self.instruction_pointer)
      self.process_node()
    self.kill_slave()

  def follow_method(self,method_name):
    
    method_bytecode = self.find_method_bytecode_in_json(self.json_file,method_name)
    if(not method_bytecode):
      return 
    
    while(self.instruction_pointer < len(self.bytecode) and not self.error_interruption):
      self.process_node()
      if self.error_interruption:

        Instruction_printer.print_error(self.stack, self.instruction_pointer, self.heap)


  def process_node(self) -> None:

    current_byte = self.bytecode[ self.instruction_pointer ]
    match current_byte[jbinary.OPERATION]:

      case jbinary.PUSH:
        self.process_push(current_byte)
        Instruction_printer.print_push(current_byte, self.stack, self.instruction_pointer)
      case jbinary.LOAD:
        self.process_load(current_byte)
        Instruction_printer.print_load(self.stack, self.instruction_pointer, current_byte)
      case jbinary.STORE:
        self.process_store(current_byte)
        Instruction_printer.print_store(self.stack, self.instruction_pointer)
      case jbinary.DUPPLICATION:
        Instruction_printer.print_dup(self.stack, self.instruction_pointer)
        self.process_dupplication()
      case jbinary.IF_ZERO:
        Instruction_printer.print_ifz(current_byte, self.stack[-1])
        self.process_if_zero(current_byte)
      case jbinary.GO_TO:
        self.process_goto(current_byte)
      case jbinary.GET:
        Instruction_printer.print_get(self.stack, self.instruction_pointer)
        self.process_get()
      case jbinary.INVOKE:
        Instruction_printer.print_invoke(current_byte)
        self.process_invoke(current_byte)
      case jbinary.THROW:
        Instruction_printer.print_throw()
        self.process_throw()
      case jbinary.BINARY_EXPR:
        Instruction_printer.print_division(self.stack, self.instruction_pointer)
        self.process_division()
      case jbinary.NEW:
        Instruction_printer.print_new(current_byte)
        self.process_new()
      case jbinary.RETURN:
        Instruction_printer.print_return(self.stack, self.instruction_pointer, self.heap)
        self.process_return()
      case jbinary.NEW_ARRAY:
        self.process_new_array()
        Instruction_printer.print_new_array(self.heap, self.instruction_pointer)
      case jbinary.ARRAY_STORE:
        Instruction_printer.print_array_store(self.heap, self.instruction_pointer, self.stack)
        self.process_array_store()
        

    



  def process_push(self, current_byte) -> None:
    self.stack.append( current_byte['value']['value'])
    self.increment_instructions_pointer()


  def process_load(self, current_byte) -> None:

    index_of_loading: int = current_byte['index']
    array_length: int = len( self.heap[index_of_loading] )
    reference_to_head: dict = {
      'type' : 'array_ref',
      'heap_index' : index_of_loading,
      'length' : array_length
    }
    self.stack.append( reference_to_head )
    self.increment_instructions_pointer()
  

  def process_store(self, current_byte) -> None:
    value_to_store: int = self.stack.pop()
    index_of_storage: int = current_byte['index']
    if index_of_storage == len(self.stack):
      self.stack.append(value_to_store)
    else:
      self.stack[index_of_storage] = value_to_store
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
      self.analysis_results['divisions_by_zero'] = 1
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


  def process_new_array(self) -> None:
    array_length: int = self.stack.pop()
    array_index_in_heap: int = self.initialize_new_array_in_heap(array_length)
    self.store_array_ref_in_stack(array_length, array_index_in_heap)
    self.increment_instructions_pointer()


  def process_array_store(self) -> None:

    value_to_store: int = self.stack.pop()
    index_of_storage_in_array: int = self.stack.pop()
    ref_of_array: dict = self.stack.pop()
    array_length: int = ref_of_array['length']
    if index_of_storage_in_array > array_length - 1:

      self.analysis_results['array_out_of_bounds'] = 1
      self.process_error()
    else:

      array_heap_index: int = ref_of_array['heap_index']
      array_in_heap: list[int] = self.heap[array_heap_index]
      array_in_heap[index_of_storage_in_array] = value_to_store
      self.increment_instructions_pointer()



  def add_to_array_in_memory(self, value: int, index: int) -> None:
    if len(self.heap) == index:
      self.heap.append(value)
    elif len(self.heap) < index:
      self.heap[index] = value
    else:
      return # error



  def increment_instructions_pointer(self) -> None:
    self.instruction_pointer += 1


  def evaluate_if_zero(self, value, comparison_type):

    match comparison_type:

      case jbinary.LARGER_OR_EQUAL:
        return value >= 0
      case jbinary.NOT_EQUAL:
        return value != 0
      
  
  def update_cursor_after_if(self, evaluation, target) -> None:

    if evaluation:
      self.increment_instructions_pointer()
    else:
      self.instruction_pointer = target


  def store_array_ref_in_stack(self, array_length, array_index_in_heap) -> None:

    array_ref: dict = {
      'type' : 'array_ref',
      'heap_index' : array_index_in_heap,
      'length' : array_length
    }
    self.stack.append(array_ref)

  
  def initialize_new_array_in_heap(self, array_length) -> int:

    array_index_in_heap: int = len(self.heap)
    new_array: list[int] = []
    for i in range(array_length):
      new_array.append(0)
    self.heap.append(new_array)

    return array_index_in_heap




  def kill_slave(self) -> None:
    self.reports_from_slaves.append(self.analysis_results)



# TODO : add the dupplication of slaves at an if statement
# TODO : add the processing of the 3 other types of error on top of division by zero
#         - Detection of infinite loops : step counter
#         - Detection of array out of bounds : registering arrays in memory
#         - Assertion error
# TODO : Complete the unsure division