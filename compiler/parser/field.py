from parser.value import Value, VariableValue
from parser.config import PRIMITIVES
from parser.reader import Reader
class Field:
    def __init__(self, name: str, t: str, derived: Value = None):
        self.name = name
        self.t = t
        self.derived = derived

    def resolve_type(self, parent, function_table, custom_types: list):
        possible_types = custom_types + PRIMITIVES
        if self.t == "undefined":
            assert self.derived, f"Field {self.name} has no type and is not derived from another field."
            print(f"Field {self.name} has no type, but it's derived from another field. Checking if that field has a type.")
            if self.derived.t != "undefined":
                self.t = self.derived.t
                print(f"Field {self.name} is now of type {self.t}, derived from {self.derived.t}")
            else:
                print(f"Field {self.name} is derived from another field, but that field has no type. Attempting to resolve type.")
                self.derived.construct_type(parent, function_table, custom_types)
                self.t = self.derived.t
                if type(self.derived.value) == VariableValue:
                    if self.derived.value.name in possible_types:
                        self.t = self.derived.value.name
                        self.derived = None
                else:
                    print(f"Field {self.name} is now of type {self.t}, derived from {self.derived.t}")

    @staticmethod
    def parse(reader: Reader, function_table: dict = {}, expected_type="undefined") -> "Field":
        name = reader.readuntil(":")
        print("Parsing field", name)
        #parse a value, if it's a variable value, we can check if that's actually a typedef later and if so, use it as a non-derived field with type
        v = Value.parse(reader, function_table, expected_type)
        reader.pop()
        return Field(name, v.t, v)
    