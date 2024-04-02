# a field can be stored or derived
# a stored field is written as <name>: @<type>
# a derived field is written as <name>: <expression>
from compiler.io.reader import Reader
from compiler.structures.program import Program

class Field:
    def __init__(self, name: str, parent_name:str, t: str):
        self.name = name
        self.parent_name = parent_name
        self.t = t
    
    @staticmethod
    def parse(reader: Reader, object_name: str, context: Program) -> "Field":
        name = reader.read_while_matching("[a-zA-Z0-9_]")
        assert name != "", "Field name cannot be empty"
        assert name[0].isalpha(), f"Field name {name} must start with a letter while parsing object {object_name}"
        reader.pop_whitespace()
        assert reader.pop() == ":", "Expected :"
        reader.pop_whitespace()
        if reader.peek() == "@":
            reader.pop()
            t = reader.readuntil(";")
            ret = StoredField(name, object_name, t)
            if not context.is_type(t):
                context.assert_type_eventually_exists(t)
            return ret
        else:
            return DerivedField.parse(reader, object_name, name, context)
        


class StoredField(Field):
    def __init__(self, name: str, object_name: str, t: str):
        super().__init__(name, object_name, t)

class DerivedField(Field):
    
    def __init__(self, name: str, object_name: str, t: str, expression: Expression):
        super().__init__(name, object_name, t)
        self.expression = expression

    '''
    does NOT parse the name of the derived field, use Field.parse for that
    '''
    @staticmethod
    def parse(reader: Reader, object_name: str, field_name: str, context: Program) -> "DerivedField":
        expression = Expression.parse(reader, object_name, field_name, context)
        return DerivedField(field_name, object_name, expression.t, expression)


