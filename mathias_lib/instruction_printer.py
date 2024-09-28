from stack_printer import Stack_printer
from solutions.jbinary import jbinary

class Instruction_printer:


  def print_step_title(step_count) -> None:

    step_title: str = '─'*15 + f' STEP N° {step_count} ' + '─'*15
    print('')
    print('')
    print(step_title)
    print('')


  def print_push(instruction_byte, stack, step_count) -> None:

    pushed_value: int = instruction_byte['value']['value']
    push_report: str = f'Push value {pushed_value} on the stack'
    print(push_report)
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
    Instruction_printer.show_memory(memory, step_count)

  
  def print_ifz(instruction_byte, stack_top: int) -> None:

    match instruction_byte[jbinary.CONDITION]:

      case jbinary.LARGER_OR_EQUAL:
        comparison_symbol: str = '>='
      case jbinary.NOT_EQUAL:
        comparison_symbol: str = '!='
    ifz_report: str = f'Ifz comparison : {stack_top} {comparison_symbol} 0'
    print(ifz_report)


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

    division_report: str = f' Division : {stack[-3]} / {stack[-2]}'
    print(division_report)
    Instruction_printer.show_stack(stack, step_count)


  def print_goto(target: int):

    goto_report: str = f'Going to instruction {target}'
    print(goto_report)



  def show_stack(stack, step_count) -> None:

    print('')
    stack_label: str = f'Stack at step n° {step_count}'
    Stack_printer.print_stack(stack, stack_label)

  
  def show_memory(memory: list[int], step_count: int) -> None:
    
    print('')
    stack_label: str = f'Memory at step n° {step_count}'
    Stack_printer.print_stack(memory, stack_label)

  