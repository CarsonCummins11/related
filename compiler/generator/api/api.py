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
        o.w(f'    "{self.name}/routes"')
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

        o.use_file(f"build.sh")
        o.w(f"#!/bin/bash")
        o.w(f'hastable=$(psql -l | grep " {self.name} ")')
        o.w(f'if [ -z "$hastable" ]; then')
        o.w(f'    echo "no db found, creating db {self.name}..."')
        o.w(f'    createdb {self.name}')
        o.w(f'    psql {self.name} < schema.sql')
        o.w("else")
        o.w(f'    echo "db {self.name} already exists, dropping and recreating..."')
        o.w(f'    dropdb {self.name}')
        o.w(f'    createdb {self.name}')
        o.w(f'    psql {self.name} < schema.sql')
        o.w(f'fi')
        o.w(f"go mod init {self.name}")
        o.w(f"go mod tidy")
        o.w(f"go build")

        o.use_file(f"up.sh")
        o.w(f"#!/bin/bash")
        o.w(f"export DATABASE_URL=postgres://localhost/{self.name}")
        o.w(f"./{self.name}")
