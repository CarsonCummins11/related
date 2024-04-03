import parser.program
from compiler.iostuff.writer import Writer
from typing import List
from generator.data.object import Object

class DataPlatform:
    def __init__(self, program: parser.program.Program):
        self.objects = [Object(obj, program) for obj in program.objects]


    def generate(self, o: Writer):
        #generate the SQL schema
        o.use_file(f"schema.sql")
        for obj in self.objects:
            obj.generate_schema(o)

        #generate the database initialization
        o.use_file(f"database/Pinit.go")
        o.w(f"package database")
        o.w(f"")
        o.w(f"import (")
        o.w(f'    "context"')
        o.w(f'    "fmt"')
        o.w(f'    "os"')
        o.w("")
        o.w(f'    "github.com/jackc/pgx/v5"')
        o.w(")")
        o.w("")
        o.w(f"var DB *pgx.Conn")
        o.w("")
        o.w("func init(){")
        o.w('   conn, err := pgx.Connect(context.Background(), os.Getenv("DATABASE_URL"))')
        o.w('   if err != nil {')
        o.w('       fmt.Fprintf(os.Stderr, "Unable to connect to database: %v\\n", err)')
        o.w('   }')
        o.w('   DB = conn')
        o.w('}')
        o.w("")

        #generate the object files
        for obj in self.objects:
            obj.generate(o)