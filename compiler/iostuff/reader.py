import re
class Reader:
    def __init__(self, src: str, pos: int = 0):
        self.src = src
        self.pos = pos
    
    def pop(self):
        ret = self.src[self.pos]
        self.pos += 1
        return ret

    def readuntil(self, c: str):
        assert len(c) == 1, "Can only readuntil a single character"
        result = ""
        while self.peek() != c:
            nextchar = self.pop()
            result += nextchar
        self.pop()
        return result
    
    def reset(self):
        self.pos = 0
    
    def can_read(self):
        return self.pos < len(self.src)
    
    def peek(self):
        if self.pos >= len(self.src):
            return None
        return self.src[self.pos]

    def set_pos(self, pos: int):
        self.pos = pos
    
    def get_pos(self):
        return self.pos
    
    def pop_whitespace(self):
        while self.peek() in [" ", "\n", "\t","\r"]:
            self.pop()

    def read_while_matching(self, regex):
        result = ""
        while re.match(regex, self.peek()):
            result += self.pop()
        return result