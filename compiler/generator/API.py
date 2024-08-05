from structures.program import Program
from iostuff.writer import Writer
from generator.routes.router import Router
from generator.structs.struct import Struct
from generator.sql.schema import Schema
from generator.sql.connection import Connection
from generator.build.build import generate_build, generate_up
from generator.Docs import generate_docs


def create_for(p: Program, o: Writer):
    #create the routes
    o.use_file("main.go")
    o.w("package main")
    o.w()
    o.w("import (")
    o.w('   "github.com/gin-gonic/gin"')
    o.w(f'   "{o.package()}/routes"')
    o.w(f'   "{o.package()}/models"')
    o.w(")")
    o.w()
    #helper function to attach authorized user to context
    o.w("func AttachUserIfAuthorized(c *gin.Context) {")
    #get header
    o.w("   token := c.GetHeader(\"Authorization\")")
    o.w("   if token == \"\" {")
    o.w("       c.Next()")
    o.w("       return")
    o.w("   }")
    o.w("   user, err := models.GetUserBySessionToken(token)")
    o.w("   if err != nil {")
    o.w("       c.Next()")
    o.w("       return")
    o.w("   }")
    o.w("   c.Set(\"user\", user)")
    o.w("   c.Next()")
    o.w("}")
    o.w("func main() {")
    Router.for_program(p).generate(o)
    o.w("}")


     #write the GetUserBySessionToken function
    o.use_file("models/authuser__.go")
    o.w("package models")
    o.w()
    o.w("import (")
    o.w('   "context"')
    o.w(')')

    o.w(f"func GetUserBySessionToken(token string) ({p.user_object_name}, error) {{")
    o.w(f"    var user {p.user_object_name}")
    o.w(f"    err := DB.QueryRow(context.Background(), `SELECT * FROM {p.user_object_name} WHERE S__session_token__ = $1`, token).Scan(")
    for field in p.get_object(p.user_object_name).stored_fields():
        o.w(f"        &user.{field.name},")
    o.w(f"    )")
    o.w(f"    if err != nil {{")
    o.w(f"        return user, err")
    o.w(f"    }}")
    o.w(f"    return user, nil")
    o.w(f"}}")

    #create the models
    for obj in p.objects:
        o.use_file(f"models/{obj.name}.go")
        o.w("package models")
        o.w()
        o.w("import (")
        o.w('   "context"')
        o.w('   "strconv"')
        o.w('   "errors"')
        if len(Struct.for_object(obj).function_derived_fields()) > 0:
            o.w(f'   "{o.package()}/derived"')
        o.w(")")
        o.w()
        #write the Create function

        Struct.for_object(obj).generate(o)

    
    #create the DB schema and connection code
    Schema.for_program(p).generate(o)
    Connection.for_program(p).generate(o)

    #create the build code
    generate_build(p.name, o)
    generate_up(p.name, o)
    

    #generate openapi spec
    o.use_file("openapi.json")

    o.w(generate_docs(p))

    o.flush()

    

        
