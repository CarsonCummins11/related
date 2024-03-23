from parser.program import Program
from generator.writer import Writer
from generator.api.api import API
from generator.data.data_platform import DataPlatform
from generator.data.derivers import Derivers
import os

def run(src: str, trg: str):
    p = Program(src)
    p.parse()
    api = API(trg, p.objects)
    w = Writer(trg)
    api.generate(w)
    data = DataPlatform(p.objects)
    data.generate(w)
    derivers = Derivers(p.function_table)
    derivers.generate(w)
    w.flush()
    #create go mod/sum files
    os.system(f"cd {trg} && go mod init {trg}")
    os.system(f"cd {trg} && go mod tidy")
    os.system(f"cd {trg} && go build")
    
    unimplemented_functions = [f.name for f in p.function_table.values() if not f.available]
    print(f"Unimplemented functions: {unimplemented_functions}")




if __name__ == '__main__':
    run(open('test.rsl').read(), "tt")