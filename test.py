import jpype
import jpype.imports
from jpype.types import *

# Start the JVM
jpype.startJVM(classpath=['SmallClass.java'])

# Import the SmallClass from the com.example package
from SmallClass import SmallClass

# Create an instance of the SmallClass
obj = SmallClass()
result = obj.sayHello()

print(result)  # Output should be: Hello from Java!

# Shutdown the JVM
jpype.shutdownJVM()

