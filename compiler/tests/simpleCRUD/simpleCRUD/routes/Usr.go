package routes

import (
    "net/http"

    "github.com/gin-gonic/gin"

    "simpleCRUD/objects"
)
func CreateUsr_route(c *gin.Context) {
    var new_Usr objects.Usr
    c.BindJSON(&new_Usr)
    ret_Usr,err := objects.CreateUsr(new_Usr)
    if err != nil {
        panic(err)
    }
    c.JSON(http.StatusOK, ret_Usr)
}

func ReadUsr_route(c *gin.Context) {
    id := c.Param("id")
    new_Usr, err := objects.ReadUsr(id)
    if err != nil && err.Error() == "no rows in result set" {
        c.JSON(http.StatusNotFound, gin.H{"status": "not found"})
        return
    }
    if err != nil {
        panic(err)
    }
    c.JSON(http.StatusOK, new_Usr)
}
func UpdateUsr_route(c *gin.Context) {
    var new_Usr objects.Usr
    c.BindJSON(&new_Usr)
    ret_Usr,err := objects.UpdateUsr(new_Usr)
    if err != nil {
        panic(err)
    }
    c.JSON(http.StatusOK, ret_Usr)
}
func DeleteUsr_route(c *gin.Context) {
    type deleteRequest struct {
        ID string
    }
    var req deleteRequest
    c.BindJSON(&req)
    err := objects.DeleteUsr(req.ID)
    if err != nil {
        panic(err)
    }
    c.JSON(http.StatusOK, gin.H{"status": "ok"})
}
