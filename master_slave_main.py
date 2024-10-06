from master_slave_interpreter.master import Master
import sys
import logging as l

should_print: bool = False
if __name__ == '__main__':
  should_print = True
  
method_id = sys.argv[1]
master: Master = Master(method_id, should_print=should_print)
