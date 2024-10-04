from master_slave_interpreter.slave import Slave
from utils.file_manipulation import File_manipulator
from jpamb_utils import MethodId

class Master:

  probabilities: dict[str, float] = {
    'division_by_zero': 0.,
    'assertion_error': 0.,
    'array_out_of_bounds': 0.,
    'infinite_loop': 0.,
    'null_pointer': 0.,
    'no_error': 0.,
  }

  __program_bytecode_file_path: str = ''
  __method_name: str = ''
  __reports_from_slaves: list[dict] = []
  __method : MethodId = None

  def __init__(self, method_id: str) -> None:
    
    self.__method = MethodId.parse(method_id)
    self.setup_master_parameters(method_id)
    self.drop_a_slave_on_bytecode()
    print(self.__reports_from_slaves)


  def drop_a_slave_on_bytecode(self):

    slave_list = []
    possible_params_values = [[],[]]
    for i,param in enumerate(self.__method.params):
      possible_params_values[i] = get_value_list_from_type(param)
    
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

    #father_slave: Slave = Slave(self.__program_bytecode_file_path, self.__method_name, self.__reports_from_slaves)
    #father_slave.follow_program()

  

  def setup_master_parameters(self, method_id: str) -> None:

    self.__program_bytecode_file_path = File_manipulator.method_id_to_filepath(method_id)
    self.__method_name = File_manipulator.method_id_to_method_name(method_id)


def get_value_list_from_type(param):
    match param:
        case "boolean":
            return [True, False]
        case "int":
            return [0, -1, 1, 123456, -123456, 2147483647, -2147483648]  # max and min 32-bit int
        case "char":
            return ['a', 'z', 'A', 'Z', '0', '\n', '\t']  # common ASCII chars
        case "char[]":
            return [['a', 'b', 'c'], ['A', 'B', 'C'], [], ['\n', '\t']]  # various char arrays
        case "int[]":
            return [[0, 1, -1], [2147483647, -2147483648], [], [123, -456]]  # int arrays
        case _:
            return ""