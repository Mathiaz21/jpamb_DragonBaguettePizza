from master_slave_interpreter.master import Master
import sys

method_id = sys.argv[1]
master: Master = Master(method_id)
