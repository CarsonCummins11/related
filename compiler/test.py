#runs the tests in /tests
import os
import subprocess
import time
import sys

def run_test(name: str, rebuild=False) -> bool:
    if not os.path.exists(f"tests/{name}/{name}/up.sh") or rebuild:
        os.system(f"rm -rf tests/{name}/{name}") #clean up
        print("Rebuilding test server for", name)
        subprocess.run(["python","app.py", f"tests/{name}/test.up", f"tests/{name}/{name}"])
        assert os.path.exists(f"tests/{name}/{name}/build.sh"), f"Failed to build test server {name}"
        os.chdir(f"tests/{name}/{name}")
        subprocess.run(["sh","build.sh"])
    print("Running test", name)
    subprocess.Popen(["sh","up.sh"])
    #give the server a sec to start up
    time.sleep(2)
    #run the test
    os.chdir(f"../../..")
    p = subprocess.run(["python",f"tests/{name}/test.py"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.returncode == 0

def run_tests(rebuild=False, runOnly=None):
    if runOnly:
        if run_test(runOnly, rebuild):
            print("Test passed")
        else:
            print("Test failed")
        return
    
    total = 0
    total_passed = 0
    failing = []
    for test in os.listdir("tests"):
        total+=1
        if run_test(test, rebuild):
            total_passed+=1
            print(f"Test {test} passed")
        else:
            failing.append(test)
            print(f"Test {test} failed")
    print(f"Failing tests:\n\t{'\n\t'.join(failing)}")
    print(f"{total_passed}/{total} tests passed ({total_passed/total*100:.2f}%)")


if __name__ == '__main__':
    rebuild = False
    runOnly = None

    if len(sys.argv) == 2:
        if sys.argv[1] == "-r" or sys.argv[1] == "--rebuild":
            rebuild = True
        else:
            runOnly = sys.argv[1]
    elif len(sys.argv) == 3:
        if sys.argv[1] == "-r" or sys.argv[1] == "--rebuild":
            rebuild = True
        runOnly = sys.argv[2]

    run_tests(rebuild, runOnly)

        
        