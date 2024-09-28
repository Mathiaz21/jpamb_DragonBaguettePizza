class Pretty_printer:

  def print_stack(array_stack: list[int], stack_name: str = 'UNDEFINED_NAME', stack_width: int = 20) -> None:

    stack_width = Pretty_printer.adjust_stack_width(stack_name, stack_width)
    Pretty_printer.print_stack_top_and_title(stack_name, stack_width)
    stack_length: int = len(array_stack)
    
    if stack_length == 1:

      Pretty_printer.print_only_stack_cell(array_stack[0], stack_width)
    else: 

      Pretty_printer.print_stack_top_cell(array_stack[-1], stack_width)
      for i in range(stack_length - 2, 0, -1):

        cell_value: int = array_stack[i]
        Pretty_printer.print_stack_middle_cell(cell_value)
      Pretty_printer.print_stack_bottom_cell(array_stack[0], stack_width)
    Pretty_printer.print_stack_bottom(stack_width)


  def adjust_stack_width(stack_name: str, stack_width: str) -> int:
    return max(stack_width, len(stack_name)+2)
  

  def print_stack_top_and_title(stack_name: str, stack_width: int) -> None:

    stack_name_length: int = len(stack_name)
    length_before: str = (stack_width - stack_name_length) // 2
    length_after: str = length_before + (stack_width - stack_name_length) % 2
    stack_top_and_title: str = '╭' + '─'*length_before + ' ' + stack_name + ' ' + '─'*length_after + '╮'
    empty_layer: str = '│' + ' '*(stack_width+2) + '│'

    print(stack_top_and_title)
    print(empty_layer)

  
  def print_stack_bottom(stack_width: int) -> None:

    bottom_line:str = '╰' + '─'*(stack_width+2) + '╯'
    print(bottom_line)

  def print_only_stack_cell(single_value: int, stack_width: int) -> None:

    stack_cell_top_line:str = '│╭' + '─'*stack_width + '╮│'
    stack_cell_underline:str = '│╰' + '─'*stack_width + '╯│'
    print(stack_cell_top_line)
    Pretty_printer.print_stack_cell_center(single_value, stack_width)
    print(stack_cell_underline)


  def print_stack_top_cell(top_value: int, stack_width: int) -> None:

    stack_cell_top_line:str = '│╭' + '─'*stack_width + '╮│'
    stack_cell_underline:str = '│├' + '─'*stack_width + '┤│'
    print(stack_cell_top_line)
    Pretty_printer.print_stack_cell_center(top_value, stack_width)
    print(stack_cell_underline)


  def print_stack_middle_cell(cell_value:int, stack_width: int) -> None:

    Pretty_printer.print_stack_cell_center(cell_value)
    stack_cell_underline:str = '│├' + '─'*stack_width + '┤│'
    print(stack_cell_underline)


  def print_stack_bottom_cell(cell_value: int, stack_width: int) -> None:

    Pretty_printer.print_stack_cell_center(cell_value, stack_width)
    stack_cell_underline:str = '│╰' + '─'*stack_width + '╯│'
    print(stack_cell_underline)


  def print_stack_cell_center(value: int, stack_width: int) -> None:

    printable_value: str = str(value)
    value_length: int = len(printable_value)
    space_before: int = (stack_width - value_length) // 2
    space_after: int = (stack_width - value_length) // 2 + (stack_width - value_length) % 2
    final_string: str = '││' + ' '*space_before + printable_value + ' '*space_after + '││'
    print(final_string)