class Pretty_printer:

  def print_stack(array_stack: list[int]):

    stack_length: int = len(array_stack)
    if stack_length == 1:

      Pretty_printer.print_only_stack_cell(array_stack[0])
    else: 

      Pretty_printer.print_stack_top_cell(array_stack[-1])
      for i in range(stack_length - 2, 0, -1):

        cell_value: int = array_stack[i]
        Pretty_printer.print_stack_middle_cell(cell_value)
      
      Pretty_printer.print_stack_bottom_cell(array_stack[0])
    

  def print_only_stack_cell(single_value: int, stack_width: int = 20):

    stack_cell_top_line:str = '╭' + '─'*stack_width + '╮'
    stack_cell_underline:str = '╰' + '─'*stack_width + '╯'
    print(stack_cell_top_line)
    Pretty_printer.print_stack_cell_center(single_value)
    print(stack_cell_underline)


  def print_stack_top_cell(top_value: int, stack_width: int = 20):

    stack_cell_top_line:str = '╭' + '─'*stack_width + '╮'
    stack_cell_underline:str = '├' + '─'*stack_width + '┤'
    print(stack_cell_top_line)
    Pretty_printer.print_stack_cell_center(top_value)
    print(stack_cell_underline)


  def print_stack_middle_cell(cell_value:int, stack_width: int = 20):

    Pretty_printer.print_stack_cell_center(cell_value)
    stack_cell_underline:str = '├' + '─'*stack_width + '┤'
    print(stack_cell_underline)


  def print_stack_bottom_cell(cell_value: int, stack_width: int = 20):

    Pretty_printer.print_stack_cell_center(cell_value)
    stack_cell_underline:str = '╰' + '─'*stack_width + '╯'
    print(stack_cell_underline)


  def print_stack_cell_center(value: int, stack_width: int = 20):

    printable_value: str = str(value)
    value_length: int = len(printable_value)
    space_before: int = (stack_width - value_length) // 2
    space_after: int = (stack_width - value_length) // 2 + (stack_width - value_length) % 2
    final_string: str = '│' + ' '*space_before + printable_value + ' '*space_after + '│'
    print(final_string)