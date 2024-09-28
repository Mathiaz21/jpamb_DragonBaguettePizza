from mathias_interpreter import *

main_file_path: str = '../decompiled/jpamb/cases/Loops.json'
main_method_name: str = 'forever'

main_interpreter: Mathias_interpreter = Mathias_interpreter(main_file_path, main_method_name)

# main_interpreter.print_tree_nodes()

main_interpreter.follow_program()