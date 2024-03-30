from typing import List, Union
from parser.function import Function
from parser.reader import Reader, get_user_input
from parser.config import PRIMITIVES


def lookaheadValue(reader: Reader, parent_name:str,  function_table: dict = {}, expected_type = "undefined"):
    saved_pos = reader.get_pos()
    res = reader.pop()
    while reader.peek().isalpha() or reader.peek().isdigit() or reader.peek() == "_":
        res +=reader.pop()
    assert res, f"Expected a value at {saved_pos}, {reader.peek()}, got nothing."
    if reader.peek() == "(":
        print("parsing function from: "+res)
        reader.set_pos(saved_pos)
        func = FunctionValue.parse(reader, parent_name, function_table, expected_type)
        return Value(func,func.t, parent_name)
    elif res == "true" or res == "false":
        return Value(BoolValue(res =="true"), "bool", parent_name)
    else:
        print("attempting to parse variable from: "+res)
        reader.set_pos(saved_pos)
        vv = VariableValue.parse(reader)
        return Value(vv, vv.t, parent_name)
class FunctionValue:
    def __init__(self, name: str, args: List["Value"], t: str):
        self.name = name
        self.args = args
        self.t = t
    def construct_types(self, parent, function_table: dict, custom_types: list, program):
        print("\n\n\n\n\n\nconstructing types for function "+self.name)
        if self.name in function_table:
            print("Function "+self.name+" already exists in function table. Getting type information.")
            if self.t == "undefined":
                self.t = function_table[self.name].t
            else:
                assert self.t == function_table[self.name].t, f"Function {self.name} is of type {self.t}, expected {function_table[self.name].t}."
            assert self.t != "undefined", f"Function {self.name} has no type information."
        for arg in self.args:
            if arg.t == "undefined":
                arg.construct_type(parent, function_table, custom_types, program)
        
        i = 0
        for arg, argt in zip(self.args, function_table[self.name].arg_types):
            if arg.t != argt and argt != "undefined":
                raise Exception(f"Argument {arg.value.name} of function {self.name} is of type {arg.t}, expected {argt}.")
            elif argt == "undefined" and arg.t != "undefined":
                function_table[self.name].arg_types[i] = arg.t
            else:
                assert argt != "undefined", f"Argument {arg.value.name} of function {self.name} has no type information."
            i+=1
        
        if self.t == "undefined":
            self.t = get_user_input(f"Type of function {self.name}: ")
            function_table[self.name].t = self.t

            
        
    @staticmethod
    def parse(reader: Reader, parent_name: str, function_table: dict, expected_type = "undefined"):
        print("parsing function")
        name = reader.readuntil("(")
        args = []
        onfirst = True
        print("starting to parse args to function "+name)
        ets = None
        if name in function_table:
            ets = function_table[name].arg_types
        while reader.peek() != ")":
            print("parsing arg "+str(len(args)))
            exp_t = ets[len(args)] if ets else "undefined"
            if not onfirst:
                assert reader.pop() == ",", "function arguments must be separated by commas."
            else:
                onfirst = False
            args.append(Value.parse(reader, parent_name,function_table, exp_t))
        reader.pop()
        if name in function_table:
            return FunctionValue(name, args, function_table[name].t)
        else:
            function_table[name] = Function(name, [a.t for a in args], expected_type)
            return FunctionValue(name, args, expected_type)
class DecimalValue:
    def __init__(self, value: float):
        self.value = value

class IntegerValue:
    def __init__(self, value: int):
        self.value = value

class StringValue:
    def __init__(self, value: str):
        self.value = value
class BoolValue:
    def __init__(self, value: bool):
        self.value = value

class VariableValue:
    def __init__(self, name: str, t: str):
        self.name = name
        self.t = t
    def parse(reader: Reader):
        name = ""
        while reader.peek().isalpha() or reader.peek().isdigit() or reader.peek() == "_" or reader.peek() == ".":
            name += reader.pop()
        return VariableValue(name, "undefined")

class Value:
    def __init__(self, value: Union[FunctionValue, DecimalValue, IntegerValue, StringValue, BoolValue, VariableValue], t: str, parent_name: str):
        self.value: Union[FunctionValue, DecimalValue, IntegerValue, StringValue, BoolValue, VariableValue] = value
        self.t = t
        self.parent_name = parent_name
    
    def is_object_derived(self) -> bool:
        if type(self.value) == FunctionValue:
            return any([arg.is_object_derived() for arg in self.value.args])
        elif type(self.value) == VariableValue:
            return self.value.t not in PRIMITIVES or "." in self.value.name
        return False
    
    def get_object_derived_values(self) -> List["Value"]:
        if not self.is_object_derived():
            return []
        if type(self.value) == FunctionValue:
            ret = []
            for x in [arg for arg in self.value.args if arg.is_object_derived()]:
                ret += x.get_object_derived_values()
            return ret
        elif type(self.value) == VariableValue:
            return [self]

    def parse(reader: Reader, parent_name:str, function_table: dict = {}, expected_type = "undefined"):
        reader.pop()
        reader.pos -=1
        if reader.peek() == "\"":
            reader.pop()
            return Value(StringValue(reader.readuntil_with_whitespace("\"")),"string", parent_name)
        elif reader.peek().isdigit():
            result = ""
            while reader.peek().isdigit():
                result += reader.pop()
            if reader.peek() == ".":
                result += reader.pop()
                while reader.peek().isdigit():
                    result += reader.pop()
                return Value(DecimalValue(float(result)),"float", parent_name)
            else:
                return Value(IntegerValue(int(result)),"int", parent_name)
        else:
            return lookaheadValue(reader, parent_name, function_table, expected_type)
        
    def construct_type(self, parent, function_table: dict, custom_types: list, program):
        poss_types = PRIMITIVES + custom_types
        if type(self.value) == FunctionValue:
                self.value.construct_types(parent, function_table, custom_types, program)
                assert self.value.t != "undefined", f"Function {self.value.name} has no type information."
                self.t = self.value.t
        elif self.t == "undefined":
            if type(self.value) == VariableValue:
                if self.value.name in poss_types:
                    self.t = self.value.name
                else:
                    print(f"{self.value.name} not found in {poss_types}. Looking for field by that name in parent object.")
                    poss_variables = [f.name for f in parent.fields]

                    if("." in self.value.name):
                        obj_name, field_name = self.value.name.split(".")

                        if obj_name in poss_variables:
                            obj_field = [f for f in parent.fields if f.name == obj_name]
                            if obj_field:
                                obj_field = obj_field[0]
                            else:
                                raise Exception(f"Field {obj_name} not found.")
                            
                            if obj_field.t == "undefined":
                                obj_field.resolve_type(parent, function_table, custom_types)
                            assert obj_field.t != "undefined", f"Object {obj_name} has no type information."
                            if obj_field.t in PRIMITIVES:
                                raise Exception(f"Only objects can have fields. {obj_name} is a primitive type.")
                            obj = [o for o in program.objects if o.name == obj_field.t]
                            if obj:
                                obj = obj[0]
                            else:
                                raise Exception(f"Object type {obj_name} not found.")
                            


                            fnames = {f.name:f for f in obj.fields}
                            if field_name in fnames:
                                field = [f for f in obj.fields if f.name == field_name][0]
                                if field.t == "undefined":
                                    field.resolve_type(parent, function_table, custom_types, program)
                                assert field.t != "undefined", f"Field {field_name} has no type information."
                                self.t = field.t
                                self.parent_name = obj.name
                                return
                            else:
                                raise Exception(f"Field {field_name} not found in object {obj_name}.")
                        else:
                            raise Exception(f"Field {obj_name} not found.")
                        
                    
                    if self.value.name in poss_variables:
                        var_field = parent.fields[poss_variables.index(self.value.name)]
                        if var_field.t == "undefined":
                            var_field.resolve_type(parent, function_table, custom_types)
                        assert var_field.t != "undefined", f"Variable {self.value.name} has no type information."
                        self.t = var_field.t
                    else:
                        raise Exception(f"Variable {self.value.name} not found.")
            else:
                raise Exception(f"Value has no type information.")