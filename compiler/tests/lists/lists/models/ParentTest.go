package models

import (
   "context"
   "strconv"
)
type ParentTest struct {
    AnotherField string
ID int
}
type ParentTestHydrated struct {
    MyChildTests []ChildTestHydrated
    AnotherField string
ID int
}

func (obj ParentTest) FetchList_MyChildTests() ([]ChildTestHydrated) {
println("fetching list for MyChildTests")
    ret := make([]ChildTest,0)
    rows,err := DB.Query(context.TODO(),"SELECT ChildTest.* FROM ParentTest_MyChildTests INNER JOIN ChildTest ON ParentTest_MyChildTests.MyChildTests = ChildTest.ID WHERE ParentTest_MyChildTests.ParentTest_id = $1", obj.ID)
    if err != nil {
        panic(err)
        return []ChildTestHydrated{}
    }
    for rows.Next() {
    println("got a list item for MyChildTests")
        var temp ChildTest
        err = rows.Scan(&temp.MyName, &temp.MyValue,&temp.ID)
        if err != nil {
            panic(err)
            continue
        }
        ret = append(ret,temp)
    }
    real_ret := make([]ChildTestHydrated,0)
    for _,item := range ret {
        real_ret = append(real_ret, item.Hydrate())
    }
    return real_ret
}

func (obj ParentTest) Hydrate() ParentTestHydrated {
    _L_MyChildTests := obj.FetchList_MyChildTests()
    return ParentTestHydrated{
      MyChildTests: _L_MyChildTests,
      AnotherField: obj.AnotherField,
        ID: obj.ID,
    }
}

func (obj ParentTest) Create() (ParentTestHydrated, error) {
    err := DB.QueryRow(context.TODO(),"INSERT INTO ParentTest (AnotherField) VALUES ($1) RETURNING ID", obj.AnotherField).Scan(&obj.ID)
    if err != nil {
        return ParentTestHydrated{}, err
    }
    return obj.Hydrate(), err
}

func ReadParentTest(id string) (ParentTestHydrated, error) {
    var obj ParentTest
    int_id,erro := strconv.Atoi(id)
    if erro != nil {
        return ParentTestHydrated{}, erro
    }
    obj.ID = int_id
    err := DB.QueryRow(context.TODO(),"SELECT AnotherField FROM ParentTest WHERE ID = $1", id).Scan(&obj.AnotherField)
    if err != nil {
        return ParentTestHydrated{}, err
    }
    return obj.Hydrate(), err
}

func (obj ParentTest) Update(id string, _LA_MyChildTests []int, _LD_MyChildTests []int) (ParentTestHydrated,error) {
    _,err := DB.Exec(context.TODO(),"UPDATE ParentTest SET AnotherField = $1 WHERE ID = $2", obj.AnotherField, id)
    if err != nil {
        return ParentTestHydrated{}, err
    }
    obj.ID,err = strconv.Atoi(id)
    if err != nil {
        return ParentTestHydrated{}, err
    }
    for _,id := range _LD_MyChildTests {
        _,err = DB.Exec(context.TODO(),"DELETE FROM ParentTest_MyChildTests WHERE ParentTest_id = $1 AND MyChildTests = $2", obj.ID, id)
        if err != nil {
            return ParentTestHydrated{}, err
        }
    }
    for _,item := range _LA_MyChildTests {
        println("running SQL to insert to list: INSERT INTO ParentTest_MyChildTests (ParentTest_id, MyChildTests) VALUES ($1, $2)", obj.ID, item)
        _,err = DB.Exec(context.TODO(),"INSERT INTO ParentTest_MyChildTests (ParentTest_id, MyChildTests) VALUES ($1, $2)", obj.ID, item)
        if err != nil {
            return ParentTestHydrated{}, err
        }
    }
    return obj.Hydrate(), err
}

func DeleteParentTest(id string) error {
    _, err := DB.Exec(context.TODO(),"DELETE FROM ParentTest WHERE ID = $1", id)
    if err != nil {
        return err
    }
    _, err = DB.Exec(context.TODO(),"DELETE FROM ParentTest_MyChildTests WHERE ParentTest_id = $1", id)
    if err != nil {
        return err
    }
    return err
}
