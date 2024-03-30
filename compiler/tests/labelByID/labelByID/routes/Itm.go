package routes

import (
    "net/http"

    "github.com/gin-gonic/gin"

    "labelByID/objects"
)
func CreateItm_route(c *gin.Context) {
    var new_Itm objects.Itm
    c.BindJSON(&new_Itm)
    ret_Itm,err := objects.CreateItm(new_Itm)
    if err != nil {
        panic(err)
    }
    c.JSON(http.StatusOK, ret_Itm)
}

func ReadItm_route(c *gin.Context) {
    id := c.Param("id")
    new_Itm, err := objects.ReadItm(id)
    if err != nil && err.Error() == "no rows in result set" {
        c.JSON(http.StatusNotFound, gin.H{"status": "not found"})
        return
    }
    if err != nil {
        panic(err)
    }
    c.JSON(http.StatusOK, new_Itm)
}
func UpdateItm_route(c *gin.Context) {
    var new_Itm objects.Itm
    c.BindJSON(&new_Itm)
    ret_Itm,err := objects.UpdateItm(new_Itm)
    if err != nil {
        panic(err)
    }
    c.JSON(http.StatusOK, ret_Itm)
}
func DeleteItm_route(c *gin.Context) {
    type deleteRequest struct {
        ID string
    }
    var req deleteRequest
    c.BindJSON(&req)
    err := objects.DeleteItm(req.ID)
    if err != nil {
        panic(err)
    }
    c.JSON(http.StatusOK, gin.H{"status": "ok"})
}
