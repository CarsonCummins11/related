# an expression is one of a constant, variable, or function
# a constant is a string, int, float, or bool
# a variable is a reference to a field in the parent object
# a function mutates a list of expressions


from compiler.io.reader import Reader
from compiler.structures.program import Program

class Expression:
    
    @staticmethod
    def parse(reader: Reader, context: "Program") -> "Expression":
        return Expression()
    
class ConstantExpression(Expression):
    def __init__(self, value: str, t: str):
        self.value = value
        self.t = t
    
    @staticmethod
    def parse(reader: Reader, context: "Program") -> "ConstantExpression":
        if reader.peek() == '"':
            reader.pop()
            value = reader.readuntil('"')
            reader.pop()
            return ConstantExpression(value, "string")
        if reader.peek() in "1234567890":
            value = reader.read_while_matching("[0-9]")
            if reader.peek() == ".":
                value += reader.pop() + reader.read_while_matching("[0-9]")
                return ConstantExpression(float(value), "float")
            return ConstantExpression(int(value), "int")
        
        if reader.peek() == "t":
            assert reader.pop() == "r"
            assert reader.pop() == "u"
            assert reader.pop() == "e"
            assert reader.peek().isalpha() == False and reader.peek() != "_"
            return ConstantExpression(True, "bool")
        if reader.peek() == "f":
            assert reader.pop() == "a"
            assert reader.pop() == "l"
            assert reader.pop() == "s"
            assert reader.pop() == "e"
            assert reader.peek().isalpha() == False and reader.peek() != "_"
            return ConstantExpression(False, "bool")
    
class VariableExpression(Expression):
    def __init__(self, name: str, obj: str, t: str):
        self.name = name
        self.obj = obj
        self.t = t
    
    @staticmethod
    def parse(reader: Reader, obj: str, context: Program) -> Expression:
        name = reader.read_while_matching("[a-zA-Z0-9_]")
        assert name != "", "Variable name cannot be empty"
        assert name[0].isalpha(), f"Variable name {name} must start with a letter"
        context.assert_variable_eventually_exists(VariableExpression(name, obj, "unknown"))

class FunctionExpression(Expression):
    ...