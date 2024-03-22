from parser.program import Program
from generator.writer import Writer
from generator.api.api import API

def run(src: str):
    p = Program(src)
    p.parse()
    api = API("tt", p.objects)
    w = Writer("tt")
    api.generate(w)
    w.flush()
    




if __name__ == '__main__':
    run(open('test.rltd').read())