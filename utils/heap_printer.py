class Heap_printer:


  def print_heap(heap: list[list[int]]) -> None:

    heap_width: int = Heap_printer.get_heap_width(heap)
    Heap_printer.print_heap_top(heap_width)
    
    heap_length: int = len(heap)
    for i in range(heap_length-1, -1, -1):

      current_array: list[int] = heap[i]
      Heap_printer.print_array(current_array, i, heap_width)
    Heap_printer.print_heap_bottom(heap_width)


  def print_heap_top(heap_width) -> None:
    heap_top = ' ╭' + '─'*(heap_width-2) + '╮'
    print(heap_top)

  def print_heap_bottom(heap_width) -> None:
    heap_top = ' ╰' + '─'*(heap_width-2) + '╯'
    print(heap_top)



  def print_array(array: list[int], array_index: int, heap_width: int) -> None:

    Heap_printer.print_array_top(array, heap_width)
    Heap_printer.print_array_center(array, array_index, heap_width)
    Heap_printer.print_array_bottom(array, heap_width)


  def print_array_center(array: list[int], array_index: int, heap_width: int) -> None:

    array_center: str = f' {array_index} '
    if len(array) == 0:

      array_center += '││'
    else:
      array_center += '│'
      for N in array:
        array_center += f' {N} │'

    completed_array_center: str = Heap_printer.complete_array_string(array_center, heap_width)
    print(completed_array_center)


  def print_array_top(array: list[int], heap_width: int) -> None:

    array_top: str = ' ╵ '
    if len(array) == 0:

      array_top += '╭╮'
    else:

      array_top += '╭'
      for N in array[:-1]:

        cell_width: int = Heap_printer.get_cell_width(N)
        array_top += '─'*cell_width + '┬'
      last_int: int = array[-1]
      last_cell_width: int = Heap_printer.get_cell_width(last_int)
      array_top += '─'*last_cell_width + '╮'
    completed_array_top: str = Heap_printer.complete_array_string(array_top, heap_width)
    print(completed_array_top)


  def print_array_bottom(array: list[int], heap_width: int) -> None:

    array_bottom: str = ' ╷ '
    if len(array) == 0:

      array_bottom += '╰╯'
    else:

      array_bottom += '╰'
      for N in array[:-1]:

        cell_width: int = Heap_printer.get_cell_width(N)
        array_bottom += '─'*cell_width + '┴'
      last_int: int = array[-1]
      last_cell_width: int = Heap_printer.get_cell_width(last_int)
      array_bottom += '─'*last_cell_width + '╯'
    completed_array_bottom: str = Heap_printer.complete_array_string(array_bottom, heap_width)
    print(completed_array_bottom)




  def get_heap_width(heap: list[list[int]]):

    array_widths: list[int] = [Heap_printer.get_array_width(array) for array in heap]
    max_width: int = max(array_widths) + 4
    return max_width

  def get_array_width(array: list[int]):

    array_length = 1
    for N in array:
      array_length += 1 + Heap_printer.get_cell_width(N)
    return array_length
  


  def get_cell_width(N: int) -> int:

    if type(N) == str:
      print('N is not an int')
      print(N)
    N = max(N, 1)
    cell_width: int = 2
    while(N != 0):

      cell_width += 1
      N = N // 10
    return cell_width
  

  def complete_array_string(array_string: str, heap_length: int) -> str:
  
    string_length: int = len(array_string)
    space_to_complete: int = heap_length -  string_length 
    completed_string: str = array_string + ' '*space_to_complete + '│'
    return completed_string
  


# sandbox_heap: list[list[int]] = [
#   [1,20,300],
#   [],
#   [10000000],
#   [1,2,3,4,5,6]
# ]
# Heap_printer.print_heap(sandbox_heap)