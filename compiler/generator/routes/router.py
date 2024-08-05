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
        o.w('   "golang.org/x/crypto/bcrypt"')
        o.w('   "github.com/gin-gonic/gin/binding"')
        o.w('   "crypto/rand"')
        o.w('   "log"')
        o.w()
        o.w(f'   "{o.package()}/models"')
        o.w(")")
        o.w()
        o.w("func MakePasswordHash(password string) string {")
        o.w("    log.Println(\"Making password hash for password: \"+password)")
        o.w("    bytes, err := bcrypt.GenerateFromPassword([]byte(password), 14)")
        o.w("    if err != nil {")
        o.w("        log.Println(\"Error hashing password: \", err)")
        o.w("        return \"\"")
        o.w("    }")
        o.w("    return string(bytes)")
        o.w("}")
        o.w()
        o.w("func MakeSessionToken() string {")
        o.w("    log.Println(\"Making session token\")")
        #note 64 character options means no modulo bias for bytes as selectors because 256 % 64 == 0
        o.w("    token_chars := \"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-\"")
        o.w("    bytes := make([]byte, 32)")
        o.w("    _, err := rand.Read(bytes)")
        o.w("    if err != nil {")
        o.w("        log.Println(\"Error making session token: \", err)")
        o.w("        return \"\"")
        o.w("    }")
        o.w("    for i, b := range bytes {")
        o.w("        bytes[i] = token_chars[int(b)%len(token_chars)]")
        o.w("    }")
        o.w("    return string(bytes)")
        o.w("}")
        o.use_file(cf)
        #attach user if authorzed user exists
        o.w(f"router.Use(AttachUserIfAuthorized)")
        for obj, routes in self.routes.items():
            cf = o.current_file
            o.w(f'  {obj} := router.Group("/{obj}")')
            #middleware to attach user object to context
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