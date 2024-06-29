from structures.program import Program
from structures.expression import BooleanExpression
from iostuff.reader import Reader
from typing import Dict

class Governance:
    def __init__(self, context: "Program", permissions: Dict[str,BooleanExpression] = {}):
        self.context = context
        self.permissions: Dict[str,BooleanExpression] = permissions
    
    def add_permission(self, permissions: str, rule: BooleanExpression):
        for c in permissions:
            assert c in "CRUD", f"Invalid permission {c}"
            self.permissions[c] = rule

    def get_permission(self, permission: str) -> BooleanExpression:
        return self.permissions.get(permission, BooleanExpression(True))

    @staticmethod
    def parse(reader: Reader, context: "Program") -> "Governance":
        ret = Governance(context)
        reader.pop() #pop the "-"
        reader.pop_whitespace()
        while not reader.peek() == ";":
            permissions = reader.read_while_matching("[CRUD]")
            assert permissions != "", "Expected permissions"
            reader.pop_whitespace()
            assert reader.pop() == ":", "Expected :"
            reader.pop_whitespace()
            assert reader.pop() == "(", "Expected ("
            ret.add_permission(permissions,BooleanExpression.parse(reader, context))
            reader.pop_whitespace()
            assert reader.pop() == ")", "Expected )"
            reader.pop_whitespace()
        
        return ret




