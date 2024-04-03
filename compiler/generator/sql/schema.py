from typing import List

from structures.program import Program
from iostuff.writer import Writer
from generator.sql.table import Table


class Schema:
    def __init__(self, tables: List[Table]):
        self.tables = tables

    def generate(self, o: Writer):
        o.use_file("schema.sql")
        for table in self.tables:
            table.generate(o)
        

    @staticmethod
    def for_program(program: Program) -> 'Schema':
        return Schema([
            Table.for_object(obj) for obj in program.objects
        ])