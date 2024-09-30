class Semantic_node:

  index:int
  children: list[int]

  def __init__(self, index:int, bytecode):

    self.index = index
    self.children = self.get_children_indices(self.index, bytecode)


  def print_node(self) -> None:

    print('Node : ')
    print('Index : ', self.index)
    if len(self.children) == 0:

      print('No children')
    else:

      print('Children : ')
      for child in self.children:
        print('  ->', child)
    print('')

  
  def get_children_indices(self, current_index: int, bytecode):

    children: list[int] = []
    match bytecode[current_index]['opr']:

      case 'ifz':
        children = self.get_if_instruction_children(current_index, bytecode)
      case 'goto':
        children = self.get_goto_instruction_children(current_index, bytecode)
      case 'return':
        children = []
      case _ : children = [current_index + 1]
      
    return children



  def get_if_instruction_children(self, current_index, bytecode) -> list[int]:
  
    children: list[int] = [current_index + 1]
    target : int = bytecode[current_index]['target']
    children.append( target)
    return children


  def get_goto_instruction_children(self, current_index, bytecode) -> list[int]:

    return [ bytecode[current_index]['target'] ]