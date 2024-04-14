from iostuff.writer import Writer

def generate_build(name: str, o: Writer):
    o.use_file('build.sh')
    o.w(f'#!/bin/bash')
    o.w(f'hastable=$(psql -l | grep " {name} ")')
    o.w(f'if [ -z "$hastable" ]; then')
    o.w(f'    echo "no db found, creating db {name}..."')
    o.w(f'    createdb {name}')
    o.w(f'    psql {name} < schema.sql')
    o.w(f'else')
    o.w(f'    echo "db {name} already exists, dropping and recreating..."')
    o.w(f'    dropdb {name}')
    o.w(f'    createdb {name}')
    o.w(f'    psql {name} < schema.sql')
    o.w(f'fi')
    o.w(f'go mod init {name}')
    o.w(f'go mod tidy')
    o.w(f'go build')


def generate_up(name: str,o: Writer):
    o.use_file('up.sh')
    o.w(f'#!/bin/bash')
    o.w(f'export DATABASE_URL=postgres://localhost/{name}')
    o.w(f'./{name}')