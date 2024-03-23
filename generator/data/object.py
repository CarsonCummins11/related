import parser.program
from generator.writer import Writer

class Object:
    def __init__(self, parser_object: parser.program.Object):
        self.name = parser_object.name
        self.data_fields = {}
        self.derived_fields = {}
        for field in parser_object.fields:
            if field.derived:
                self.derived_fields[field.name] = field
            else:
                self.data_fields[field.name] = field
    
    def write_create(self, o: Writer):
        o.w(f"func Create{self.name}(obj {self.name}) ({self.name}, error) {{")
        o.w(f"    //TODO: Implement this")
        o.w(f"    return obj, nil")
        o.w("}")
        o.w("")

    def write_read(self, o: Writer):
        o.w(f"func Read{self.name}(id string) ({self.name}, error) {{")
        o.w(f"    //TODO: Implement this")
        o.w(f"    return {self.name}{{}}, nil")
        o.w("}")
        o.w("")
    
    def write_update(self, o: Writer):
        o.w(f"func Update{self.name}(obj {self.name}) ({self.name}, error) {{")
        o.w(f"    //TODO: Implement this")
        o.w(f"    return obj, nil")
        o.w("}")
        o.w("")

    def write_delete(self, o: Writer):
        o.w(f"func Delete{self.name}(id string) error {{")
        o.w(f"    //TODO: Implement this")
        o.w(f"    return nil")
        o.w("}")
        o.w("")


    def generate(self, o: Writer):
        cur_file = o.current_file
        o.use_file(f"objects/{self.name}.go")
        o.w(f"package objects")
        o.w(f"")

        o.w("type " + self.name + " struct {")
        for field in self.data_fields.values():
            o.w(f"    {field.name} {field.t}")
        o.w("    ID string")
        o.w("}")
        o.w("")

        o.use_file(cur_file)
