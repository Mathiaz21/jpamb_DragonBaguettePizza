import sys, logging
from solutions.jbinary import jbinary
from jpamb_utils import MethodId

l = logging
l.basicConfig(level=logging.DEBUG)
(name,) = sys.argv[1:]


method = MethodId.parse(name)
m = method.load()





sys.exit(0)