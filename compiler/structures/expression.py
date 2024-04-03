# an expression is one of a constant, variable, or function
# a constant is a string, int, float, or bool
# a variable is a reference to a field in the parent object
# a function mutates a list of expressions


from iostuff.reader import Reader
from typing import List

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from structures.program import Program

class Expression:
    def __init__(self,t: str):
        self.t = t
    
    @staticmethod
    def parse(reader: Reader, obj:str, field_name: str, context: "Program") -> "Expression":
        if reader.peek() == '"' or reader.peek().isdigit():
            return ConstantExpression.parse(reader, context)
        startpos = reader.get_pos()
        if reader.peek().isalpha():
            name = reader.read_while_matching("[a-zA-Z0-9_]")
            if reader.peek() == "(":
                reader.pop()
                reader.set_pos(startpos)
                return FunctionExpression.parse(reader, obj, field_name, context)
            if name == "true" or name == "false":
                return ConstantExpression(name == "true", "bool")
            reader.set_pos(startpos)
            return VariableExpression.parse(reader, obj, field_name, context)
        assert False, f"Expected expression, got {reader.peek()}"
        
        
        
        
    
class ConstantExpression(Expression):
    def __init__(self, value: str, t: str):
        self.value = value
        self.t = t
    @staticmethod
    def parse(reader: Reader, context: "Program") -> "ConstantExpression":
        if reader.peek() == '"':
            reader.pop()
            value = reader.readuntil('"')
            return ConstantExpression(value, "string")
        if reader.peek().isdigit() or reader.peek() == "-":
            neg = reader.peek() == "-"
            if neg:
                reader.pop()
            value = ("-" if neg else "") + reader.read_while_matching("[0-9]")
            if reader.peek() == ".":
                value += reader.pop() + reader.read_while_matching("[0-9]")
                return ConstantExpression(float(value), "float")
            return ConstantExpression(int(value), "int")
        
        if reader.peek() == "t":
            assert reader.read_while_matching("[a-z]") == "true"
            return ConstantExpression(True, "bool")
        if reader.peek() == "f":
            assert reader.read_while_matching("[a-z]") == "false"
            return ConstantExpression(False, "bool")
        
        assert False, f"Expected constant, got {reader.peek()}"

    def __str__(self):
        return str(self.value)
    
class VariableExpression(Expression):
    def __init__(self, name: str, obj: str, t: str):
        self.name = name
        self.obj = obj
        self.t = t
    
    @staticmethod
    def parse(reader: Reader, obj: str, field_name: str, context: "Program") -> Expression:
        name = reader.read_while_matching("[a-zA-Z0-9_]")
        assert name != "", "Variable name cannot be empty"
        assert name[0].isalpha(), f"Variable name {name} must start with a letter"
        vr = VariableExpression(name, obj, "unknown")
        context.assert_variable_eventually_exists(vr)
        return vr
    
    def __str__(self):
        return f"{self.obj}.{self.name}"

class FunctionExpression(Expression):
    def __init__(self, name: str, t: str, args: List[Expression]):
        self.name = name
        self.args = args
        self.t = t
    
    @staticmethod
    def parse(reader: Reader, obj: str, field: str, context: "Program") -> "FunctionExpression":
        name = reader.read_while_matching("[a-zA-Z0-9_]")
        assert name != "", "Function name cannot be empty"
        assert name[0].isalpha(), f"Function name {name} must start with a letter"
        assert context.has_function(name), f"Function {name} must exist"
        reader.pop_whitespace()
        assert reader.pop() == "(", "Expected ("
        reader.pop_whitespace()
        args = []

        while reader.peek() != ")":
            args.append(Expression.parse(reader, obj, field, context))
            reader.pop_whitespace()
            if reader.peek() == ",":
                reader.pop()
                reader.pop_whitespace()

        assert reader.pop() == ")", "Expected )"
        t = context.get_function(name).t
        return FunctionExpression(name, t, args)
    
    def __str__(self):
        return f"{self.name}({', '.join(map(str, self.args))}) returns {self.t}"