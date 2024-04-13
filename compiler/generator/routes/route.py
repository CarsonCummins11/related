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
        o.w(f'    c.BindJSON(&obj)')
        o.w(f'    obj_hydrated, err := obj.Create()')
        o.w(f'    if err != nil {{')
        o.w(f'        c.JSON(500, err)')
        o.w(f'        return')
        o.w(f'    }}')
        o.w(f'    c.JSON(200, obj_hydrated)')
        o.w(f'}}')

    @staticmethod
    def for_object(obj: Object) -> 'CreateRoute':
        return CreateRoute("POST", "/create", f"Create{obj.name}_route", obj)

class ReadRoute(Route):
    def __init__(self, method: str, path: str, handler: str, obj: Object):
        super().__init__(method, path, handler, obj)

    def generate(self, o: Writer):
        o.w(f'func {self.handler}(c *gin.Context) {{')
        o.w(f'    id := c.Param("id")')
        o.w(f'    obj, err := models.Read{self.obj.name}(id)')
        o.w(f'    if err != nil {{')
        o.w(f'        c.JSON(500, err)')
        o.w(f'        return')
        o.w(f'    }}')
        o.w(f'    c.JSON(200, obj)')
        o.w(f'}}')

    @staticmethod
    def for_object(obj: Object) -> 'ReadRoute':
        return ReadRoute("GET", "/read/:id", f"Read{obj.name}_route", obj)

class UpdateRoute(Route):
    def __init__(self, method: str, path: str, handler: str, obj: Object):
        super().__init__(method, path, handler, obj)
    
    def generate(self, o: Writer):
        o.w(f'func {self.handler}(c *gin.Context) {{')
        o.w(f'    id := c.Param("id")')
        o.w(f'    var obj models.{self.obj.name}')
        o.w(f'    c.BindJSON(&obj)')
        o.w(f'    obj_hydrated, err := obj.Update(id)')
        o.w(f'    if err != nil {{')
        o.w(f'        c.JSON(500, err)')
        o.w(f'        return')
        o.w(f'    }}')
        o.w(f'    c.JSON(200, obj_hydrated)')
        o.w(f'}}')

    @staticmethod
    def for_object(obj: Object) -> 'UpdateRoute':
        return UpdateRoute("PUT", "/update/:id", f"Update{obj.name}_route", obj)

class DeleteRoute(Route):
    def __init__(self, method: str, path: str, handler: str, obj: Object):
        super().__init__(method, path, handler, obj)

    def generate(self, o: Writer):
        o.w(f'func {self.handler}(c *gin.Context) {{')
        o.w(f'    id := c.Param("id")')
        o.w(f'    err := models.Delete{self.obj.name}(id)')
        o.w(f'    if err != nil {{')
        o.w(f'        c.JSON(500, err)')
        o.w(f'        return')
        o.w(f'    }}')
        o.w('    c.JSON(200, "Deleted")')
        o.w(f'}}')

    @staticmethod
    def for_object(obj: Object) -> 'DeleteRoute':
        return DeleteRoute("DELETE", "/delete/:id", f"Delete{obj.name}_route", obj)