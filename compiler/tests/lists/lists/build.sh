#!/bin/bash
hastable=$(psql -l | grep " lists ")
if [ -z "$hastable" ]; then
    echo "no db found, creating db lists..."
    createdb lists
    psql lists < schema.sql
else
    echo "db lists already exists, dropping and recreating..."
    dropdb lists
    createdb lists
    psql lists < schema.sql
fi
go mod init lists
go mod tidy
go build
