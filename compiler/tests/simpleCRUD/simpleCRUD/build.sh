#!/bin/bash
hastable=$(psql -l | grep " simpleCRUD ")
if [ -z "$hastable" ]; then
    echo "no db found, creating db simpleCRUD..."
    createdb simpleCRUD
    psql simpleCRUD < schema.sql
else
    echo "db simpleCRUD already exists, dropping and recreating..."
    dropdb simpleCRUD
    createdb simpleCRUD
    psql simpleCRUD < schema.sql
fi
go mod init simpleCRUD
go mod tidy
go build
