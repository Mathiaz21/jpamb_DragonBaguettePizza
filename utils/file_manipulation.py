import json
import re

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
  

  def method_id_to_filepath(method_id: str) -> str:

    regex_rule: str = r'jpamb\.cases\.([A-Z][a-z]+)\.[A-Za-z]+:\([A-Z]\)[A-Z]'
    regex_info = re.match(regex_rule, method_id)
    if regex_info:

      file_name:str = regex_info.group(1)
      filepath: str = f'decompiled/jpamb/cases/{file_name}.json'
      print(filepath)
      return filepath
    else:

      print('file not matched')


  def method_id_to_method_name(method_id: str) -> str:

    regex_rule: str = r'jpamb\.cases\.[A-Z][a-z]+\.([A-Za-z]+):\([A-Z]\)[A-Z]'
    regex_info = re.match(regex_rule, method_id)
    if regex_info:

      method_name:str = regex_info.group(1)
      print(method_name)
      return method_name
    else:

      print('method_name not matched')

File_manipulator.method_id_to_method_name('jpamb.cases.Simple.assertPositive:(I)V')