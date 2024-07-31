#an object is a named list of fields
from typing import List
from iostuff.reader import Reader
from structures.field import Field
from structures.governance import Governance
from structures.expression import TRUE_EXPRESSION
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from structures.program import Program

class Object:
    def __init__(self, name:str, fields: List[Field], governance: Governance, context: "Program"):
        self.name = name
        self.fields = fields
        assert context, "Context must be provided to object"
        self.context = context
        self.governance = governance

    def get_field(self, name: str) -> Field:
        if "." in name:
            objname, fieldname = name.split(".")
            if self.has_field(objname):
                return self.context.get_object(self.get_field(objname).t).get_field(fieldname)
            raise Exception(f"Field {objname} does not exist in object {self.name}")
        for field in self.fields:
            if field.name == name:
                return field
        raise Exception(f"Field {name} does not exist in object {self.name}")
    
    def has_field(self, name: str) -> bool:
        if "." in name:
            objname, fieldname = name.split(".")
            if self.has_field(objname):
                return self.context.get_object(self.get_field(objname).t).has_field(fieldname)
            return False
        for field in self.fields:
            if field.name == name:
                return True
        return False
    
    def stored_fields(self) -> List[Field]:
        return [field for field in self.fields if not field.is_derived() and not field.is_list()]
    
    def __str__(self):
        ret = f"{self.name}:\n"
        for field in self.fields:
            ret += f"    {field}\n"

        return ret

    @staticmethod
    def parse(reader: Reader, context: "Program") -> "Object":
        name = reader.read_while_matching("[a-zA-Z0-9_]")
        assert name != "", "object name cant start with "+reader.pop()#"Object name cannot be empty"
        assert name[0].isalpha(), "Object name must start with a letter"
        assert not context.has_object(name), f"Object {name} already exists"
        reader.pop_whitespace()
        assert reader.pop() == "{", "Expected {"
        reader.pop_whitespace()
        fields = []
        while reader.peek() != "}":
            fields.append(Field.parse(reader, name, context))
            reader.pop_whitespace()
        assert reader.pop() == "}", "Expected }"
        reader.pop_whitespace()

        governance = Governance(context, {
            "C": TRUE_EXPRESSION,
            "R": TRUE_EXPRESSION,
            "U": TRUE_EXPRESSION,
            "D": TRUE_EXPRESSION
        })


        #parse governance string if present
        if reader.peek() == "-":
            governance = Governance.parse(reader, name, context)

        return Object(name, fields, governance, context)