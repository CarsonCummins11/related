from typing import List

from structures.program import Program
from iostuff.writer import Writer
from generator.sql.table import Table


class Schema:
    def __init__(self, name: str, tables: List[Table]):
        self.name = name
        self.tables = tables

    def generate(self, o: Writer):
        o.use_file("schema.sql")
        for table in self.tables:
            table.generate(o)
        

    @staticmethod
    def for_program(program: Program) -> 'Schema':
        return Schema(program.objects)