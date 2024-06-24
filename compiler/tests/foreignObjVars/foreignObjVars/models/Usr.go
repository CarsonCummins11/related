package models

import (
   "context"
   "strconv"
   "foreignObjVars/derived"
)
type Usr struct {
    Name string
    Item int
ID int
}
type UsrHydrated struct {
    Name string
    Item ItmHydrated
    QuadValue int
ID int
}

func (obj Usr) Hydrate() UsrHydrated {
    Item, err := ReadItm(strconv.Itoa(obj.Item))
    if err != nil {
        panic(err)
    }
    return UsrHydrated{
      Name: obj.Name,
      Item: Item,
      QuadValue: derived.Times2(Item.DoubleValue),
        ID: obj.ID,
    }
}

func (obj Usr) Create() (UsrHydrated, error) {
    err := DB.QueryRow(context.TODO(),"INSERT INTO Usr (Name, Item) VALUES ($1, $2) RETURNING ID", obj.Name, obj.Item).Scan(&obj.ID)
    if err != nil {
        return UsrHydrated{}, err
    }
    return obj.Hydrate(), err
}

func ReadUsr(id string) (UsrHydrated, error) {
    var obj Usr
    int_id,erro := strconv.Atoi(id)
    if erro != nil {
        return UsrHydrated{}, erro
    }
    obj.ID = int_id
    err := DB.QueryRow(context.TODO(),"SELECT Name, Item FROM Usr WHERE ID = $1", id).Scan(&obj.Name, &obj.Item)
    if err != nil {
        return UsrHydrated{}, err
    }
    return obj.Hydrate(), err
}

func (obj Usr) Update(id string) (UsrHydrated,error) {
    _,err := DB.Exec(context.TODO(),"UPDATE Usr SET Name = $1, Item = $2 WHERE ID = $3", obj.Name, obj.Item, id)
    if err != nil {
        return UsrHydrated{}, err
    }
    obj.ID,err = strconv.Atoi(id)
    if err != nil {
        return UsrHydrated{}, err
    }
    return obj.Hydrate(), err
}

func DeleteUsr(id string) error {
    _, err := DB.Exec(context.TODO(),"DELETE FROM Usr WHERE ID = $1", id)
    if err != nil {
        return err
    }
    return err
}
