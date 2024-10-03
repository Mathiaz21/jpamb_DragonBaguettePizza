from master_slave_interpreter.master import Master

main_file_path: str = 'decompiled/jpamb/cases/Arrays.json'
main_method_name: str = 'arrayOutOfBounds'

master: Master = Master(main_file_path, main_method_name)

# TODO : Junction between this main file and the generation of results.json
