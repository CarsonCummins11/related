package objects

import (
	"context"
	"simpleCRUD/database"
	"simpleCRUD/derived"
)

type Itm struct {
	Name  string
	Value int
	ID    string
}

type ItmHydrated struct {
	Name        string
	Value       int
	DoubleValue int
	ID          string
}

func hydrateItm(obj Itm) (ItmHydrated, error) {
	new_obj := ItmHydrated{}
	err := database.DB.QueryRow(context.Background(), "SELECT * FROM Itm WHERE ID = $1 Limit 1", obj.ID).Scan(
		&obj.Name,
		&obj.Value,
		&obj.ID)
	new_obj.Name = obj.Name
	new_obj.Value = obj.Value
	new_obj.DoubleValue = derived.Times2(obj.Value)
	new_obj.ID = obj.ID
	return new_obj
}

func CreateItm(obj Itm) (ItmHydrated, error) {
	ret_obj := hydrateItm(obj)
	database.DB.QueryRow(context.Background(), "INSERT INTO Itm (Name,Value,DoubleValue) VALUES ($1,$2,$3) RETURNING ID",
		ret_obj.Name,
		ret_obj.Value,
		ret_obj.DoubleValue,
	).Scan(&ret_obj.ID)
	return ret_obj, nil
}

func ReadItm(id string) (ItmHydrated, error) {
	var obj ItmHydrated
	err := database.DB.QueryRow(context.Background(), "SELECT * FROM Itm WHERE ID = $1", id).Scan(
		&obj.Name,
		&obj.Value,
		&obj.DoubleValue,
		&obj.ID,
	)
	if err != nil {
		return ItmHydrated{}, err
	}
	return obj, nil
}

func UpdateItm(obj Itm) (ItmHydrated, error) {
	ret_obj := hydrateItm(obj)
	return ret_obj, nil
}

func DeleteItm(id string) error {
	database.DB.Exec(context.Background(), "DELETE FROM Itm WHERE ID = $1", id)
	return nil
}
