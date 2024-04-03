#an object is a named list of fields
from typing import List
from iostuff.reader import Reader
from structures.field import Field
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from structures.program import Program

class Object:
    def __init__(self, name:str, fields: List[Field]):
        self.name = name
        self.fields = fields

    def get_field(self, name: str) -> Field:
        for field in self.fields:
            if field.name == name:
                return field
        raise Exception(f"Field {name} does not exist in object {self.name}")
    
    def has_field(self, name: str) -> bool:
        for field in self.fields:
            if field.name == name:
                return True
        return False
    
    def __str__(self):
        ret = f"{self.name}:\n"
        for field in self.fields:
            ret += f"    {field}\n"

        return ret

    @staticmethod
    def parse(reader: Reader, context: "Program") -> "Object":
        name = reader.read_while_matching("[a-zA-Z0-9_]")
        assert name != "", "Object name cannot be empty"
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

        return Object(name, fields)