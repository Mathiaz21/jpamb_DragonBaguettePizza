from master_slave_interpreter.slave import Slave
from utils.file_manipulation import File_manipulator
from utils.results_printer import print_results

class Master:

  probabilities: dict[str, float] = {
    'division_by_zero': 0.,
    'assertion_error': 0.,
    'array_out_of_bounds': 0.,
    'infinite_loop': 0.,
    'null_pointer': 0.,
    'no_error': 0.,
  }

  program_bytecode_file_path: str = ''
  method_name: str = ''
  reports_from_slaves: list[dict] = []


  def __init__(self, method_id: str) -> None:
    
    self.setup_master_parameters(method_id)
    self.drop_a_slave_on_bytecode()
    print(self.reports_from_slaves)


  def drop_a_slave_on_bytecode(self):

    father_slave: Slave = Slave(self.program_bytecode_file_path, self.method_name, self.reports_from_slaves)

    father_slave.follow_program()
    print_results(self.probabilities)


  

  def setup_master_parameters(self, method_id: str) -> None:

    self.program_bytecode_file_path = File_manipulator.method_id_to_filepath(method_id)
    self.method_name = File_manipulator.method_id_to_method_name(method_id)
