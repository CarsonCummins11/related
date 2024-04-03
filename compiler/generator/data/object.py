import parser.program
import parser.field
import parser.value
from parser.config import PRIMITIVES
from compiler.iostuff.writer import Writer
from typing import List, Dict, Set, Tuple

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

def make_field_name(obj:parser.program.Object,v: parser.value.Value) -> str:
    fieldname = v.name
    objname = v.t+"."
    if "." in v.name:
        objname, fieldname = v.name.split(".")
        objname = obj.type_of(objname)+"."
    return objname+fieldname

def make_sql_query(obj: parser.program.Object, fields: List[parser.program.Field] = []) -> Tuple[str, List[str]]:
    if not fields:
        fields = obj.fields
    table_columns: Dict[str, (str,Set[str])] = {}
    for field in fields:
        if field.is_object_derived():
            for v in field.derived.get_object_derived_values():
                objname = v.t
                fieldname = v.name
                if "." in v.name:
                    objname, fieldname = v.name.split(".")
                    objname = obj.type_of(objname)
                joinstr = f"INNER JOIN {objname} ON {obj.name}.{objname} = {objname}.ID"
                if objname not in table_columns:
                    table_columns[objname] = (joinstr,set())
                table_columns[objname][1].add(fieldname)
    ret = "SELECT "
    needed_tables = table_columns.keys()
    selected_fields = []
    for f in needed_tables:
        for field in table_columns[f][1]:
            ret += f"{f}.{field}, "
            selected_fields.append(f"retr_{f}_{field}")
    ret = ret[:-2]
    ret += f" FROM {obj.name} "
    for f in needed_tables:
        ret += table_columns[f][0]
    
    return ret, selected_fields



class Object:
    def __init__(self, parser_object: parser.program.Object, program: parser.program.Program):
        self.name = parser_object.name
        self.derived_fields:List[parser.field.Field] = [x for x in parser_object.fields if x.derived]
        self.data_fields: List[parser.field.Field] = [x for x in parser_object.fields if not x.derived]
        self.program = program

    def object_derived_fields(self):
        return [field for field in self.derived_fields if field.is_object_derived()]
            

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
        
        assert type(val) in [parser.value.FunctionValue, parser.value.VariableValue], f"Unknown value type {type(val)}"
        ret = ""
        if type(val) == parser.value.FunctionValue:
            ret += f"derived.{val.name}("
            for arg in val.args:
                ret += self.get_value_derivation_string(arg) + ", "
            ret = ret[:-2]
            ret += ")"
        elif type(val) == parser.value.VariableValue:
            if val.name in [x.name for x in self.data_fields]:
                ret += f"obj.{val.name}"
            elif val.name in [x.name for x in self.derived_fields]:
                #TODO: make it so that this can use a cached calculation, not recalculating for each hydration
                ret += self.get_field_derivation_string(val) + ","
            elif "." in val.name:
                #this is a reference to another object
                #we've already written the query to store the reference in "retr_<valname>"
                ret+= f"retr_{val.name.replace('.','_')},"
            else:
                assert False, f"Unknown variable {val.name}"
        else:
            raise Exception(f"Unknown value type {type(val)}")
        
        return ret

    def write_create(self, o: Writer):
        o.w(f"func Create{self.name}(obj {self.name}) ({self.name}Hydrated, error) {{")
        o.w(f"    ret_obj,err := hydrate{self.name}(obj)")
        o.w(f"    if err != nil {{")
        o.w(f"        return {self.name}Hydrated{{}}, err")
        o.w(f"    }}")
        query = f"INSERT INTO {self.name} ("
        for field in self.data_fields:
            query += f"{field.name},"
        for field in self.derived_fields:
            query += f"{field.name},"
        query = query[:-1]
        query += ") VALUES ("
        for i,field in enumerate(self.data_fields):
            query+=f"${i+1},"
        query = query[:-1]
        query += ") RETURNING ID"
        o.w(f"    database.DB.QueryRow(context.Background(), \"{query}\",")
        for field in self.data_fields:
            o.w(f"        ret_obj.{field.name},")
        o.w(f"    ).Scan(&ret_obj.ID)")
        o.w(f"    return ret_obj, nil")
        o.w("}")
        o.w("")

    def write_read(self, o: Writer):
        o.w(f"func Read{self.name}(id string) ({self.name}Hydrated, error) {{")
        o.w(f"    var obj {self.name}")
        o.w(f"    err := database.DB.QueryRow(context.Background(), \"SELECT * FROM {self.name} WHERE ID = $1\", id).Scan(")
        for field in self.data_fields:
            o.w(f"        &obj.{field.name},")
        o.w(f"        &obj.ID,")
        o.w(f"    )")
        o.w(f"    if err != nil {{")
        o.w(f"        return {self.name}Hydrated{{}}, err")
        o.w(f"    }}")
        o.w(f"    ret_obj,err := hydrate{self.name}(obj)")
        o.w(f"    if err != nil {{")
        o.w(f"        return {self.name}Hydrated{{}}, err")
        o.w(f"    }}")
        o.w(f"    return obj, nil")
        o.w("}")
        o.w("")
    
    def write_update(self, o: Writer):
        o.w(f"func Update{self.name}(obj {self.name}) ({self.name}Hydrated, error) {{")
        update_query = f"    err:= database.DB.QueryRow(context.Background(), \"UPDATE {self.name} SET "
        ind = 1
        for field in self.data_fields:
            update_query+=f"{field.name} = ${ind},"
            ind+=1
        update_query = update_query[:-1]
        update_query += " WHERE ID = $"+str(ind)+"\","
        for field in self.data_fields:
            update_query+=f"obj.{field.name},"
        update_query+=f"obj.ID)"
        o.w(update_query)
        o.w(f"    if err != nil {{")
        o.w(f"        return {self.name}Hydrated{{}}, err")
        o.w(f"    }}")
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
        o.w(f"func hydrate{self.name}(obj {self.name}) ({self.name}Hydrated,error) {{")
        o.w(f"    new_obj := {self.name}Hydrated{{}}")
        #query the db for the info we need for hydration
        q, selected_fields = make_sql_query(self, self.data_fields+self.derived_fields)
        query = f"err := database.DB.Query(context.Background(), \"{q} WHERE {self.name}.ID = $1\", obj.ID).Scan("
        for field in selected_fields:
            query += f"&retr_.{field},"
        for field in self.data_fields:
            o.w(f"    new_obj.{field.name} = obj.{field.name}")
        for field in self.derived_fields:
            o.w(f"    new_obj.{field.name} = "+self.get_field_derivation_string(field))
        o.w(f"    new_obj.ID = obj.ID")
        o.w(f"    return new_obj")
        o.w("}")
        o.w("")


    def generate(self, o: Writer):
        cur_file = o.current_file
        o.use_file(f"objects/{self.name}.go")
        o.w(f"package objects")
        o.w(f"")
        non_constant_derived = [field for field in self.derived_fields if type(field.derived.value) == parser.value.FunctionValue]
        o.w(f"import (")
        if len(non_constant_derived) > 0:
            o.w(f"    \"{o.package()}/derived\"")
        o.w('    "context"')
        o.w(f'   "{o.package()}/database"')    
        o.w(f")")
        o.w(f"")

        o.w("type " + self.name + " struct {")
        for field in self.data_fields:
            o.w(f"    {field.name} {correct_type(field.t)}")
        o.w("    ID string")
        o.w("}")
        o.w("")

        o.w(f"type {self.name}Hydrated struct {{")
        for field in self.data_fields:
            o.w(f"    {field.name} {correct_type(field.t)}")
        for field in self.derived_fields:
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
        for field in self.data_fields:
            ret += f"    {field.name} {correct_type_sql(field.t)} NOT NULL,\n"
        for field in self.derived_fields:
            ret += f"    {field.name} {correct_type_sql(field.t)} NOT NULL,\n"
        ret += "    ID SERIAL PRIMARY KEY\n"
        ret += ");"
        o.w(ret)
        return ret