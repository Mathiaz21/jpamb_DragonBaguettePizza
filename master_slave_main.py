from master_slave_interpreter.master import Master
import sys

#(name,) = sys.argv[1:]



main_file_path: str = 'decompiled/jpamb/cases/Arrays.json'
main_method_name: str = 'arrayInBounds'
name = 'jpamb.cases.Simple.assertInteger:(I)V'

master: Master = Master(name)

# TODO : Junction between this main file and the generation of results.json
