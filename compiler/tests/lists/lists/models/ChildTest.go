package models

import (
   "context"
   "strconv"
   "lists/derived"
)
type ChildTest struct {
    MyName string
    MyValue int
ID int
}
type ChildTestHydrated struct {
    MyList []string
    MyName string
    MyValue int
    MyValueMore int
    CapitalMyList []string
ID int
}

func (obj ChildTest) FetchList_MyList() ([]string) {
println("fetching list for MyList")
    ret := make([]string,0)
    rows,err := DB.Query(context.TODO(),"SELECT MyList FROM ChildTest_MyList WHERE ChildTest_id = $1", obj.ID)
    if err != nil {
        return []string{}
    }
    for rows.Next() {
    println("got a list item for MyList")
        var temp string
        err = rows.Scan(&temp)
        if err != nil {
            continue
        }
        ret = append(ret,temp)
    }
    return ret
}

func (obj ChildTest) Hydrate() ChildTestHydrated {
    _L_MyList := obj.FetchList_MyList()
    return ChildTestHydrated{
      MyList: _L_MyList,
      MyName: obj.MyName,
      MyValue: obj.MyValue,
      MyValueMore: derived.PlusFunc(obj.MyValue, 10),
      CapitalMyList: derived.Capitalize_all(_L_MyList),
        ID: obj.ID,
    }
}

func (obj ChildTest) Create() (ChildTestHydrated, error) {
    err := DB.QueryRow(context.TODO(),"INSERT INTO ChildTest (MyName, MyValue) VALUES ($1, $2) RETURNING ID", obj.MyName, obj.MyValue).Scan(&obj.ID)
    if err != nil {
        return ChildTestHydrated{}, err
    }
    return obj.Hydrate(), err
}

func ReadChildTest(id string) (ChildTestHydrated, error) {
    var obj ChildTest
    int_id,erro := strconv.Atoi(id)
    if erro != nil {
        return ChildTestHydrated{}, erro
    }
    obj.ID = int_id
    err := DB.QueryRow(context.TODO(),"SELECT MyName, MyValue FROM ChildTest WHERE ID = $1", id).Scan(&obj.MyName, &obj.MyValue)
    if err != nil {
        return ChildTestHydrated{}, err
    }
    return obj.Hydrate(), err
}

func (obj ChildTest) Update(id string, _LA_MyList []string, _LD_MyList []int) (ChildTestHydrated,error) {
    _,err := DB.Exec(context.TODO(),"UPDATE ChildTest SET MyName = $1, MyValue = $2 WHERE ID = $3", obj.MyName, obj.MyValue, id)
    if err != nil {
        return ChildTestHydrated{}, err
    }
    obj.ID,err = strconv.Atoi(id)
    if err != nil {
        return ChildTestHydrated{}, err
    }
    for _,id := range _LD_MyList {
        _,err = DB.Exec(context.TODO(),"DELETE FROM ChildTest_MyList WHERE ChildTest_id = $1 AND MyList = $2", obj.ID, id)
        if err != nil {
            return ChildTestHydrated{}, err
        }
    }
    for _,item := range _LA_MyList {
        println("running SQL to insert to list: INSERT INTO ChildTest_MyList (ChildTest_id, MyList) VALUES ($1, $2)", obj.ID, item)
        _,err = DB.Exec(context.TODO(),"INSERT INTO ChildTest_MyList (ChildTest_id, MyList) VALUES ($1, $2)", obj.ID, item)
        if err != nil {
            return ChildTestHydrated{}, err
        }
    }
    return obj.Hydrate(), err
}

func DeleteChildTest(id string) error {
    _, err := DB.Exec(context.TODO(),"DELETE FROM ChildTest WHERE ID = $1", id)
    if err != nil {
        return err
    }
    _, err = DB.Exec(context.TODO(),"DELETE FROM ChildTest_MyList WHERE ChildTest_id = $1", id)
    if err != nil {
        return err
    }
    return err
}
