import parser.program
from generator.writer import Writer
from typing import List
from generator.data.object import Object

class DataPlatform:
    def __init__(self, objects: List[parser.program.Object]):
        self.objects = [Object(obj) for obj in objects]

    def generate(self, o: Writer):
        for obj in self.objects:
            obj.generate(o)