package objects

import (
    "labelByID/derived"
    "context"
   "labelByID/database"
)

type Usr struct {
    Name string
    Item Itm
    ID string
}

type UsrHydrated struct {
    Name string
    Item Itm
    DoubleValue int
    ID string
}

func hydrateUsr(obj Usr) (UsrHydrated,error) {
    new_obj := UsrHydrated{}
    err := database.DB.QueryRow(context.Background(), "SELECT * FROM Usr WHERE ID = $1 Limit 1", obj.ID).Scan(
        &obj.Name,
        &obj.Item,
        &obj.ID)
    new_obj.Name = obj.Name
    new_obj.Item = obj.Item
    new_obj.DoubleValue = derived.Times2(retr_Item_Value,)
    new_obj.ID = obj.ID
    return new_obj
}

func CreateUsr(obj Usr) (UsrHydrated, error) {
    ret_obj := hydrateUsr(obj)
    database.DB.QueryRow(context.Background(), "INSERT INTO Usr (Name,Item,DoubleValue) VALUES ($1,$2,$3) RETURNING ID",
        ret_obj.Name,
        ret_obj.Item,
        ret_obj.DoubleValue,
    ).Scan(&ret_obj.ID)
    return ret_obj, nil
}

func ReadUsr(id string) (UsrHydrated, error) {
    var obj UsrHydrated
    err := database.DB.QueryRow(context.Background(), "SELECT * FROM Usr WHERE ID = $1", id).Scan(
        &obj.Name,
        &obj.Item,
        &obj.DoubleValue,
        &obj.ID,
    )
    if err != nil {
        return UsrHydrated{}, err
    }
    return obj, nil
}

func UpdateUsr(obj Usr) (UsrHydrated, error) {
    ret_obj := hydrateUsr(obj)
    return ret_obj, nil
}

func DeleteUsr(id string) error {
    database.DB.Exec(context.Background(), "DELETE FROM Usr WHERE ID = $1", id)
    return nil
}

