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
    
    def write_create(self, o: Writer):

        o.w(f"func Create{self.name}_route(c *gin.Context) {{")
        o.w(f"    var new_{self.name} {self.name}")
        o.w(f"    c.BindJSON(&new_{self.name})")
        o.w(f"    //TODO: insert obj into db")
        o.w(f"    c.JSON(http.StatusOK, gin.H{{\"status\": \"ok\"}})")
        o.w("}")
        o.w(f"")
    def write_read(self, o: Writer):
        o.w(f"func Read{self.name}_route(c *gin.Context) {{")
        o.w(f"    //TODO: read obj from db")
        o.w(f"    c.JSON(http.StatusOK, gin.H{{\"status\": \"ok\"}})")
        o.w("}")
    def write_update(self, o: Writer):
        o.w(f"func Update{self.name}_route(c *gin.Context) {{")
        o.w(f"    //TODO: update obj")
        o.w(f"    c.JSON(http.StatusOK, gin.H{{\"status\": \"ok\"}})")
        o.w("}")
    def write_delete(self, o: Writer):
        o.w(f"func Delete{self.name}_route(c *gin.Context) {{")
        o.w(f"    //TODO: delete obj")
        o.w(f"    c.JSON(http.StatusOK, gin.H{{\"status\": \"ok\"}})")
        o.w("}")
    def generate(self, o: Writer):
        cur_file = o.current_file
        o.use_file(f"objects/{self.name}.go")
        o.w(f"package objects")
        o.w(f"")
        o.w(f"import (")
        o.w(f'    "net/http"')
        o.w("")
        o.w(f'    "github.com/gin-gonic/gin"')
        o.w(f")")
        o.w("type " + self.name + " struct {")
        for field in self.data_fields.values():
            o.w(f"    {field.name} {field.t}")
        o.w("    ID string")
        o.w("}")
        self.write_create(o)
        self.write_read(o)
        self.write_update(o)
        self.write_delete(o)
        o.use_file(cur_file)

    def generate_route_strings(self, o: Writer):
        o.w(f'    {self.name} := router.Group("/{self.name}")')
        o.w(f'    {self.name}.POST("/create", objects.Create{self.name}_route)')
        o.w(f'    {self.name}.GET("/read", objects.Read{self.name}_route)')
        o.w(f'    {self.name}.POST("/update", objects.Update{self.name}_route)')
        o.w(f'    {self.name}.POST("/delete", objects.Delete{self.name}_route)')
        o.w(f"")
