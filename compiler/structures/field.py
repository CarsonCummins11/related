# a field can be stored or derived
# a stored field is written as <name>: @<type>
# a derived field is written as <name>: <expression>
from iostuff.reader import Reader
from structures.expression import Expression, VariableExpression
from typing import TYPE_CHECKING, List
import uuid
if TYPE_CHECKING:
    from structures.program import Program

PRIMITIVES = ["int", "float", "bool", "string"]

class Field:
    def __init__(self, name: str, parent_name:str, t: str):
        self.name = name
        self.parent_name = parent_name
        self.t = t
    
    def is_derived(self) -> bool:
        if type(self) == DerivedField:
            return True
        return False
    
    def is_object_field(self) -> bool:
        return type(self) == ObjectField
    
    
    def dependencies(self) -> List[VariableExpression]:
        if type(self) == DerivedField:
            return self.expression.dependencies()
        return []

    @staticmethod
    def parse(reader: Reader, object_name: str, context: "Program") -> "Field":
        name = reader.read_while_matching("[a-zA-Z0-9_]")
        print(f"parsing field {name} in object {object_name}")
        assert name != "", "Field name cannot be empty"
        assert name[0].isalpha(), f"Field name {name} must start with a letter while parsing object {object_name}"
        reader.pop_whitespace()
        assert reader.pop() == ":", "Expected :"
        reader.pop_whitespace()
        if reader.peek() == "@":
            reader.pop()
            t = reader.readuntil(";")
            if not context.has_type(t):
                    context.assert_type_eventually_exists(t)
                
            if t not in PRIMITIVES:
                ret = ObjectField(name, object_name, t)
            else:
                ret = PrimitiveField(name, object_name, t)

            return ret
        else:
            return DerivedField.parse(reader, object_name, name, context)
        
    def get_derivation_string(self) -> str:
        raise NotImplementedError()
        


class PrimitiveField(Field):
    def __init__(self, name: str, object_name: str, t: str):
        super().__init__(name, object_name, t)
        assert t in PRIMITIVES, f"Stored field {name} in object {object_name} must be a primitive type, got {t}"

    def __str__(self):
        return f"{self.name}: stored value of type {self.t}"
    
    def get_derivation_string(self) -> str:
        return "obj." + self.name
    
class ObjectField(Field):
    def __init__(self, name: str, object_name: str, t: str):
        super().__init__(name, object_name, t)
        assert t not in PRIMITIVES, f"Stored field {name} in object {object_name} must be an object type, got {t}"

    def __str__(self):
        return f"{self.name}: object pointer to value of type {self.t}"
    
    def get_derivation_string(self) -> str:
        return self.name

class DerivedField(Field):
    
    def __init__(self, name: str, object_name: str, t: str, expression: Expression):
        super().__init__(name, object_name, t)
        self.expression = expression

    '''
    does NOT parse the name of the derived field, use Field.parse for that
    '''
    @staticmethod
    def parse(reader: Reader, object_name: str, field_name: str, context: "Program") -> "DerivedField":
        expression = Expression.parse(reader, object_name, field_name, context)
        reader.pop_whitespace()
        assert reader.pop() == ";", "Expected ;"
        return DerivedField(field_name, object_name, expression.t, expression)

    def __str__(self):
        return f"{self.name}: {self.expression}"
    
    def get_derivation_string(self) -> str:
        return self.expression.get_derivation_string()

