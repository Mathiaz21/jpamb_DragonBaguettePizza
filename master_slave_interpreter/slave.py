import json
from utils.jbinary import jbinary
from utils.jpamb_criteria import jpamb_criteria
from utils.instruction_printer import Instruction_printer


class Slave:

  slave_id: int = 0

  __bytecode: list = []
  __instruction_pointer: int = 0
  __step_counter: int = 0
  __MAX_STEPS: int = 1000
  __stack: list[int] = []
  __heap: list[ list[int] ] = []
  __json_file = {}

  __error_interruption: bool = False

  analysis_results: dict[str, float] = None
  __reports_from_slaves: list[dict] = None

  __should_print_process: bool = False


  def __init__(self, file_path: str, method_name: str, reports_from_slaves: list[dict],params = [],start_index = 0, stack=None, should_print_process: bool = False):
    
    self.file_path = file_path
    self.method_name = method_name
    self.__bytecode = self.get_method_bytecode_from_file()
    self.__reports_from_slaves = reports_from_slaves
    self.__instruction_pointer = start_index
    self.__should_print_process = should_print_process

    self.analysis_results: dict[str, float] = {
      jpamb_criteria.DIVIDE_BY_ZERO: False,
      jpamb_criteria.INFINITE_LOOP: False,
      jpamb_criteria.ASSERTION_ERROR: False,
      jpamb_criteria.ARRAY_OUT_OF_BOUNDS: False,
      jpamb_criteria.NULL_POINTER: False,
    }

    #This if avoid sharing list among different instance of the class. Python is shit
    if stack is None:
      self.__stack = []
    else:
      self.__stack = stack

    for param in reversed(params):
      self.__stack.append(param)


  def run(self):
    if self.__should_print_process:
      Instruction_printer.print_new_slave(self.slave_id)
    self.follow_program()
    return



  def get_method_bytecode_from_file(self) -> list:
    
    file = open(self.file_path)
    self.__json_file = json.load(file)
    file.close()
    return self.find_method_bytecode_in_json(self.__json_file)
  

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

    while( self.__instruction_pointer < len(self.__bytecode) and not self.__error_interruption):
      self.__step_counter += 1
      self.process_node()
      if self.__step_counter > self.__MAX_STEPS:

        self.analysis_results[jpamb_criteria.INFINITE_LOOP] = 1.
        self.process_error()
    self.kill_slave()

  def follow_method(self,method_name) -> None:
    
    method_bytecode = self.find_method_bytecode_in_json(self.__json_file,method_name)
    if(not method_bytecode):
      return 
    
    while(self.__instruction_pointer < len(self.__bytecode) and not self.__error_interruption):
      self.__step_counter += 1
      self.process_node()
      if self.__step_counter > self.__MAX_STEPS:

        self.analysis_results[jpamb_criteria.INFINITE_LOOP] = 1.
        self.process_error()
      if self.__error_interruption:

        Instruction_printer.print_error(self.__stack, self.__instruction_pointer, self.__heap)


  def process_node(self, stack_offset=0) -> None:

    if self.__should_print_process:
      Instruction_printer.print_byte_index(self.__instruction_pointer)
    current_byte = self.__bytecode[ self.__instruction_pointer ]
    match current_byte[jbinary.OPERATION]:

      case jbinary.PUSH:
        self.process_push(current_byte)
      case jbinary.LOAD:
        self.process_load(current_byte,stack_offset)
      case jbinary.STORE:
        self.process_store(current_byte,stack_offset)
      case jbinary.DUPPLICATION:
        self.process_dupplication()
      case jbinary.IF_ZERO:
        self.process_if_zero(current_byte)
      case jbinary.IF:
        self.process_if(current_byte)
      case jbinary.GO_TO:
        self.process_goto(current_byte)
      case jbinary.GET:
        self.process_get()
      case jbinary.INVOKE:
        self.process_invoke(current_byte)
      case jbinary.THROW:
        self.process_throw()
      case jbinary.BINARY_EXPR:
        self.process_division()
      case jbinary.NEW:
        self.process_new()
      case jbinary.RETURN:
        self.process_return()
      case jbinary.NEW_ARRAY:
        self.process_new_array()
      case jbinary.ARRAY_STORE:
        self.process_array_store()
      case jbinary.ARRAY_LENGTH:
        self.process_array_length()
      case jbinary.INCREMENT:
        self.process_increment(current_byte)
      # case _ :
      #   self.increment_instructions_pointer()

    if self.__should_print_process:
      self.print_the_instruction(current_byte)



  def process_push(self, current_byte) -> None:
    if current_byte['value'] != None:
      self.__stack.append( current_byte['value']['value'])
    else:
      self.__stack.append( None )
    self.increment_instructions_pointer()


  def process_load(self, current_byte,stack_offset=0) -> None:
    stack_index_to_load = current_byte['index']
    i = stack_index_to_load + stack_offset
    if i < len(self.__stack):
      self.__stack.append(self.__stack[i])
    self.increment_instructions_pointer()


  def process_store(self, current_byte,stack_offset) -> None:
    value_to_store: int = self.__stack.pop()
    index_of_storage: int = current_byte['index']
    if index_of_storage == len(self.__stack): #to store at the same position it were
      self.__stack.append(value_to_store)
    else:
      self.__stack[index_of_storage + stack_offset] = value_to_store
    self.increment_instructions_pointer()


  def process_dupplication(self) -> None:

    if self.__stack:
      self.__stack.append( self.__stack[-1] )
    self.increment_instructions_pointer()


  def process_if_zero(self, current_byte) -> None:
    
    value: int = self.__stack.pop()
    target: int = current_byte[jbinary.TARGET]
    comparison_type: str = current_byte[jbinary.CONDITION]

    evaluation: bool = self.evaluate_if_zero(value, comparison_type)
    self.update_cursor_after_if(evaluation, target)
    
  

  def process_if(self, current_byte) -> None:

    left_int: int = self.__stack.pop()
    right_int: int = self.__stack.pop()
    target: int = current_byte[jbinary.TARGET]
    comparison_type = current_byte[jbinary.CONDITION]

    evaluation: bool = self.evaluate_if(left_int, right_int, comparison_type)
    self.update_cursor_after_if(evaluation, target)
  


  def process_goto(self, current_byte) -> None:
    target: int = current_byte[jbinary.TARGET]
    self.__instruction_pointer = target
  
  def process_get(self) -> None:
    self.__stack.append(1)
    self.increment_instructions_pointer() 
  
  def process_invoke(self,invoke_instruction) -> None:
     method_prefix = invoke_instruction["method"]["ref"]["name"] + "/"
     method_to_invoke = invoke_instruction["method"]["name"]
                         
     if(method_prefix + method_to_invoke in jbinary.ASSERTION_ERROR_METHOD_SIGNATURE):
       self.__error_interruption = True
       self.analysis_results[jpamb_criteria.ASSERTION_ERROR] = True
       return
     
     instruction_pointer_before_invoke = self.__instruction_pointer 
     self.__instruction_pointer = 0 
     self.follow_method(method_to_invoke)
     self.__instruction_pointer =  instruction_pointer_before_invoke
    
     self.increment_instructions_pointer()
  

  def process_throw(self) -> None:
    self.increment_instructions_pointer()
  

  def process_division(self) -> None:

    divisor: int = self.__stack.pop()
    dividend: int = self.__stack.pop()
    if divisor == 0:
      self.analysis_results[jpamb_criteria.DIVIDE_BY_ZERO] = True
      self.process_error()
    else:
      self.__stack.append( dividend // divisor )
    self.increment_instructions_pointer()


  def process_new(self) -> None:
    self.increment_instructions_pointer()
  

  def process_return(self) -> None:
    self.increment_instructions_pointer()


  def process_error(self) -> None:
    self.__error_interruption = True


  def process_new_array(self) -> None:
    array_length: int = self.__stack.pop()
    array_index_in_heap: int = self.initialize_new_array_in_heap(array_length)
    self.store_array_ref_in_stack(array_length, array_index_in_heap)
    self.increment_instructions_pointer()


  def process_array_store(self) -> None:

    value_to_store: int = self.__stack.pop()
    index_of_storage_in_array: int = self.__stack.pop()
    ref_of_array: dict = self.__stack.pop()
    if ref_of_array == None:

      self.analysis_results[jpamb_criteria.NULL_POINTER] = 1.
      self.process_error()
      return
    array_length: int = ref_of_array['length']
    if index_of_storage_in_array > array_length - 1:

      self.analysis_results[jpamb_criteria.ARRAY_OUT_OF_BOUNDS] = 1.
      self.process_error()
    else:

      array_heap_index: int = ref_of_array['heap_index']
      array_in_heap: list[int] = self.__heap[array_heap_index]
      array_in_heap[index_of_storage_in_array] = value_to_store
      self.increment_instructions_pointer()

  def process_array_length(self) -> None:

    array_reference: dict = self.__stack.pop()
    if array_reference == None:
      self.analysis_results[jpamb_criteria.NULL_POINTER] = 1.
      self.process_error()
    else:
      self.__stack.append(array_reference['length'])
      self.increment_instructions_pointer()


  def process_increment(self, current_byte) -> None:

    amount_to_increment: int = current_byte['amount']
    stack_index_of_number: int = current_byte['index']
    self.__stack[stack_index_of_number] += amount_to_increment
    self.increment_instructions_pointer()


  def add_to_array_in_memory(self, value: int, index: int) -> None:
    if len(self.__heap) == index:
      self.__heap.append(value)
    elif len(self.__heap) < index:
      self.__heap[index] = value
    else:
      return # error



  def increment_instructions_pointer(self) -> None:
    self.__instruction_pointer += 1


  def evaluate_if_zero(self, value: int, comparison_type) -> bool:

    match comparison_type:

      case jbinary.LARGER_OR_EQUAL:
        return value >= 0
      case jbinary.NOT_EQUAL:
        return value != 0
      case jbinary.GREATER_THAN:
        return value > 0
      # TODO : complete potential cases



  def evaluate_if(self, left_int: int, right_int: int, comparison_type) -> bool:

    match comparison_type:

      case jbinary.GREATER_OR_EQUAL:
        return left_int >= right_int
      # TODO : complete potential cases


  
  def update_cursor_after_if(self, evaluation, target) -> None:

    if evaluation:
      self.increment_instructions_pointer()
    else:
      self.__instruction_pointer = target


  def store_array_ref_in_stack(self, array_length, array_index_in_heap) -> None:

    array_ref: dict = {
      'type' : 'array_ref',
      'heap_index' : array_index_in_heap,
      'length' : array_length
    }
    self.__stack.append(array_ref)

  
  def initialize_new_array_in_heap(self, array_length) -> int:

    array_index_in_heap: int = len(self.__heap)
    new_array: list[int] = []
    for i in range(array_length):
      new_array.append(0)
    self.__heap.append(new_array)

    return array_index_in_heap




  def kill_slave(self) -> None:
    if not self.__error_interruption:
      self.analysis_results["ok"] = 1
    self.__reports_from_slaves.append(self.analysis_results)



  def print_the_instruction(self, current_byte):

    match current_byte[jbinary.OPERATION]:

      case jbinary.PUSH:
        Instruction_printer.print_push(current_byte, self.__stack, self.__instruction_pointer)
      case jbinary.LOAD:
        Instruction_printer.print_load(self.__stack, self.__instruction_pointer, current_byte)
      case jbinary.STORE:
        Instruction_printer.print_store(self.__stack, self.__instruction_pointer)
      case jbinary.DUPPLICATION:
        Instruction_printer.print_dup(self.__stack, self.__instruction_pointer)
      case jbinary.IF_ZERO:
        Instruction_printer.print_ifz(current_byte)
      case jbinary.IF:
        Instruction_printer.print_if(current_byte)
      case jbinary.GO_TO:
        Instruction_printer.print_goto(current_byte)
      case jbinary.GET:
        Instruction_printer.print_get(self.__stack, self.__instruction_pointer)
      case jbinary.INVOKE:
        Instruction_printer.print_invoke(current_byte)
      case jbinary.THROW:
        Instruction_printer.print_throw()
      case jbinary.BINARY_EXPR:
        Instruction_printer.print_division(self.__stack, self.__instruction_pointer)
      case jbinary.NEW:
        Instruction_printer.print_new(current_byte)
      case jbinary.RETURN:
        Instruction_printer.print_return(self.__stack, self.__instruction_pointer, self.__heap)
      case jbinary.NEW_ARRAY:
        Instruction_printer.print_new_array(self.__heap, self.__instruction_pointer)
      case jbinary.ARRAY_STORE:
        Instruction_printer.print_array_store(self.__heap, self.__instruction_pointer)
      case jbinary.ARRAY_LENGTH:
        Instruction_printer.print_array_length(self.__stack, self.__instruction_pointer)
      case jbinary.INCREMENT:
        Instruction_printer.print_increment(current_byte, self.__stack, self.__instruction_pointer)




# TODO : add the processing of the 3 other types of error on top of division by zero
#         - Detection of infinite loops : step counter
#         - Assertion error