package database

import (
    "context"
    "fmt"
    "os"

    "github.com/jackc/pgx/v5"
)

var DB *pgx.Conn

func init(){
   conn, err := pgx.Connect(context.Background(), os.Getenv("DATABASE_URL"))
   if err != nil {
       fmt.Fprintf(os.Stderr, "Unable to connect to database: %v\n", err)
   }
   DB = conn
}

