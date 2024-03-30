import os
import shutil
class Writer:
    def __init__(self, path: str):
        self.path = path
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        else:
            shutil.rmtree(self.path)
            os.makedirs(self.path)
        self.current_file = ""
        self.buffer = {}
    
    def use_file(self, file_name: str):
        self.current_file = file_name

    def w(self, s: str, endl: bool = True):
        term = "\n" if endl else ""
        if self.current_file not in self.buffer:
            self.buffer[self.current_file] = ""
        self.buffer[self.current_file] += s + term

    def flush(self):
        for file_name, content in self.buffer.items():
            if not os.path.exists(os.path.join(self.path, file_name)):
                os.makedirs(os.path.dirname(os.path.join(self.path, file_name)), exist_ok=True)
            with open(os.path.join(self.path, file_name), "w+") as f:
                f.write(content)
        self.buffer = {}

    def package(self):
        #returns the current parent go package being written to
        return self.path.split("/")[-1]