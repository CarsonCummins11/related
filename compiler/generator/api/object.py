#an object loads its data fields from the database
# and provides db backed CRUD operations on them
# and provides read options for derived fields
import parser.program
from generator.writer import Writer

class Object:
    def __init__(self, parser_object: parser.program.Object):
        self.name = parser_object.name
        self.data_fields = {}
        self.derived_fields = {}
        for field in parser_object.fields:
            if field.derived:
                self.derived_fields[field.name] = field
            else:
                self.data_fields[field.name] = field
    
    def write_create_route(self, o: Writer):
        #writes the create route
        o.w(f"func Create{self.name}_route(c *gin.Context) {{")
        o.w(f"    var new_{self.name} objects.{self.name}")
        o.w(f"    c.BindJSON(&new_{self.name})")
        o.w(f"    ret_{self.name},err := objects.Create{self.name}(new_{self.name})")
        o.w(f"    if err != nil {{")
        o.w(f"        panic(err)")
        o.w(f"    }}")
        o.w(f"    c.JSON(http.StatusOK, ret_{self.name})")
        o.w("}")
        o.w(f"")
    def write_read_route(self, o: Writer):
        o.w(f"func Read{self.name}_route(c *gin.Context) {{")
        #get the id from the request
        o.w(f"    id := c.Param(\"id\")")
        o.w(f"    new_{self.name}, err := objects.Read{self.name}(id)")
        o.w(f'    if err != nil && err.Error() == "no rows in result set" {{')
        o.w(f'        c.JSON(http.StatusNotFound, gin.H{{"status": "not found"}})')
        o.w(f'        return')
        o.w(f"    }}")
        o.w(f"    if err != nil {{")
        o.w(f"        panic(err)")
        o.w(f"    }}")
        o.w(f"    c.JSON(http.StatusOK, new_{self.name})")
        o.w("}")
    def write_update_route(self, o: Writer):
        o.w(f"func Update{self.name}_route(c *gin.Context) {{")
        o.w(f"    var new_{self.name} objects.{self.name}")
        o.w(f"    c.BindJSON(&new_{self.name})")
        o.w(f"    ret_{self.name},err := objects.Update{self.name}(new_{self.name})")
        o.w(f"    if err != nil {{")
        o.w(f"        panic(err)")
        o.w(f"    }}")
        o.w(f"    c.JSON(http.StatusOK, ret_{self.name})")
        o.w("}")
    def write_delete_route(self, o: Writer):
        o.w(f"func Delete{self.name}_route(c *gin.Context) {{")
        o.w(f"    type deleteRequest struct {{")
        o.w(f"        ID string")
        o.w(f"    }}")
        o.w(f"    var req deleteRequest")
        o.w(f"    c.BindJSON(&req)")
        o.w(f"    err := objects.Delete{self.name}(req.ID)")
        o.w(f"    if err != nil {{")
        o.w(f"        panic(err)")
        o.w(f"    }}")
        o.w(f"    c.JSON(http.StatusOK, gin.H{{\"status\": \"ok\"}})")
        o.w("}")
    def generate(self, o: Writer):
        cur_file = o.current_file
        o.use_file(f"routes/{self.name}.go")
        o.w(f"package routes")
        o.w(f"")
        o.w(f"import (")
        o.w(f'    "net/http"')
        o.w("")
        o.w(f'    "github.com/gin-gonic/gin"')
        o.w("")
        o.w(f'    "{o.package()}/objects"')
        o.w(f")")
        self.write_create_route(o)
        self.write_read_route(o)
        self.write_update_route(o)
        self.write_delete_route(o)
        o.use_file(cur_file)

    def generate_route_strings(self, o: Writer):
        o.w(f'    {self.name} := router.Group("/{self.name}")')
        o.w(f'    {self.name}.POST("/create", routes.Create{self.name}_route)')
        o.w(f'    {self.name}.GET("/read/:id", routes.Read{self.name}_route)')
        o.w(f'    {self.name}.POST("/update", routes.Update{self.name}_route)')
        o.w(f'    {self.name}.POST("/delete", routes.Delete{self.name}_route)')
        o.w(f"")
