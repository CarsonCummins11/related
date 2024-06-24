CREATE TABLE ChildTest (
    MyName TEXT,
    MyValue INTEGER,
    ID SERIAL PRIMARY KEY
);
CREATE TABLE ChildTest_MyList (
    ChildTest_id INTEGER,
    MyList TEXT,
    FOREIGN KEY (ChildTest_id) REFERENCES ChildTest(ID),
    ID SERIAL PRIMARY KEY
);
CREATE TABLE ParentTest (
    AnotherField TEXT,
    ID SERIAL PRIMARY KEY
);
CREATE TABLE ParentTest_MyChildTests (
    ParentTest_id INTEGER,
    MyChildTests INTEGER,
    FOREIGN KEY (MyChildTests) REFERENCES ChildTest(ID),
    FOREIGN KEY (ParentTest_id) REFERENCES ParentTest(ID),
    ID SERIAL PRIMARY KEY
);
