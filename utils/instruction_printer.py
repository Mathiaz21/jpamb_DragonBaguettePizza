from utils.stack_printer import Stack_printer
from utils.heap_printer import Heap_printer
from utils.jbinary import jbinary

class Instruction_printer:

  def print_new_slave(slave_id: int) :

    print('')
    print('╭─────────────────────────────────╮')
    print(f'│          NEW SLAVE, N°{slave_id}         │')
    print('╰─────────────────────────────────╯')


  def print_byte_index(step_count) -> None:

    step_title: str = '─'*15 + f' BYTE INDEX {step_count} ' + '─'*15
    print('')
    print('')
    print(step_title)
    print('')


  def print_push(instruction_byte, stack, step_count) -> None:

    if instruction_byte['value'] != None:
      pushed_value: int = instruction_byte['value']['value']
    else:
      pushed_value: None = None
    push_report: str = f'Push value {pushed_value} on the stack'
    print(push_report)
    Instruction_printer.show_stack(stack, step_count)
    


  def print_store(stack: list[int], step_count: int) -> None:

    stored_value: int = stack[-1]
    store_report: str = f'Store value {stored_value} on the stack'
    print(store_report)
    Instruction_printer.show_stack(stack, step_count)
  

  def print_load(stack: list[int], step_count: int, current_byte) -> None:

    index_of_load: int = current_byte['index']
    load_report: str = f'Load on stack from stack index {index_of_load}'
    print(load_report) 
    Instruction_printer.show_stack(stack, step_count)


  def print_get(stack, step_count) -> None:

    get_report: str = f'Get value True (1) on the stack'
    print(get_report)
    Instruction_printer.show_stack(stack, step_count)

  
  def print_dup(stack, step_count):

    dup_report: str = f'Dupplicated value {stack[-1]} on the stack'
    print(dup_report)
    Instruction_printer.show_stack(stack, step_count)


  def print_return(stack: list[int], step_count: int, memory: list[int]) -> None:

    return_report: str = f'Program terminated after {step_count} steps'
    print(return_report)
    Instruction_printer.show_stack(stack, step_count)
    Instruction_printer.show_heap(memory)


  def print_error(stack: list[int], step_count: int, memory: list[int]) -> None:

    error_report: str = f'Program interrupted by error after {step_count} steps'
    print(error_report)
    Instruction_printer.show_stack(stack, step_count)
    Instruction_printer.show_heap(memory)

  
  def print_ifz(instruction_byte) -> None:

    comparison_symbol: str
    match instruction_byte[jbinary.CONDITION]:

      case jbinary.LARGER_OR_EQUAL:
        comparison_symbol= '>='
      case jbinary.NOT_EQUAL:
        comparison_symbol = '!='
      case jbinary.GREATER_THAN:
        comparison_symbol = '>'
      case _ :
        comparison_symbol = '!! Unknown comparison symbol !!'
    ifz_report: str = f'''Ifz comparison : stack[-1] {comparison_symbol} 0
      Else target : {instruction_byte[jbinary.TARGET]}'''
    print(ifz_report)


  def print_if(instruction_byte) -> None:

    comparison_symbol: str
    match instruction_byte[jbinary.CONDITION]:

      case jbinary.GREATER_OR_EQUAL:
        comparison_symbol = '>='
    if_report: str = f'''If comparison : stack[-1] {comparison_symbol} stack[-2]
      Else target : {instruction_byte[jbinary.TARGET]}'''
    print(if_report)




  def print_new(instruction_byte):

    new_object_report: str = f'New object : {instruction_byte["class"]}'
    print(new_object_report)

  
  def print_invoke(instruction_byte) -> None:

    invoke_report: str = f'Invoke : {instruction_byte["method"]["ref"]["name"]}'
    print(invoke_report)

  
  def print_throw() -> None:

    throw_report: str = f'Throw called'
    print(throw_report)


  def print_division(stack: list[int], step_count: int) -> None:

    division_report: str = f' Division : stack[-2] / stack[-1]'
    print(division_report)
    Instruction_printer.show_stack(stack, step_count)


  def print_goto(current_byte):

    target: int = current_byte['target']
    goto_report: str = f'Going to instruction {target}'
    print(goto_report)

  
  def print_new_array(memory: list[int], step_count: int) -> None:

    new_array_report: str = f'Initializing a new array'
    print(new_array_report)
    Instruction_printer.show_heap(memory)


  def print_array_store(heap: list[int], step_count: int):

    array_store_report: str = f'Storing stack[-1] in array at index stack[-1]'
    print(array_store_report)
    Instruction_printer.show_heap(heap)


  def print_array_length(stack: list[int], step_count) -> None:

    array_length_report: str = 'Getting the length of the array referenced at the top of the stack, then pushing it onto the stack'
    print(array_length_report)
    Instruction_printer.show_stack(stack, step_count)


  def print_increment(current_byte, stack: list[int], step_count: int) -> None:

    amount_to_increment: int = current_byte['amount']
    index_on_stack: int = current_byte['index']
    increment_report: str = f'Incrementing stack[{index_on_stack}] of {amount_to_increment}'
    print(increment_report)
    Instruction_printer.show_stack(stack, step_count)


  def show_stack(stack, step_count) -> None:

    print('')
    stack_label: str = f'Stack at step n° {step_count}'
    Stack_printer.print_stack(stack, stack_label)

  
  def show_heap(heap: list[ list[int] ]) -> None:
    
    print('')
    Heap_printer.print_heap(heap)
