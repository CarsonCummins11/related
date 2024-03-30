package objects

import (
    "context"
   "simpleCRUD/database"
)

type Usr struct {
    Name string
    Item Itm
    ID string
}

type UsrHydrated struct {
    Name string
    Item Itm
    Tr bool
    S string
    N int
    W float64
    ID string
}

func hydrateUsr(obj Usr) (UsrHydrated,error) {
    new_obj_hydrated := UsrHydrated{}
    err := database.DB.QueryRow(context.Background(), "SELECT * FROM Usr WHERE ID = $1 Limit 1", obj.ID).Scan(
        &obj.Name,
        &obj.Item,
        &obj.ID)
    new_obj.Name = obj.Name
    new_obj.Item = obj.Item
    new_obj.Tr = true
    new_obj.S = "a string here"
    new_obj.N = 55
    new_obj.W = 42.123
    new_obj.ID = obj.ID
    return new_obj
}

func CreateUsr(obj Usr) (UsrHydrated, error) {
    ret_obj := hydrateUsr(obj)
    database.DB.QueryRow(context.Background(), "INSERT INTO Usr (Name,Item,Tr,S,N,W) VALUES ($1,$2,$3,$4,$5,$6) RETURNING ID",
        ret_obj.Name,
        ret_obj.Item,
        ret_obj.Tr,
        ret_obj.S,
        ret_obj.N,
        ret_obj.W,
    ).Scan(&ret_obj.ID)
    return ret_obj, nil
}

func ReadUsr(id string) (UsrHydrated, error) {
    var obj UsrHydrated
    err := database.DB.QueryRow(context.Background(), "SELECT * FROM Usr WHERE ID = $1", id).Scan(
        &obj.Name,
        &obj.Item,
        &obj.Tr,
        &obj.S,
        &obj.N,
        &obj.W,
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

