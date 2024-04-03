from typing import List

from iostuff.writer import Writer
from structures.field import Field

class Struct:
    def __init__(self, name: str, fields: List[Field]):
        self.name = name
        self.fields = fields

    def generate(self, o: Writer):
        o.w(f'type {self.name} struct {{')
        for field in self.fields:
            if field.is_derived():
                continue
            o.w(f'    {field.name} {field.t}')
        o.w("ID int")
        o.w(f'}}')

        o.w(f'type {self.name}Hydrated struct {{')
        for field in self.fields:
            o.w(f'    {field.name} {field.t}')
        o.w("ID int")
        o.w(f'}}')


class StructCreator:
    def __init__(self, s: Struct):
        self.s = s

    @staticmethod
    def for_struct(s: Struct) -> 'StructCreator':
        return StructCreator(s)

class StructUpdater:
    def __init__(self, s: Struct):
        self.s = s

    @staticmethod
    def for_struct(s: Struct) -> 'StructUpdater':
        return StructUpdater(s)
    
class StructReader:
    def __init__(self, s: Struct):
        self.s = s

    @staticmethod
    def for_struct(s: Struct) -> 'StructReader':
        return StructReader(s)
    
class StructDeleter:
    def __init__(self, s: Struct):
        self.s = s

    @staticmethod
    def for_struct(s: Struct) -> 'StructDeleter':
        return StructDeleter(s)