from parser.program import Program


def run(src: str):
    Program(src).parse()
    




if __name__ == '__main__':
    run(open('test.rltd').read())