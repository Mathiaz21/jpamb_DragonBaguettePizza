from master_slave_interpreter.master import Master

main_file_path: str = 'decompiled/jpamb/cases/Simple.json'
main_method_name: str = 'divideByZero'

master: Master = Master(main_file_path, main_method_name)
