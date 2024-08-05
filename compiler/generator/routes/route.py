from structures.program import PRIMITIVES
from structures.object import Object
from iostuff.writer import Writer

class Route:
    def __init__(self, method: str, path: str, handler: str, obj: Object):
        self.method = method
        self.path = path
        self.handler = handler
        self.obj = obj
    
    def generate(self, o: Writer):
        pass


class CreateRoute(Route):
    def __init__(self, method: str, path: str, handler: str, obj: Object):
        super().__init__(method, path, handler, obj)

    def generate(self, o: Writer):
        o.w(f'func {self.handler}(c *gin.Context) {{')
        o.w(f'    var obj models.{self.obj.name}')
        o.w(f'    c.ShouldBindBodyWith(&obj, binding.JSON)')
        if self.obj.context.user_object_name == self.obj.name:
            #parse password from context as well to see if a S__password field exists
            #generate password hash and session token if so
            o.w(f'    type PasswordStruct struct {{')
            o.w(f'        S__password__ string')
            o.w(f'    }}')
            o.w(f'    var password PasswordStruct')
            o.w(f'    c.ShouldBindBodyWith(&password, binding.JSON)')
            o.w(f'    if password.S__password__ != "" {{')
            o.w(f'        obj.S__password_hash__ = MakePasswordHash(password.S__password__)')
            o.w(f'        obj.S__session_token__ = MakeSessionToken()')
            o.w(f'    }}')


        o.w(f'    var user models.{self.obj.context.user_object_name}')
        o.w(f'    user_ut, exists := c.Get("user")')
        o.w(f'    if exists {{')
        o.w(f'      user = user_ut.(models.{self.obj.context.user_object_name})')
        o.w(f'    }}')
        o.w(f'    log.Println("Creating object: ", obj)')
        o.w(f'    obj_hydrated, err := obj.Create(user)')
        o.w(f'    if err != nil {{')
        o.w(f'        log.Println("Error creating object: ", err)')
        o.w(f'        c.JSON(500, err)')
        o.w(f'        return')
        o.w(f'    }}')
        o.w(f'    c.JSON(200, obj_hydrated)')
        o.w(f'}}')

    @staticmethod
    def for_object(obj: Object) -> 'CreateRoute':
        return CreateRoute("POST", "/", f"Create{obj.name}_route", obj)

class ReadRoute(Route):
    def __init__(self, method: str, path: str, handler: str, obj: Object):
        super().__init__(method, path, handler, obj)

    def generate(self, o: Writer):
        o.w(f'func {self.handler}(c *gin.Context) {{')
        o.w(f'    id := c.Param("id")')
        #get user from context
        o.w(f'    var user models.{self.obj.context.user_object_name}')
        o.w(f'    user_ut, exists := c.Get("user")')
        o.w(f'    if exists {{')
        o.w(f'      user = user_ut.(models.{self.obj.context.user_object_name})')
        o.w(f'    }}')
        o.w(f'    obj, err := models.Read{self.obj.name}(id, user)')
        o.w(f'    if err != nil {{')
        #check for obj not found and correct error to 404
        o.w(f'        if err.Error() == "no rows in result set" {{')
        o.w(f'            c.JSON(404, "Object not found")')
        o.w(f'            return')
        o.w(f'        }}')
        o.w(f'        log.Println("Error reading object: ", err)')
        o.w(f'        c.JSON(500, err)')
        o.w(f'        return')
        o.w(f'    }}')
        o.w(f'    c.JSON(200, obj)')
        o.w(f'}}')

    @staticmethod
    def for_object(obj: Object) -> 'ReadRoute':
        return ReadRoute("GET", "/:id", f"Read{obj.name}_route", obj)

class UpdateRoute(Route):
    def __init__(self, method: str, path: str, handler: str, obj: Object):
        super().__init__(method, path, handler, obj)
    
    def generate(self, o: Writer):
        o.w(f'func {self.handler}(c *gin.Context) {{')
        #get user from context
        o.w(f'    var user models.{self.obj.context.user_object_name}')
        o.w(f'    user_ut, exists := c.Get("user")')
        o.w(f'    if exists {{')
        o.w(f'      user = user_ut.(models.{self.obj.context.user_object_name})')
        o.w(f'    }}')
        o.w(f'    id := c.Param("id")')
        o.w(f'    var obj struct{{')
        o.w(f'      Obj models.{self.obj.name}')
        for field in self.obj.fields:
            if field.is_list():
                o.w(f'      LA_{field.name} []{field.t.replace("[]","") if field.t.replace("[]","") in PRIMITIVES else "int"}')
                o.w(f'      LD_{field.name} []int')
        o.w(f'    }}')
        o.w(f'    c.BindJSON(&obj)')
        o.w(f'    log.Println("Updating object: ", obj)')
        o.w(f'    obj_hydrated, err := obj.Obj.Update(id,')
        for field in self.obj.fields:
            if field.is_list():
                o.w(f'        obj.LA_{field.name},')
                o.w(f'        obj.LD_{field.name},')
        o.w(f'    user)')
        o.w(f'    if err != nil {{')
        o.w(f'        if err.Error() == "no rows in result set" {{')
        o.w(f'            c.JSON(404, "Object not found")')
        o.w(f'            return')
        o.w(f'        }}')
        o.w(f'        log.Println("Error updating object: ", err)')
        o.w(f'        c.JSON(500, err)')
        o.w(f'        return')
        o.w(f'    }}')
        o.w(f'    c.JSON(200, obj_hydrated)')
        o.w(f'}}')

    @staticmethod
    def for_object(obj: Object) -> 'UpdateRoute':
        return UpdateRoute("PUT", "/:id", f"Update{obj.name}_route", obj)

class DeleteRoute(Route):
    def __init__(self, method: str, path: str, handler: str, obj: Object):
        super().__init__(method, path, handler, obj)

    def generate(self, o: Writer):
        o.w(f'func {self.handler}(c *gin.Context) {{')
        o.w(f'    id := c.Param("id")')
        #get the logged in user from context
        #get user from context
        o.w(f'    var user models.{self.obj.context.user_object_name}')
        o.w(f'    user_ut, exists := c.Get("user")')
        o.w(f'    if exists {{')
        o.w(f'      user = user_ut.(models.{self.obj.context.user_object_name})')
        o.w(f'    }}')
        o.w(f'    err := models.Delete{self.obj.name}(id,user)')
        o.w(f'    if err != nil {{')
        o.w(f'        if err.Error() == "no rows in result set" {{')
        o.w(f'            c.JSON(404, "Object not found")')
        o.w(f'            return')
        o.w(f'        }}')
        o.w(f'        log.Println("Error deleting object: ", err)')
        o.w(f'        c.JSON(500, err)')
        o.w(f'        return')
        o.w(f'    }}')
        o.w(f'    log.Println("Deleted object with id: ", id)')
        o.w('    c.JSON(200, "Deleted")')
        o.w(f'}}')

    @staticmethod
    def for_object(obj: Object) -> 'DeleteRoute':
        return DeleteRoute("DELETE", "/:id", f"Delete{obj.name}_route", obj)