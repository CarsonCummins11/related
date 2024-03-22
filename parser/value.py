from typing import List, Union
from parser.function import Function
from parser.reader import Reader, get_user_input
from parser.config import PRIMITIVES


def lookaheadValue(reader: Reader, function_table: dict = {}, expected_type = "undefined"):
    saved_pos = reader.get_pos()
    res = reader.pop()
    while reader.peek().isalpha() or reader.peek().isdigit() or reader.peek() == "_":
        res +=reader.pop()
    assert res, f"Expected a value at {saved_pos}, {reader.peek()}, got nothing."
    if reader.peek() == "(":
        print("parsing function from: "+res)
        reader.set_pos(saved_pos)
        func = FunctionValue.parse(reader, function_table, expected_type)
        return Value(func,func.t)
    elif res == "true" or res == "false":
        return Value(BoolValue(res =="true"), "bool")
    else:
        print("attempting to parse variable from: "+res)
        reader.set_pos(saved_pos)
        vv = VariableValue.parse(reader)
        return Value(vv, vv.t)
class FunctionValue:
    def __init__(self, name: str, args: List["Value"], t: str):
        self.name = name
        self.args = args
        self.t = t
    def construct_types(self, parent, function_table: dict, custom_types: list):
        if self.name in function_table:
            print("Function "+self.name+" already exists in function table. Getting type information.")
            if self.t == "undefined":
                self.t = function_table[self.name].t
            else:
                assert self.t == function_table[self.name].t, f"Function {self.name} is of type {self.t}, expected {function_table[self.name].t}."
        for arg in self.args:
            if arg.t == "undefined":
                arg.construct_type(parent, function_table, custom_types)
        
        i = 0
        for arg, argt in zip(self.args, function_table[self.name].arg_types):
            if arg.t != argt and argt != "undefined":
                raise Exception(f"Argument {arg.value.name} of function {self.name} is of type {arg.t}, expected {argt}.")
            elif argt == "undefined" and arg.t != "undefined":
                function_table[self.name].arg_types[i] = arg.t
            i+=1
        
        if self.t == "undefined":
            self.t = get_user_input(f"Type of function {self.name}: ")
            function_table[self.name].t = self.t

            
        
    @staticmethod
    def parse(reader: Reader, function_table: dict, expected_type = "undefined"):
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
            args.append(Value.parse(reader, function_table, exp_t))
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
        while reader.peek().isalpha() or reader.peek().isdigit() or reader.peek() == "_":
            name += reader.pop()
        return VariableValue(name, "undefined")

class Value:
    def __init__(self, value: Union[FunctionValue, DecimalValue, IntegerValue, StringValue, BoolValue, VariableValue], t: str):
        self.value = value
        self.t = t
    def parse(reader: Reader, function_table: dict = {}, expected_type = "undefined"):
        reader.pop()
        reader.pos -=1
        if reader.peek() == "\"":
            reader.pop()
            return Value(StringValue(reader.readuntil_with_whitespace("\"")),"string")
        elif reader.peek().isdigit():
            result = ""
            while reader.peek().isdigit():
                result += reader.pop()
            if reader.peek() == ".":
                result += reader.pop()
                while reader.peek().isdigit():
                    result += reader.pop()
                return Value(DecimalValue(float(result)),"float")
            else:
                return Value(IntegerValue(int(result)),"int")
        else:
            return lookaheadValue(reader, function_table, expected_type)
        
    def construct_type(self, parent, function_table: dict, custom_types: list):
        poss_types = PRIMITIVES + custom_types

        if self.t == "undefined":
            if type(self.value) == FunctionValue:
                self.value.construct_types(parent, function_table, custom_types)
                self.t = self.value.t
            elif type(self.value) == VariableValue:
                if self.value.name in poss_types:
                    self.t = self.value.name
                else:
                    poss_variables = [f.name for f in parent.fields]
                    if self.value.name in poss_variables:
                        var_field = parent.fields[poss_variables.index(self.value.name)]
                        if var_field.t == "undefined":
                            var_field.resolve_type(parent, function_table, custom_types)
                        self.t = var_field.t
                    else:
                        raise Exception(f"Variable {self.value.name} not found.")
            else:
                raise Exception(f"Value has no type information.")