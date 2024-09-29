class SimpleJVMInterpreter:
    def __init__(self):
        self.stack = []       # Stack for method execution
        self.locals = []      # Local variables for methods
        self.method_map = {}  # Map method ids to bytecode
        self.pc = 0           # Program counter

    def load_method(self, method_id, bytecode):
        """Load a method's bytecode into the interpreter."""
        self.method_map[method_id] = bytecode

    def execute_method(self, method_id, input_value):
        """Execute the given method with the provided input value."""
        if method_id not in self.method_map:
            print(f"Method {method_id} not found.")
            return

        # Load the bytecode for the specified method
        bytecode = self.method_map[method_id]
        self.locals = [input_value]  # Set the input value as the first local variable
        self.pc = 0  # Reset program counter
        self.stack = []  # Reset stack

        while self.pc < len(bytecode):
            instruction = bytecode[self.pc]
            print(f"PC: {self.pc}, Instruction: {instruction}, LOCALS: {self.locals}, STACK: {self.stack}")

            if instruction['opr'] == 'push':
                self.stack.append(instruction['value'])
            elif instruction['opr'] == 'return':
                return_value = self.stack.pop() if self.stack else None
                print(f"Returning: {return_value}")
                break
            else:
                print(f"Unknown operation: {instruction['opr']}")

            self.pc += 1  # Move to the next instruction

        # Final query output
        if self.stack:
            print(f"Query Result: {self.stack[-1]}")
        else:
            print("Query Result: None")

# Example usage
if __name__ == "__main__":
    interpreter = SimpleJVMInterpreter()

    # Define bytecode for a simple method 'justReturn' that returns an integer 0
    bytecode_just_return = [
        {'opr': 'push', 'value': {'type': 'integer', 'value': 0}},  # Push 0 onto the stack
        {'opr': 'return'},  # Return the top of the stack
    ]

    # Load the method into the interpreter
    interpreter.load_method('jpamb.cases.Simple.justReturn', bytecode_just_return)

    # Execute the method with input (in this case, the input is irrelevant for this method)
    interpreter.execute_method('jpamb.cases.Simple.justReturn', ())

