from utils.file_manipulation import File_manipulator
from master_slave_interpreter.slave import Slave

class Master:

  probabilities: dict = {
    'division_by_zero': 0,
    'assertion_error': 0,
    'array_out_of_bounds': 0,
    'infinite_loop': 0,
  }

  program_bytecode_file_path: str = ''
  method_name: str = ''
  bytecode: list = []
  reports_from_slaves: list[dict] = []


  def __init__(self, program_bytecode_file_path, method_name) -> None:
    
    self.program_bytecode_file_path = program_bytecode_file_path
    self.method_name = method_name
    self.bytecode = File_manipulator.get_method_bytecode_from_file(self.method_name, self.program_bytecode_file_path)
    self.drop_a_slave_on_bytecode()


  def drop_a_slave_on_bytecode(self):

    father_slave: Slave = Slave(self.program_bytecode_file_path, self.method_name, self.reports_from_slaves)

    father_slave.follow_program()