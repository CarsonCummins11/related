from typing import List

from iostuff.writer import Writer
from structures.field import Field
from structures.object import Object
from structures.expression import VariableExpression


def correct_go_type(t: str) -> str:
    if t == "float":
        return "float64"
    return t


class Struct:
    def __init__(self, name: str, fields: List[Field]):
        self.name = name
        self.fields = fields

    def generate(self, o: Writer):
        o.w(f'type {self.name} struct {{')
        for field in self.fields:
            if field.is_derived(): # skip derived fields for unhydrated structs
                continue
            o.w(f'    {field.name} {correct_go_type(field.t)}')
        o.w("ID int")
        o.w(f'}}')

        o.w(f'type {self.name}Hydrated struct {{')
        for field in self.fields:
            o.w(f'    {field.name} {correct_go_type(field.t)}')
        o.w("ID int")
        o.w(f'}}')

        StructHydrator.for_struct(self).generate(o)
        StructCreator.for_struct(self).generate(o)
        StructReader.for_struct(self).generate(o)
        StructUpdater.for_struct(self).generate(o)
        StructDeleter.for_struct(self).generate(o)


    def derived_fields(self):
        return [field for field in self.fields if field.is_derived()]
    
    def stored_fields(self):
        return [field for field in self.fields if not field.is_derived()]
    
    @staticmethod
    def for_object(obj: Object) -> 'Struct':
        return Struct(obj.name, obj.fields)


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
        o.w(f'func (obj {self.s.name}) Hydrate() {self.s.name}Hydrated {{')
        o.w(f'    return {self.s.name}Hydrated{{')
        for field in self.s.fields:
            if field.is_derived():
                continue
            o.w(f'        {field.name}: obj.{field.name},')
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
        o.w(f'    _, err := DB.Exec(context.TODO(),"INSERT INTO {self.s.name} ({", ".join({field.name for field in self.s.stored_fields()})}) VALUES ({", ".join({f"?" for _ in self.s.stored_fields()})})", {", ".join({f"obj.{field.name}" for field in self.s.stored_fields()})})')
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
        o.w(f'func (obj {self.s.name}) Update(id string) ({self.s.name}Hydrated,error) {{')
        o.w(f'    _, err := DB.Exec(context.TODO(),"UPDATE {self.s.name} SET {", ".join({f"{field.name} = ?" for field in self.s.stored_fields() })} WHERE ID = ?", {", ".join({f"obj.{field.name}" for field in self.s.stored_fields()})}, id)')
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
        o.w(f'    var obj {self.s.name}')
        o.w(f'    err := DB.QueryRow(context.TODO(),"SELECT {", ".join({field.name for field in self.s.stored_fields()})}, FROM {self.s.name} WHERE ID = ?", id).Scan({", ".join({f"&obj.{field.name}" for field in self.s.stored_fields()})})')
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
        o.w(f'    _, err := DB.Exec(context.TODO(),"DELETE FROM {self.s.name} WHERE ID = ?", id)')
        o.w(f'    return err')
        o.w('}')

    @staticmethod
    def for_struct(s: Struct) -> 'StructDeleter':
        return StructDeleter(s)