# a program is a list of objects and a list of functions
from typing import List, Tuple
from iostuff.reader import Reader
from structures.function import Function
from structures.object import Object
from structures.expression import VariableExpression

PRIMITIVES = ["int", "float", "bool", "string"]

class Program:
    def __init__(self, name: str, objects: List[Object] = [], functions: List[Function] = []):
        self.objects = objects
        self.functions = functions
        self.name = name

        self.types_must_exist: List[str] = []
        self.variables_must_exist: List[VariableExpression] = []

        self.variable_type_assertions: List[Tuple[str,str]] = []

    def assert_type_eventually_exists(self, t: str):
        self.types_must_exist.append(t)
    
    def assert_variable_eventually_exists(self, v: VariableExpression):
        self.variables_must_exist.append(v)
    
    def assert_variable_has_type(self, v: str, t: str):
        self.variable_type_assertions.append((v,t))

    def check(self):
        for t in self.types_must_exist:
            assert self.has_type(t), f"Type {t} must exist"
        
        for v in self.variables_must_exist:
            obj = self.get_object(v.obj)
            assert obj.has_field(v.name), f"Variable {v} must exist"
            vv = obj.get_field(v.name)
            v.t = vv.t
        
        for v, t in self.variable_type_assertions:
            if not self.has_type(t):
                raise Exception(f"Type {t} must exist")
            
            objname, fieldname = v.split(".")
            obj = self.get_object(objname)
            found = False
            for field in obj.fields:
                if field.name == fieldname:
                    found = True
                    break
            assert found, f"Variable {v} must exist"
            assert field.t == t, f"Field {v} must have type {t}"


    def has_type(self, t: str) -> bool:
        for obj in self.objects:
            if obj.name == t:
                return True
        return t in PRIMITIVES

    def get_object(self, name: str) -> Object:
        for obj in self.objects:
            if obj.name == name:
                return obj
        raise Exception(f"Object {name} not found")
    def get_function(self, name: str) -> Function:
        for func in self.functions:
            if func.name == name:
                return func
        raise Exception(f"Function {name} not found")
    def has_object(self, name: str) -> bool:
        for obj in self.objects:
            if obj.name == name:
                return True
        return False
    def has_function(self, name: str) -> bool:
        print(self.functions)
        for func in self.functions:
            if func.name == name:
                return True
        return False
    
    def add_object(self, obj: Object):
        self.objects.append(obj)
    

    def __str__(self) -> str:
        ret = ""
        for obj in self.objects:
            ret += f"{obj}\n\n"

        return ret


    @staticmethod
    def parse(src: str, name: str, functions: List[Function]) -> 'Program':
        reader = Reader(src)
        result = Program(name, [], functions)

        while reader.can_read():
            result.add_object(Object.parse(reader, result))

        result.check()

        return result
