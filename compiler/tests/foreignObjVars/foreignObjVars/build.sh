#!/bin/bash
hastable=$(psql -l | grep " foreignObjVars ")
if [ -z "$hastable" ]; then
    echo "no db found, creating db foreignObjVars..."
    createdb foreignObjVars
    psql foreignObjVars < schema.sql
else
    echo "db foreignObjVars already exists, dropping and recreating..."
    dropdb foreignObjVars
    createdb foreignObjVars
    psql foreignObjVars < schema.sql
fi
go mod init foreignObjVars
go mod tidy
go build
