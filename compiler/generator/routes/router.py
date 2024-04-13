from typing import Dict, List
from iostuff.writer import Writer
from structures.program import Program
from generator.routes.route import *

class Router:
    def __init__(self, routes: Dict[str,List[Route]] = []):
        self.routes = routes

    def add_route(self, route: Route):
        self.routes.append(route)

    def generate(self, o: Writer) -> str:
        o.w("   router := gin.Default()")
        o.w()
        cf = o.current_file
        o.use_file("routes/routes.go")
        o.w("package routes")
        o.w()
        o.w("import (")
        o.w('   "github.com/gin-gonic/gin"')
        o.w()
        o.w(f'   "{o.package()}/models"')
        o.w(")")
        o.use_file(cf)
        for obj, routes in self.routes.items():
            cf = o.current_file
            o.w(f'  {obj} := router.Group("/{obj}")')
            for route in routes:
                o.w(f'  {obj}.{route.method}("{route.path}", routes.{route.handler})')
                cf = o.current_file
                o.use_file("routes/routes.go")
                route.generate(o)
                o.use_file(cf)
        
        o.w('router.Run("localhost:8080")')

    
    @staticmethod
    def for_program(program: Program) -> 'Router':
        routes = {}
        for obj in program.objects:

            if not obj.name in routes:
                routes[obj.name] = []

            routes[obj.name].extend([
                CreateRoute.for_object(obj),
                ReadRoute.for_object(obj),
                UpdateRoute.for_object(obj),
                DeleteRoute.for_object(obj)
            ])
        return Router(routes)