from structures.expression import BooleanExpression, TRUE_EXPRESSION
from iostuff.reader import Reader
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from structures.program import Program


class Governance:
    def __init__(self, context: "Program", permissions: Dict[str,BooleanExpression] = {}):
        self.context = context
        self.permissions: Dict[str,BooleanExpression] = permissions
    
    def add_permission(self, permissions: str, rule: BooleanExpression):
        for c in permissions:
            print(f"adding permission {c}, {rule.get_executable_str()}")
            assert c in "CRUD", f"Invalid permission {c}"
            self.permissions[c] = rule

    def get_permission(self, permission: str) -> BooleanExpression:
        return self.permissions.get(permission, TRUE_EXPRESSION)

    @staticmethod
    def parse(reader: Reader, obj: str ,context: "Program") -> "Governance":
        print("parsing governance")
        ret = Governance(context)
        reader.pop_whitespace()
        assert reader.pop() == "-", "Governance expression needs to start with hyphen" #pop the "-"
        reader.pop_whitespace()
        while not reader.peek() == ";":
            permissions = reader.read_while_matching("[CRUD]")
            assert permissions != "", "Expected permissions"
            print(f"found permissions {permissions}")
            reader.pop_whitespace()
            assert reader.pop() == ":", "Expected :"
            reader.pop_whitespace()
            ret.add_permission(permissions,BooleanExpression.parse(reader,obj, context))
            reader.pop_whitespace()
        
        assert reader.pop() == ";", "Governance expression must end with ;" # pop the ;
        print("parsed governance rule !!")
        return ret




