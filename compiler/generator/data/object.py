import parser.program
import parser.field
import parser.value
from parser.config import PRIMITIVES
from generator.writer import Writer

def correct_type(t: str):
        if t == "float":
            return "float64"
        return t

def correct_type_sql(t: str):
    if t == "float":
        return "REAL"
    if t=="string":
        return "TEXT"
    if t=="int":
        return "INTEGER"
    if t=="bool":
        return "BOOLEAN"
    
    if t not in PRIMITIVES:
        #t is an object, we we link with id
        return "TEXT"

    assert False, f"Unknown type {t}"

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
        query = f"INSERT INTO {self.name} ("
        for field in self.data_fields.values():
            query += f"d_{field.name},"
        for field in self.derived_fields.values():
            query += f"d_{field.name},"
        query = query[:-1]
        query += ") VALUES ("
        for i,field in enumerate(self.data_fields.values()):
            query+=f"${i},"
        for i,field in enumerate(self.derived_fields.values()):
            query+=f"${i+len(self.data_fields)},"
        query = query[:-1]
        query += ") RETURNING ID"
        o.w(f"    the_id, err := database.DB.Exec(context.Background(), \"{query}\",")
        for field in self.data_fields.values():
            o.w(f"        ret_obj.{field.name},")
        for field in self.derived_fields.values():
            o.w(f"        ret_obj.{field.name},")
        o.w(f"    )")
        o.w(f"    if err != nil {{")
        o.w(f"        return {self.name}Hydrated{{}}, err")
        o.w(f"    }}")
        o.w(f"    ret_obj.ID = the_id.String()")
        o.w(f"    return ret_obj, nil")
        o.w("}")
        o.w("")

    def write_read(self, o: Writer):
        o.w(f"func Read{self.name}(id string) ({self.name}Hydrated, error) {{")
        o.w(f"    var obj {self.name}Hydrated")
        o.w(f"    err := database.DB.QueryRow(context.Background(), \"SELECT * FROM {self.name} WHERE ID = $1\", id).Scan(")
        for field in self.data_fields.values():
            o.w(f"        &obj.{field.name},")
        for field in self.derived_fields.values():
            o.w(f"        &obj.{field.name},")
        o.w(f"        &obj.ID,")
        o.w(f"    )")
        o.w(f"    if err != nil {{")
        o.w(f"        return {self.name}Hydrated{{}}, err")
        o.w(f"    }}")
        o.w(f"    return obj, nil")
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
        o.w(f"    database.DB.Exec(context.Background(), \"DELETE FROM {self.name} WHERE ID = $1\", id)")
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
        non_constant_derived = [field for field in self.derived_fields.values() if type(field.derived.value) == parser.value.FunctionValue]
        o.w(f"import (")
        if len(non_constant_derived) > 0:
            o.w(f"    \"{o.package()}/derivers\"")
        o.w(f"    \"context\"")
        o.w(f'      "{o.package()}/database"')    
        o.w(f")")
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


    def generate_schema(self, o: Writer):
        ret = f"CREATE TABLE {self.name} (\n"
        for field in self.data_fields.values():
            ret += f"    d_{field.name} {correct_type_sql(field.t)} NOT NULL,\n"
        for field in self.derived_fields.values():
            ret += f"    d_{field.name} {correct_type_sql(field.t)} NOT NULL,\n"
        ret += "    ID SERIAL PRIMARY KEY\n"
        ret += ");"
        o.w(ret)
        return ret