from typing import List

from structures.program import PRIMITIVES
from structures.field import Field
from structures.object import Object
from iostuff.writer import Writer

def type_for_sql(t: str) -> str:
    if t == "int":
        return "INTEGER"
    if t == "float":
        return "REAL"
    if t == "bool":
        return "BOOLEAN"
    if t == "string":
        return "TEXT"
    
    #assuming if its not a primitive, its a reference to another object
    return "INTEGER"

class Table:
    def __init__(self, name: str, fields: List[Field]):
        self.name = name
        self.fields = [field for field in fields if not field.is_derived()]

    def generate(self, o: Writer):
        o.w(f'CREATE TABLE {self.name} (')
        for field in self.fields:
            if field.is_list():
                continue
            else:
                if field.is_object_field():
                    o.w(f'    FOREIGN KEY ({field.name}) REFERENCES {field.t.replace("[]","")}(ID),')
                else:
                    o.w(f'    {field.name} {type_for_sql(field.t)},')
        o.w(f'    ID SERIAL PRIMARY KEY')
        o.w(');')

        #create tables for list fields
        for field in self.fields:
            if field.is_list():
                o.w(f'CREATE TABLE {self.name}_{field.name} (')
                o.w(f'    {self.name}_id INTEGER,')
                o.w(f'    {field.name} {type_for_sql(field.t.replace("[]",""))},')
                if field.t.replace("[]","") not in PRIMITIVES:
                    o.w(f'    FOREIGN KEY ({field.name}) REFERENCES {field.t.replace("[]","")}(ID),')
                o.w(f'    FOREIGN KEY ({self.name}_id) REFERENCES {self.name}(ID),')
                o.w(f'    ID SERIAL PRIMARY KEY')
                o.w(');')

    @staticmethod
    def for_object(obj: Object) -> 'Table':
        return Table(obj.name,obj.fields)