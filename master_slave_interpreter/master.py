from master_slave_interpreter.slave import Slave
from utils.file_manipulation import File_manipulator
from jpamb_utils import MethodId
from utils.jpamb_criteria import jpamb_criteria

class Master:

  probabilities: dict[str, float] = {
    jpamb_criteria.DIVIDE_BY_ZERO: 0.,
    jpamb_criteria.ASSERTION_ERROR: 0.,
    jpamb_criteria.ARRAY_OUT_OF_BOUNDS: 0.,
    jpamb_criteria.INFINITE_LOOP: 0.,
    jpamb_criteria.NULL_POINTER: 0.,
    jpamb_criteria.OK: 0.,
  }

  __program_bytecode_file_path: str = ''
  __method_name: str = ''
  __reports_from_slaves: list[dict] = []
  __method : MethodId = None

  def __init__(self, method_id: str) -> None:
    
    self.__method = MethodId.parse(method_id)
    self.setup_master_parameters(method_id)
    self.drop_slaves_on_bytecode()
    self.process_reports_from_slaves()
    self.print_probabilities_for_game()


  def drop_slaves_on_bytecode(self):

    slave_list = []
    possible_params_values = [[],[]]
    for i,param in enumerate(self.__method.params):
      possible_params_values[i] = Master.get_value_list_from_type(param)
    
    for param_1_value in possible_params_values[0]:
          params = [param_1_value]
          if possible_params_values[1]:
             for param_2_value in possible_params_values[1]:
                if len(params) == 2:
                  params[1] = param_2_value
                else:    
                  params.append(param_2_value)
                slave_list.append(Slave(self.__program_bytecode_file_path, self.__method_name, self.__reports_from_slaves,params))
          else:
            slave_list.append(Slave(self.__program_bytecode_file_path, self.__method_name, self.__reports_from_slaves,params))    


    reports = []
    if slave_list:  
      for slave in slave_list:
         slave.run() 

    _ = reports

  

  def setup_master_parameters(self, method_id: str) -> None:

    self.__program_bytecode_file_path = File_manipulator.method_id_to_filepath(method_id)
    self.__method_name = File_manipulator.method_id_to_method_name(method_id)


  def get_value_list_from_type(param):
      match param:
          case "boolean":
              return [True, False]
          case "int":
              return [ 11 ]  #[0, -1, 1, 123456, -123456, 2147483647, -2147483648]  # max and min 32-bit int
          case "char":
              return ['a', 'z', 'A', 'Z', '0', '\n', '\t']  # common ASCII chars
          case "char[]":
              return [['a', 'b', 'c'], ['A', 'B', 'C'], [], ['\n', '\t']]  # various char arrays
          case "int[]":
              return [[0, 1, -1], [2147483647, -2147483648], [], [123, -456]]  # int arrays
          case _:
              return ""
         

  def process_reports_from_slaves(self):
    
    reports: list[ dict[str, float] ] = self.__reports_from_slaves
    number_of_reports: int = len(reports)
    if number_of_reports == 0:
       raise ValueError('No reports from slaves to process')
    for report in reports:

      self.add_probabilities_from_single_report(report)
    self.normalize_reports(number_of_reports)



  def add_probabilities_from_single_report(self, report: dict[str, bool]) -> None:
     
    no_error: bool = True
    for criteria in report:
      if report[criteria]:
          
        self.probabilities[criteria] += 1.
        no_error = False
    if no_error:
      self.probabilities[jpamb_criteria.OK] += 1.

     
        
  def normalize_reports(self, number_of_reports: int):
     for criteria in self.probabilities:
        self.probabilities[criteria] /= number_of_reports


  def print_probabilities_for_game(self):
     for criteria in self.probabilities:
        
        percentage: int = int( self.probabilities[criteria]*100 )
        criteria_report: str = f'{criteria};{percentage}%'
        print(criteria_report)