from master_slave_interpreter.slave import *

main_file_path: str = 'decompiled/jpamb/cases/Calls.json'
main_method_name: str = 'allPrimesArePositive'

main_interpreter: Slave = Slave(main_file_path, main_method_name)

# main_interpreter.print_tree_nodes()

main_interpreter.follow_program()