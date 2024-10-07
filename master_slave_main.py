from master_slave_interpreter.master import Master
import sys
import logging as l

method_id = sys.argv[1]
should_print: bool = False
if len(sys.argv) > 2:
  if sys.argv[2] == '--print':
    should_print = True
  
master: Master = Master(method_id, should_print=should_print)