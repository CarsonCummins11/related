import parser.program
import parser.field
import parser.value
from generator.writer import Writer

def correct_type(t: str):
        if t == "float":
            return "float64"
        return t


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

    def get_field_derivation_string(self,field: parser.field.Field) -> str:
        assert field.derived, f"Field {field.name} is not derived"
        return self.get_value_derivation_string(field.derived)

    def get_value_derivation_string(self,val: parser.value.Value) -> str:
        val = val.value
        if type(val) == parser.value.DecimalValue:
            return f"{val.value}"
        elif type(val) == parser.value.IntegerValue:
            return f"{val.value}"
        elif type(val) == parser.value.StringValue:
            return f'"{val.value}"'
        elif type(val) == parser.value.BoolValue:
            return f"{val.value}".lower()
        
        ret = ""
        if type(val) == parser.value.FunctionValue:
            ret += f"derivers.{val.name}("
            for arg in val.args:
                ret += self.get_value_derivation_string(arg) + ", "
            ret = ret[:-2]
            ret += ")"
        elif type(val) == parser.value.VariableValue:
            if val.name in self.data_fields:
                ret += f"obj.{val.name}"
            elif val.name in self.derived_fields:
                #TODO: make it so that this uses a cached calculation, not recalculating for each hydration
                ret += self.get_field_derivation_string(self.derived_fields[val.name])
        else:
            raise Exception(f"Unknown value type {type(val)}")
        
        return ret

    def write_create(self, o: Writer):
        o.w(f"func Create{self.name}(obj {self.name}) ({self.name}Hydrated, error) {{")
        o.w(f"    ret_obj := hydrate{self.name}(obj)")
        o.w(f"    return ret_obj, nil")
        o.w("}")
        o.w("")

    def write_read(self, o: Writer):
        o.w(f"func Read{self.name}(id string) ({self.name}Hydrated, error) {{")
        o.w(f"    //TODO: Implement this")
        o.w(f"    return {self.name}Hydrated{{}}, nil")
        o.w("}")
        o.w("")
    
    def write_update(self, o: Writer):
        o.w(f"func Update{self.name}(obj {self.name}) ({self.name}Hydrated, error) {{")
        o.w(f"    ret_obj := hydrate{self.name}(obj)")
        o.w(f"    return ret_obj, nil")
        o.w("}")
        o.w("")

    def write_delete(self, o: Writer):
        o.w(f"func Delete{self.name}(id string) error {{")
        o.w(f"    //TODO: Implement this")
        o.w(f"    return nil")
        o.w("}")
        o.w("")

    def write_hydrate(self, o: Writer):
        o.w(f"func hydrate{self.name}(obj {self.name}) {self.name}Hydrated {{")
        o.w(f"    new_obj := {self.name}Hydrated{{}}")
        for field in self.data_fields.values():
            o.w(f"    new_obj.{field.name} = obj.{field.name}")
        for field in self.derived_fields.values():
            o.w(f"    new_obj.{field.name} = "+self.get_field_derivation_string(field))
        o.w(f"    return new_obj")
        o.w("}")
        o.w("")


    def generate(self, o: Writer):
        cur_file = o.current_file
        o.use_file(f"objects/{self.name}.go")
        o.w(f"package objects")
        o.w(f"")

        o.w("type " + self.name + " struct {")
        for field in self.data_fields.values():
            o.w(f"    {field.name} {correct_type(field.t)}")
        o.w("    ID string")
        o.w("}")
        o.w("")

        o.w(f"type {self.name}Hydrated struct {{")
        for field in self.data_fields.values():
            o.w(f"    {field.name} {correct_type(field.t)}")
        for field in self.derived_fields.values():
            o.w(f"    {field.name} {correct_type(field.t)}")
        o.w("    ID string")
        o.w("}")
        o.w("")

        self.write_hydrate(o)
        self.write_create(o)
        self.write_read(o)
        self.write_update(o)
        self.write_delete(o)

        o.use_file(cur_file)
