package models

import (
   "context"
   "strconv"
   "simpleCRUD/derived"
)
type Itm struct {
    Name string
    Value int
ID int
}
type ItmHydrated struct {
    Name string
    Value int
    DoubleValue int
ID int
}

func (obj Itm) Hydrate() ItmHydrated {
    return ItmHydrated{
      Name: obj.Name,
      Value: obj.Value,
      DoubleValue: derived.Times2(obj.Value),
        ID: obj.ID,
    }
}

func (obj Itm) Create() (ItmHydrated, error) {
    err := DB.QueryRow(context.TODO(),"INSERT INTO Itm (Name, Value) VALUES ($1, $2) RETURNING ID", obj.Name, obj.Value).Scan(&obj.ID)
    if err != nil {
        return ItmHydrated{}, err
    }
    return obj.Hydrate(), err
}

func ReadItm(id string) (ItmHydrated, error) {
    var obj Itm
    int_id,erro := strconv.Atoi(id)
    if erro != nil {
        return ItmHydrated{}, erro
    }
    obj.ID = int_id
    err := DB.QueryRow(context.TODO(),"SELECT Name, Value FROM Itm WHERE ID = $1", id).Scan(&obj.Name, &obj.Value)
    if err != nil {
        return ItmHydrated{}, err
    }
    return obj.Hydrate(), err
}

func (obj Itm) Update(id string) (ItmHydrated,error) {
    _,err := DB.Exec(context.TODO(),"UPDATE Itm SET Name = $1, Value = $2 WHERE ID = $3", obj.Name, obj.Value, id)
    if err != nil {
        return ItmHydrated{}, err
    }
    obj.ID,err = strconv.Atoi(id)
    if err != nil {
        return ItmHydrated{}, err
    }
    return obj.Hydrate(), err
}

func DeleteItm(id string) error {
    _, err := DB.Exec(context.TODO(),"DELETE FROM Itm WHERE ID = $1", id)
    if err != nil {
        return err
    }
    return err
}
