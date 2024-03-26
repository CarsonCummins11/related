from parser.reader import Reader
from parser.field import Field
from typing import List
from parser.value import VariableValue, FunctionValue
from parser.config import PRIMITIVES, SQL_KEYWORDS

#a program is a list of data objects
class Object:
    def __init__(self, name:str, fields: List[Field]):
        self.name = name
        assert self.name not in PRIMITIVES, f"Object name {self.name} is a primitive type"
        assert self.name not in SQL_KEYWORDS, f"Object name {self.name} is a SQL keyword"
        assert self.name[0].isupper(), f"Object name {self.name} must start with a capital letter"
        self.fields = fields
        for f in self.fields:
            assert f.name not in PRIMITIVES, f"Field name {f.name} is a primitive type"
            assert f.name not in SQL_KEYWORDS, f"Field name {f.name} is a SQL keyword"
    @staticmethod
    def parse(reader: Reader, function_table) -> "Object":
        name = reader.readuntil("{")
        print("Parsing object", name)
        fields = []
        while reader.peek_pop_result() not in ["}",""]:
            fields.append(Field.parse(reader, function_table))
        try:
            reader.pop()
        except:
            print("eof ERROR but all else good")
        return Object(name, fields)


class Program:
    def __init__(self, src, function_table = {}):
        self.src = src
        self.reader = Reader(src)
        self.objects:List[Object] = []
        self.function_table = function_table

    def parse(self):
        self.reader.reset()
        print("Parsing program:\n", self.src)
        while self.reader.can_read():
            self.objects += [Object.parse(self.reader, self.function_table)]
        self.construct_types()
        for o in self.objects:
            print(f"Object {o.name}")
            for f in o.fields:
                print(f"\tField {f.name} of type {f.t}")
                if f.derived:
                    print(f"\t\tDerived from {f.derived.t} {f.derived.value.name if "name" in f.derived.value.__dict__ else 'primitive constant'}")
                    if type(f.derived.value) == FunctionValue:
                        print(f"\t\t\tFunction {f.derived.value.name}")
                        cc = 0
                        for arg in f.derived.value.args:
                            cc+=1
                            print(f"\t\t\t\tArg {cc} of type {arg.t}")
        for f in self.function_table:
            print(f"Function {f} of type {self.function_table[f].t}")
            print(f"\tArgs: {self.function_table[f].arg_types}")

    def construct_types(self):
        custom_types = [o.name for o in self.objects]
        for o in self.objects:
            for f in o.fields:
                f.resolve_type(o, self.function_table, custom_types)