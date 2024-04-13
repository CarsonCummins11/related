'''
var DB *pgx.Conn

func init(){
   conn, err := pgx.Connect(context.Background(), os.Getenv("DATABASE_URL"))
   if err != nil {
       fmt.Fprintf(os.Stderr, "Unable to connect to database: %v\n", err)
   }
   DB = conn
}
'''

from structures.program import Program
from iostuff.writer import Writer

class Connection:
    
    def generate(self, o: Writer):
        o.use_file('models/db.go')

        o.w('package models')

        o.w()
        o.w('import (')
        o.w('   "os"')
        o.w('   "fmt"')
        o.w('   "context"')
        o.w('   "github.com/jackc/pgx/v4"')
        o.w(')')

        o.w('var DB *pgx.Conn')
        o.w()
        o.w('func init(){')
        o.w('   conn, err := pgx.Connect(context.Background(), os.Getenv("DATABASE_URL"))')
        o.w('   if err != nil {')
        o.w('       fmt.Fprintf(os.Stderr, "Unable to connect to database: %v\\n", err)')
        o.w('   }')
        o.w('   DB = conn')
        o.w('}')
        o.w()
    
    @staticmethod
    def for_program(program: Program) -> 'Connection':
        return Connection()