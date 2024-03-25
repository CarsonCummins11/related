from parser.program import Program
from generator.writer import Writer
from generator.api.api import API
from generator.data.data_platform import DataPlatform
from generator.data.derivers import Derivers
from parser.function import Function
import os
import subprocess

def gather_function_table(path: str = "derived"):
    #to gather the funcs + types on local package derived, use:
    #go doc -short compiler/derived | grep "^[ ]*func "
    pkg_name = path.split("/")[-1]
    pkg_first = path.split("/")[0]
    pkg_root = pkg_first + "/"+"/".join(path.split("/")[1:-1])
    proc = subprocess.Popen(f"go doc -C {pkg_root} -short {pkg_name} | grep '^[ ]*func ' ",shell=True, stdout=subprocess.PIPE)
    functypes = [x.decode().replace("\n","") for x in proc.stdout.readlines()]
    print(functypes)
    function_table = {}
    for ft in functypes:
        if not ft:
            continue
        f = ft.split(" ")
        fname = f[1].split("(")[0]
        freturn = f[-1]
    
        argstring = ft[ft.index("(")+1:ft.index(")")]
        argstrings = []
        if argstring:
            argstrings = argstring.split(", ")
        argtypes = [x.split(" ")[1] for x in argstrings]
        argnames = [x.split(" ")[0] for x in argstrings]

        src = "\n".join([x.decode() for x in subprocess.Popen(f"go doc -C {pkg_root} -short -src {pkg_name}.{fname}",shell=True, stdout=subprocess.PIPE).stdout.readlines()][1:-1])
        function_table[fname] = Function(fname, argtypes, freturn, True,src, argnames)
    return function_table

def run(src: str, trg: str):
    
    p = Program(src, gather_function_table())
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