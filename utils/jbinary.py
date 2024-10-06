class jbinary: 

    # KEYS
    CODE = "code"
    BYTECODE = "bytecode"
    OPERATION = "opr"

    # OPERATORS
    PUSH = "push"
    LOAD = "load"
    BINARY_EXPR = "binary"
    DIVISION = "div"
    BYTECODE = "bytecode"
    INVOKE = "invoke"
    ASSERTION_ERROR = "java/lang/AssertionError"
    DUPPLICATION = 'dup'
    STORE = 'store'
    IF = 'if'
    IF_ZERO = 'ifz'
    GO_TO = 'goto'
    GET = 'get'
    NEW = 'new'
    THROW = 'throw'
    RETURN = 'return'
    NEW_ARRAY = 'newarray'
    ARRAY_STORE = 'array_store'
    ARRAY_LENGTH = 'arraylength'
    INCREMENT = 'incr'

    # CONDITION TYPES
    CONDITION = 'condition'
    TARGET = 'target'

    LARGER_OR_EQUAL = 'le'
    GREATER_OR_EQUAL = 'ge'
    NOT_EQUAL = 'ne'
    GREATER_THAN = 'gt'

    ASSERTION_ERROR_METHOD_SIGNATURE = "java/lang/AssertionError/<init>"