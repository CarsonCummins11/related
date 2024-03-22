import parser.program
from generator.api.object import Object
from generator.writer import Writer
from typing import List
import os
class API:
    def __init__(self, name,objects: List[parser.program.Object]):
        self.name = name
        self.objects: List[Object] = []
        for obj in objects:
            self.objects.append(Object(obj))

    def generate(self, o: Writer):
        o.use_file(f"main.go")
        o.w(f"package main")
        o.w(f"")
        o.w(f"import (")
        o.w(f'    "github.com/gin-gonic/gin"')
        o.w(f'    "{self.name}/objects"')
        o.w(f")")
        o.w(f"")
        o.w(f"func main() {{")
        o.w(f"    router := gin.Default()")
        o.w(f"")
        for obj in self.objects:
            obj.generate(o)
            obj.generate_route_strings(o)
        o.w(f"")
        o.w(f'    router.Run("localhost:8080")')
        o.w(f"}}")
        #create go mod/sum files
        os.system(f"cd {o.path} && go mod init {self.name}")
