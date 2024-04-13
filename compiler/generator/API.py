from structures.program import Program
from iostuff.writer import Writer
from generator.routes.router import Router
from generator.structs.struct import Struct
from generator.sql.schema import Schema
from generator.sql.connection import Connection

def create_for(p: Program, o: Writer):
    #create the routes
    o.use_file("main.go")
    o.w("package main")
    o.w()
    o.w("import (")
    o.w('   "github.com/gin-gonic/gin"')
    o.w(f'   "{o.package()}/routes"')
    o.w(")")
    o.w()
    o.w("func main() {")
    Router.for_program(p).generate(o)
    o.w("}")


    #create the models
    for obj in p.objects:
        o.use_file(f"models/{obj.name}.go")
        o.w("package models")
        o.w()
        o.w("import (")
        o.w('   "database/sql"')
        o.w('   "context"')
        o.w(")")
        Struct.for_object(obj).generate(o)

    
    #create the DB
    Schema.for_program(p).generate(o)
    Connection.for_program(p).generate(o)
    o.flush()
    

        
