from typing import List

from structures.program import PRIMITIVES
from structures.program import Program
from iostuff.writer import Writer
from structures.field import Field, DerivedField
from structures.object import Object
from structures.expression import VariableExpression


def correct_go_type(t: str) -> str:
    if t.startswith("["):
        return "[]" + correct_go_type(t[t.index("]")+1:])
    

    if t == "float":
        return "float64"
    if t == "int":
        return "int"
    if t == "bool":
        return "bool"
    if t == "string":
        return "string"
    
    #assuming if its not a primitive, its a reference to another object
    return t+"Hydrated"

def correct_go_type_unhydrated(t: str) -> str:
    if t == "float":
        return "float64"
    if t == "int":
        return "int"
    if t == "bool":
        return "bool"
    if t == "string":
        return "string"
    
    #assuming if its not a primitive, its a reference to another object
    return "int"


class Struct:
    def __init__(self, name: str, fields: List[Field], context: Program):
        self.name = name
        self.fields = fields
        self.context = context

    def generate(self, o: Writer):
        o.w(f'type {self.name} struct {{')
        for field in self.fields:
            if field.is_derived() or field.is_list(): # skip derived || list fields
                continue
            else:
                o.w(f'    {field.name} {correct_go_type_unhydrated(field.t)}')
        o.w("ID int")
        o.w(f'}}')

        o.w(f'type {self.name}Hydrated struct {{')
        for field in self.fields:
            o.w(f'    {field.name} {correct_go_type(field.t)}')
        o.w("ID int")
        o.w(f'}}')
        o.w()

        StructHydrator.for_struct(self).generate(o)
        StructCreator.for_struct(self).generate(o)
        StructReader.for_struct(self).generate(o)
        StructUpdater.for_struct(self).generate(o)
        StructDeleter.for_struct(self).generate(o)


    def derived_fields(self):
        return [field for field in self.fields if field.is_derived()]
    
    def stored_fields(self):
        return [field for field in self.fields if not field.is_derived() and not field.is_list()]
    
    def function_derived_fields(self):
        return [field for field in self.fields if field.is_derived() and type(field) == DerivedField and field.expression.is_function()]
    
    @staticmethod
    def for_object(obj: Object) -> 'Struct':
        return Struct(obj.name, obj.fields, obj.context)


class StructHydrator:
    def __init__(self, s: Struct):
        self.s = s

    def get_field_dependencies(self) -> List[VariableExpression]:
        ret = []
        for field in self.s.fields:
            if field.is_derived():
                ret += field.dependencies()
        return ret

    def generate(self, o: Writer):
        #make the list fetchers
        for field in self.s.fields:
            if field.is_list():
                o.w(f'func (obj {self.s.name}) FetchList_{field.name}() ({correct_go_type(field.t)}) {{')
                o.w(f'println("fetching list for {field.name}")')
                o.w(f'    ret := make({correct_go_type(field.t).replace("Hydrated","")},0)')
                if field.t.replace("[]","") in PRIMITIVES:
                    o.w(f'    rows,err := DB.Query(context.TODO(),"SELECT {field.name} FROM {self.s.name}_{field.name} WHERE {self.s.name}_id = $1", obj.ID)')
                else:
                    #this is a reference to another object
                    #we need to join the tables for that query
                    o.w(f'    rows,err := DB.Query(context.TODO(),"SELECT {field.t.replace('[]','')}.* FROM {self.s.name}_{field.name} INNER JOIN {field.t.replace('[]','')} ON {self.s.name}_{field.name}.{field.name} = {field.t.replace('[]','')}.ID WHERE {self.s.name}_{field.name}.{self.s.name}_id = $1", obj.ID)')
                o.w(f'    if err != nil {{')
                o.w(f'        panic(err)')
                o.w(f'        return {correct_go_type(field.t)}{{}}')
                o.w(f'    }}')
                o.w(f'    for rows.Next() {{')
                o.w(f'    println("got a list item for {field.name}")')
                o.w(f'        var temp {correct_go_type(field.t).replace("[]","").replace("Hydrated","")}')
                if field.t.replace("[]","") not in PRIMITIVES:
                    stored_fields = self.s.context.get_object(field.t.replace("[]","")).stored_fields()
                    o.w(f'        err = rows.Scan(' + ", ".join([f'&temp.{field.name}' for field in stored_fields]) + ',&temp.ID)')
                else:
                    o.w(f'        err = rows.Scan(&temp)')
                o.w(f'        if err != nil {{')
                o.w(f'            panic(err)')
                o.w(f'            continue')
                o.w(f'        }}')
                o.w(f'        ret = append(ret,temp)')
                o.w(f'    }}')
                if field.t.replace("[]","") in PRIMITIVES:
                    o.w(f'    return ret')
                else:
                    o.w(f'    real_ret := make({correct_go_type(field.t)},0)')
                    o.w(f'    for _,item := range ret {{')
                    o.w(f'        real_ret = append(real_ret, item.Hydrate())')
                    o.w(f'    }}')
                    o.w(f'    return real_ret')
                o.w('}')
                o.w()
        o.w(f'func (obj {self.s.name}) Hydrate() {self.s.name}Hydrated {{')
        for field in self.s.fields:
            if field.is_list():
                o.w(f'    _L_{field.name} := obj.FetchList_{field.name}()')
        for field in self.s.fields:
            if field.is_object_field():
                o.w(f'    {field.name}, err := Read{field.t}(strconv.Itoa(obj.{field.name}))')
                o.w(f'    if err != nil {{')
                o.w(f'        panic(err)')
                o.w(f'    }}')

        o.w(f'    return {self.s.name}Hydrated{{')
        for field in self.s.fields:
            o.w(f'      {field.name}: {field.get_derivation_string()},')
        o.w(f'        ID: obj.ID,')
        o.w('    }')
        o.w('}')
        o.w()

    @staticmethod
    def for_struct(s: Struct) -> 'StructHydrator':
        return StructHydrator(s)


class StructCreator:
    def __init__(self, s: Struct):
        self.s = s

    def generate(self, o: Writer):
        o.w(f'func (obj {self.s.name}) Create() ({self.s.name}Hydrated, error) {{')

        if len(self.s.stored_fields()) == 0:
            o.w(f'    err := DB.QueryRow(context.TODO(),"INSERT INTO {self.s.name} DEFAULT VALUES RETURNING ID").Scan(&obj.ID)')
            o.w(f'    if err != nil {{')
            o.w(f'        return {self.s.name}Hydrated{{}}, err')
            o.w(f'    }}')
            o.w(f'    return obj.Hydrate(), err')
            o.w('}')
            o.w()
            return
        
        query_str = f'err := DB.QueryRow(context.TODO(),"INSERT INTO {self.s.name} ('
        for field in self.s.stored_fields():
            query_str += f"{field.name}, "
        query_str = query_str[:-2]
        query_str += ") VALUES (" + ", ".join([f"${ind+1}" for ind,_ in enumerate(self.s.stored_fields())]) + ")"
        query_str += ' RETURNING ID"'
        query_str += ", " + ", ".join([f"obj.{field.name}" for field in self.s.stored_fields()])
        query_str += ").Scan(&obj.ID)"
        o.w(f'    {query_str}')
        o.w(f'    if err != nil {{')
        o.w(f'        return {self.s.name}Hydrated{{}}, err')
        o.w(f'    }}')
        o.w(f'    return obj.Hydrate(), err')
        o.w('}')
        o.w()

    @staticmethod
    def for_struct(s: Struct) -> 'StructCreator':
        return StructCreator(s)

class StructUpdater:
    def __init__(self, s: Struct):
        self.s = s

    def generate(self, o: Writer):
        add_list_fields = "".join([f", _LA_{field.name} {field.t if field.t.replace('[]','') in PRIMITIVES else '[]int'}" for field in self.s.fields if field.is_list()])
        delete_list_fields = "".join([f", _LD_{field.name} []int" for field in self.s.fields if field.is_list()])

        o.w(f'func (obj {self.s.name}) Update(id string{add_list_fields}{delete_list_fields}) ({self.s.name}Hydrated,error) {{')

        if len(self.s.stored_fields()) == 0:
            o.w(f'var err error;')
            
        else:
            query_str = f'_,err := DB.Exec(context.TODO(),"UPDATE {self.s.name} SET '
            for ind,field in enumerate(self.s.stored_fields()):
                query_str += f"{field.name} = ${ind+1}, "
            query_str = query_str[:-2]
            query_str += ' WHERE ID = $' + str(len(self.s.stored_fields())+1)
            query_str += '", ' + ", ".join([f"obj.{field.name}" for field in self.s.stored_fields()])
            query_str += ", id)"
            o.w(f'    {query_str}')
            o.w(f'    if err != nil {{')
            o.w(f'        return {self.s.name}Hydrated{{}}, err')
            o.w(f'    }}')
            o.w(f'    obj.ID,err = strconv.Atoi(id)')
            o.w(f'    if err != nil {{')
            o.w(f'        return {self.s.name}Hydrated{{}}, err')
            o.w(f'    }}')

        #update list fields
        for field in self.s.fields:
            if field.is_list():
                #delete all the delete items
                o.w(f'    for _,id := range _LD_{field.name} {{')
                o.w(f'        _,err = DB.Exec(context.TODO(),"DELETE FROM {self.s.name}_{field.name} WHERE {self.s.name}_id = $1 AND {field.name} = $2", obj.ID, id)')
                o.w(f'        if err != nil {{')
                o.w(f'            return {self.s.name}Hydrated{{}}, err')
                o.w(f'        }}')
                o.w(f'    }}')

                #insert all the add items
                o.w(f'    for _,item := range _LA_{field.name} {{')
                o.w(f'        println("running SQL to insert to list: INSERT INTO {self.s.name}_{field.name} ({self.s.name}_id, {field.name}) VALUES ($1, $2)", obj.ID, item)')
                o.w(f'        _,err = DB.Exec(context.TODO(),"INSERT INTO {self.s.name}_{field.name} ({self.s.name}_id, {field.name}) VALUES ($1, $2)", obj.ID, item)')
                o.w(f'        if err != nil {{')
                o.w(f'            return {self.s.name}Hydrated{{}}, err')
                o.w(f'        }}')
                o.w(f'    }}')

                #an update will be a delete followed by an insert, can be sent at the same time
            

        o.w(f'    return obj.Hydrate(), err')
        o.w('}')
        o.w()

    @staticmethod
    def for_struct(s: Struct) -> 'StructUpdater':
        return StructUpdater(s)
    
class StructReader:
    def __init__(self, s: Struct):
        self.s = s

    def generate(self, o: Writer):
        o.w(f'func Read{self.s.name}(id string) ({self.s.name}Hydrated, error) {{')
        if len(self.s.stored_fields()) == 0:
            o.w(f'    int_id,erro := strconv.Atoi(id)')
            o.w(f'    if erro != nil {{')
            o.w(f'        return {self.s.name}Hydrated{{}}, erro')
            o.w(f'    }}')
            o.w(f'    return {self.s.name}Hydrated{{ID: int_id}}, nil')
            o.w('}')
            return
        o.w(f'    var obj {self.s.name}')
        o.w(f'    int_id,erro := strconv.Atoi(id)')
        o.w(f'    if erro != nil {{')
        o.w(f'        return {self.s.name}Hydrated{{}}, erro')
        o.w(f'    }}')
        o.w(f'    obj.ID = int_id')
        query_str = f'err := DB.QueryRow(context.TODO(),"SELECT '
        query_str += ", ".join([field.name for field in self.s.stored_fields()])
        query_str += f' FROM {self.s.name} WHERE ID = $1", id).Scan('
        query_str += ", ".join([f"&obj.{field.name}" for field in self.s.stored_fields()])
        query_str += ')'
        o.w(f'    {query_str}')
        o.w(f'    if err != nil {{')
        o.w(f'        return {self.s.name}Hydrated{{}}, err')
        o.w(f'    }}')
        o.w(f'    return obj.Hydrate(), err')
        o.w('}')
        o.w()

    @staticmethod
    def for_struct(s: Struct) -> 'StructReader':
        return StructReader(s)
    
class StructDeleter:
    def __init__(self, s: Struct):
        self.s = s

    def generate(self, o: Writer):
        o.w(f'func Delete{self.s.name}(id string) error {{')
        o.w(f'    _, err := DB.Exec(context.TODO(),"DELETE FROM {self.s.name} WHERE ID = $1", id)')
        o.w(f'    if err != nil {{')
        o.w(f'        return err')
        o.w(f'    }}')
        for field in self.s.fields:
            if field.is_list():
                o.w(f'    _, err = DB.Exec(context.TODO(),"DELETE FROM {self.s.name}_{field.name} WHERE {self.s.name}_id = $1", id)')
                o.w(f'    if err != nil {{')
                o.w(f'        return err')
                o.w(f'    }}')
        o.w(f'    return err')
        o.w('}')

    @staticmethod
    def for_struct(s: Struct) -> 'StructDeleter':
        return StructDeleter(s)