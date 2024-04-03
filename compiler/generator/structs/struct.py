from typing import List

from iostuff.writer import Writer
from structures.field import Field

class Struct:
    def __init__(self, name: str, fields: List[Field]):
        self.name = name
        self.fields = fields

    def generate(self, o: Writer):
        o.w(f'type {self.name} struct {{')
        for field in self.fields:
            if field.is_derived(): # skip derived fields for unhydrated structs
                continue
            o.w(f'    {field.name} {field.t}')
        o.w("ID int")
        o.w(f'}}')

        o.w(f'type {self.name}Hydrated struct {{')
        for field in self.fields:
            o.w(f'    {field.name} {field.t}')
        o.w("ID int")
        o.w(f'}}')

        StructCreator.for_struct(self).generate(o)
        StructReader.for_struct(self).generate(o)
        StructUpdater.for_struct(self).generate(o)
        StructDeleter.for_struct(self).generate(o)

    def derived_fields(self):
        return [field for field in self.fields if field.is_derived()]
    
    def stored_fields(self):
        return [field for field in self.fields if not field.is_derived()]


class StructCreator:
    def __init__(self, s: Struct):
        self.s = s

    def generate(self, o: Writer):
        o.w(f'func Create{self.s.name}(obj {self.s.name}) ({self.s.name}Hydrated, error) {{')
        o.w(f'    _, err := db.Exec("INSERT INTO {self.s.name} ({", ".join({field.name for field in self.s.stored_fields()})}) VALUES ({", ".join({f"?" for _ in self.s.stored_fields()})})", {", ".join({f"obj.{field.name}" for field in self.s.stored_fields()})})')
        o.w(f'    return Hydrate{self.s.name}(obj), err')
        o.w('}')
        o.w()

    @staticmethod
    def for_struct(s: Struct) -> 'StructCreator':
        return StructCreator(s)

class StructUpdater:
    def __init__(self, s: Struct):
        self.s = s

    def generate(self, o: Writer):
        o.w(f'func Update{self.s.name}(obj {self.s.name}) ({self.s.name}Hydrated,error) {{')
        o.w(f'    _, err := db.Exec("UPDATE {self.s.name} SET {", ".join({f"{field.name} = ?" for field in self.s.stored_fields() })} WHERE ID = ?", {", ".join({f"obj.{field.name}" for field in self.s.stored_fields()})}, obj.ID)')
        o.w(f'    return Hydrate{self.s.name}(obj), err')
        o.w('}')
        o.w()

    @staticmethod
    def for_struct(s: Struct) -> 'StructUpdater':
        return StructUpdater(s)
    
class StructReader:
    def __init__(self, s: Struct):
        self.s = s

    def generate(self, o: Writer):
        o.w(f'func Read{self.s.name}(id int) ({self.s.name}Hydrated, error) {{')
        o.w(f'    var obj {self.s.name}Hydrated')
        o.w(f'    err := db.QueryRow("SELECT {", ".join({field.name for field in self.s.stored_fields()})}, " FROM {self.s.name} WHERE ID = ?", id).Scan({", ".join({f"&obj.{field.name}" for field in self.s.stored_fields()})})')
        o.w(f'    return obj, err')
        o.w('}')
        o.w()

    @staticmethod
    def for_struct(s: Struct) -> 'StructReader':
        return StructReader(s)
    
class StructDeleter:
    def __init__(self, s: Struct):
        self.s = s

    def generate(self, o: Writer):
        o.w(f'func Delete{self.s.name}(id int) error {{')
        o.w(f'    _, err := db.Exec("DELETE FROM {self.s.name} WHERE ID = ?", id)')
        o.w(f'    return err')
        o.w('}')

    @staticmethod
    def for_struct(s: Struct) -> 'StructDeleter':
        return StructDeleter(s)