from parser.program import Program
from generator.writer import Writer
from generator.api.api import API
from generator.data.data_platform import DataPlatform
from parser.function import Function
import subprocess
import sys
import os

def gather_function_table(path: str = "derived"):
    #to gather the funcs + types on local package derived, use:
    #go doc -short compiler/derived | grep "^[ ]*func "
    proc = subprocess.Popen(f"go doc -C {path} -short derived | grep '^[ ]*func ' ",shell=True, stdout=subprocess.PIPE)
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

        src = "\n".join([x.decode() for x in subprocess.Popen(f"go doc -C {path} -short -src derived.{fname}",shell=True, stdout=subprocess.PIPE).stdout.readlines()][1:-1])
        function_table[fname] = Function(fname, argtypes, freturn, True,src, argnames)
        print(function_table[fname].arg_types)
    return function_table

def run(src: str, trg: str):
    derived_loc = "derived"
    if len(src.split("/")) > 1:
        derived_loc = "/".join(src.split("/")[:-1]) + "/derived"
    print("expecting derived located at ", derived_loc)
    p = Program(open(src).read(), gather_function_table(derived_loc))
    p.parse()
    api = API(trg.split("/")[-1], p.objects)
    w = Writer(trg)
    api.generate(w)
    data = DataPlatform(p)
    data.generate(w)
    os.system(f"cp -r {'/'.join(src.split('/')[:-1])}/derived {trg}/derived")
    w.flush()
    
    unimplemented_functions = [f.name for f in p.function_table.values() if not f.available]
    print(f"Unimplemented functions: {unimplemented_functions}")
    assert len(unimplemented_functions) == 0, "Unimplemented functions found"




if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python app.py <source> <target>")
        sys.exit(1)
    print("running compilation with source", sys.argv[1], "and target", sys.argv[2])
    run(sys.argv[1], sys.argv[2])