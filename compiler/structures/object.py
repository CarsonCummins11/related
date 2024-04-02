#an object is a named list of fields
from typing import List
from compiler.io.reader import Reader
from compiler.structures.program import Program
from compiler.structures.field import Field

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