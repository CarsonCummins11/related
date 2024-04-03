from typing import List

from structures.field import Field
from structures.object import Object
from iostuff.writer import Writer

class Table:
    def __init__(self, name: str, fields: List[Field]):
        self.name = name
        self.fields = fields

    def generate(self, o: Writer):
        o.w(f'CREATE TABLE {self.name} (')
        for field in self.fields:
            o.w(f'    {field.name} {field.type},')
        o.w(f'    ID SERIAL PRIMARY KEY')
        o.w(');')

    @staticmethod
    def for_object(obj: Object) -> 'Table':
        return Table(obj.name,obj.fields)