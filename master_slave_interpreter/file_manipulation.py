import json

class File_manipulator:

  def get_method_bytecode_from_file(method_name: str, file_path: str) -> list:
  
    file = open(file_path)
    file_to_json = json.load(file)
    file.close()
    return File_manipulator.find_method_bytecode_in_json(method_name, file_to_json)
  

  def find_method_bytecode_in_json(method_name: str, jsoned_file: dict) -> list:

    for whole_method_instance in jsoned_file['methods']:

      if whole_method_instance['name'] == method_name:
        return whole_method_instance['code']['bytecode']
      
    return