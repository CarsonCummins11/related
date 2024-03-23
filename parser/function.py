from typing import List

class Function:
    def __init__(self, name: str, arg_types: List[str], t: str, available: bool = False, body: str = "", arg_names: List[str] = []):
        self.name = name
        self.arg_types = arg_types
        self.arg_names = arg_names
        self.t = t
        self.available = available
        self.body = body
