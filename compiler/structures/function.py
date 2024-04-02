from typing import List

class Function:
    def __init__(self, name: str, t: str, argtypes: List[str]) -> None:
        self.name = name
        self.t = t
        self.argtypes = argtypes