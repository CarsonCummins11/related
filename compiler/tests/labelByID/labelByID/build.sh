#!/bin/bash
hastable=$(psql -l | grep " labelByID ")
if [ -z "$hastable" ]; then
    echo "no db found, creating db labelByID..."
    createdb labelByID
    psql labelByID < schema.sql
else
    echo "db labelByID already exists, dropping and recreating..."
    dropdb labelByID
    createdb labelByID
    psql labelByID < schema.sql
fi
go mod init labelByID
go mod tidy
go build
