import parser.function
from generator.writer import Writer
from typing import Dict, List

class Derivers:
    def __init__(self, function_table: Dict[str, parser.function.Function]):
        self.function_table = function_table

    def generate(self, o: Writer):
        o.use_file(f"derivers/derivers.go")
        o.w(f"package derivers")
        o.w(f"")
        for name, function in self.function_table.items():
            if not function.available:
                function.body = "//TODO: implement this\nreturn "
                if function.t == "int":
                    function.body += "0"
                elif function.t == "string":
                    function.body += "\"\""
                elif function.t == "bool":
                    function.body += "false"
                else:
                    function.body += "nil"
                function.arg_names = [f"arg{i}" for i in range(len(function.arg_types))]
            Deriver(name, function.arg_types, function.t, function.body, function.arg_names).generate(o)
                
class Deriver:
    def __init__(self, name: str, arg_types: List[str], return_type: str, body: str, arg_names: List[str]):
        self.name = name
        self.arg_types = arg_types
        self.arg_names = arg_names
        self.return_type = return_type
        self.body = body

    def generate(self, o: Writer):
        argout = []
        for name, type in zip(self.arg_names, self.arg_types):
            argout.append(f"{name} {type}")
        o.w(f"func {self.name}(" + ",".join(argout) +f") {self.return_type} {{")
        o.w(f"    {self.body}")
        o.w(f"}}")