import sys, logging
from analyzers.jbinary import jbinary
from jpamb_utils import MethodId
from analyzers.interpreter import Interpreter

l = logging
l.basicConfig(level=logging.DEBUG)
#(name,) = sys.argv[1:]

name = "jpamb.cases.Calls.allPrimesArePositive:(I)V"

method = MethodId.parse(name)
fileName = "C:\GitHub\jpamb_DragonBaguettePizza\decompiled\jpamb\cases\Calls.json"

inter = Interpreter(fileName,method.method_name)

sys.exit(0)