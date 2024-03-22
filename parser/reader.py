class Reader:
    def __init__(self, src: str, pos: int = 0):
        self.src = src
        self.pos = pos
    
    def pop(self):
        while self.pos < len(self.src) and self.src[self.pos] in [" ", "\n", "\t"]:
            self.pos += 1
        self.pos += 1
        if self.pos-1 >= len(self.src):
            raise Exception("End of file reached unexpectedly.")
        return self.src[self.pos - 1]
    
    def readuntil_with_whitespace(self, c: str):
        result = ""
        while self.peek() != c:
            result += self.peek()
            self.pos += 1
        self.pop()
        return result

    def readuntil(self, c: str):
        result = ""
        while self.peek_pop_result() not in  [c,""]:
            nextchar = self.pop()
            result += nextchar
        self.pop()
        return result
    def peek_pop_result(self):
        init = self.pos
        while self.pos < len(self.src) and self.src[self.pos] in [" ", "\n", "\t"]:
            self.pos += 1
        self.pos += 1
        if self.pos >= len(self.src):
            return ""
        r = self.src[self.pos - 1]
        self.pos = init
        return r
    def reset(self):
        self.pos = 0
    
    def can_read(self):
        return self.pos < len(self.src)
    
    def peek(self):
        return self.src[self.pos]

    def set_pos(self, pos: int):
        self.pos = pos
    
    def get_pos(self):
        return self.pos

def get_user_input(prompt: str):
    return input(prompt)