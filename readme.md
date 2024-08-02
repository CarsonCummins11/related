## rsl

rsl is a declarative API creation DSL. It is implemented in this repo with a compiler (written in python3) targeting Go. It is unique for a few reasons:

- automatically generates OpenAPI (swagger) docs
- uses declarative reactive paradigm to match common frontend paradigms
- targets a single binary (generates go code so this just happens)
- provides auth system + granular data access controls

Here is an example of a simple collaborative document editor API implemented in rsl:

```
Document {
    Owner: @User;
    Editors: []User;
    Edits: []Edit - RU: $ in Editors || $ = Owner D: $ = Owner;
    DocHTML: AssembleDocument(Edits);
    EditsByOwner: Query("SELECT * FROM Edit WHERE Author = ", Owner.ID);
} -  CRUD: $.ID = Owner.ID 
$User{
    Name: @string;
} - CRUD: $.ID = ID

Edit{
    StartAt: @int;
    DeleteCount: @int;
    AddText: @string;
    Author: @User; 
}
```

###  "documentation"
@ - store this value
[] - a stored list value
$ - the object associated with login
\- start of a governance clause




A governance clause is true iff current state of data can be transitioned to the next state for the op. So,
`Must_Be_One: @int - CUD: Must_Be_One == 1;`
Would allow Create, Update, Delete access to all changes that result in the stored integer Must_Be_One remaining equal to 1. 

Functions, like AssembleDocument or Query must be implemented in Go in a folder called derivations. Look at the tests for examples.