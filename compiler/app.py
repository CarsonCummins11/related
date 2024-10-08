import subprocess
import sys
from typing import List

from iostuff.writer import Writer
from structures.program import Program
from structures.function import Function
import generator.API
import os

def gather_function_table(path: str = "derived") -> List[Function]:
    #to gather the funcs + types on local package derived, use:
    #go doc -short compiler/derived | grep "^[ ]*func "

    #if theres no go package to examine funcs from, make it and delete it at the end
    should_delete_mod_file = False
    if not os.path.exists(f"go.mod"):
        should_delete_mod_file = True
        with open("go.mod", "w") as f:
            f.write("module derived")

    proc = subprocess.Popen(f"go doc -C {path} | grep '^[ ]*func ' ",shell=True, stdout=subprocess.PIPE)
    functypes = [x.decode().replace("\n","") for x in proc.stdout.readlines()]

    print(f"This is the functype printing:   \n\n\n\n\n\n\n\n\n\n\n\n\n\n\n {functypes}")
    function_table = []
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
        argnames = [x.split(" ")[0] for x in argstrings] #Might want to save eventually

        src = "\n".join([x.decode() for x in subprocess.Popen(f"go doc -C {path} -short -src derived.{fname}",shell=True, stdout=subprocess.PIPE).stdout.readlines()])
        function_table.append(Function(fname, freturn, argtypes))
        print(f"function {fname} with return {freturn} and args {argtypes} and src: \n{src}")

    if should_delete_mod_file:
        os.remove("go.mod")

    return function_table

def run(pth: str, trg: str):
    derived_loc = "derived"
    if len(pth.split("/")) > 1:
        derived_loc = "/".join(pth.split("/")[:-1]) + "/derived"
    print("expecting derived located at ", derived_loc)
    src = open(pth).read()
    name = trg.split("/")[-1].split(".")[0]


    p = Program.parse(src, name, gather_function_table(derived_loc))
    print(p)

    writer = Writer(trg)
    generator.API.create_for(p, writer)
    #copy in derived folder
    os.system(f"cp -r {derived_loc} {trg}")





if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python app.py <source> <target>")
        sys.exit(1)
    print("running compilation with source", sys.argv[1], "and target", sys.argv[2])
    run(sys.argv[1], sys.argv[2])