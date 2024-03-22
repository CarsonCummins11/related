from typing import List

class Function:
    def __init__(self, name: str, arg_types: List[str], t: str, available: bool = False):
        self.name = name
        self.arg_types = arg_types
        self.t = t
        self.available = available
