package routes

import (
   "github.com/gin-gonic/gin"
   "log"

   "simpleCRUD/models"
)
func CreateUsr_route(c *gin.Context) {
    var obj models.Usr
    c.BindJSON(&obj)
    log.Println("Creating object: ", obj)
    obj_hydrated, err := obj.Create()
    if err != nil {
        log.Println("Error creating object: ", err)
        c.JSON(500, err)
        return
    }
    c.JSON(200, obj_hydrated)
}
func ReadUsr_route(c *gin.Context) {
    id := c.Param("id")
    obj, err := models.ReadUsr(id)
    if err != nil {
        if err.Error() == "no rows in result set" {
            c.JSON(404, "Object not found")
            return
        }
        log.Println("Error reading object: ", err)
        c.JSON(500, err)
        return
    }
    c.JSON(200, obj)
}
func UpdateUsr_route(c *gin.Context) {
    id := c.Param("id")
    var obj models.Usr
    c.BindJSON(&obj)
    obj_hydrated, err := obj.Update(id)
    if err != nil {
        if err.Error() == "no rows in result set" {
            c.JSON(404, "Object not found")
            return
        }
        log.Println("Error updating object: ", err)
        c.JSON(500, err)
        return
    }
    c.JSON(200, obj_hydrated)
}
func DeleteUsr_route(c *gin.Context) {
    id := c.Param("id")
    err := models.DeleteUsr(id)
    if err != nil {
        if err.Error() == "no rows in result set" {
            c.JSON(404, "Object not found")
            return
        }
        log.Println("Error deleting object: ", err)
        c.JSON(500, err)
        return
    }
    log.Println("Deleted object with id: ", id)
    c.JSON(200, "Deleted")
}
func CreateItm_route(c *gin.Context) {
    var obj models.Itm
    c.BindJSON(&obj)
    log.Println("Creating object: ", obj)
    obj_hydrated, err := obj.Create()
    if err != nil {
        log.Println("Error creating object: ", err)
        c.JSON(500, err)
        return
    }
    c.JSON(200, obj_hydrated)
}
func ReadItm_route(c *gin.Context) {
    id := c.Param("id")
    obj, err := models.ReadItm(id)
    if err != nil {
        if err.Error() == "no rows in result set" {
            c.JSON(404, "Object not found")
            return
        }
        log.Println("Error reading object: ", err)
        c.JSON(500, err)
        return
    }
    c.JSON(200, obj)
}
func UpdateItm_route(c *gin.Context) {
    id := c.Param("id")
    var obj models.Itm
    c.BindJSON(&obj)
    obj_hydrated, err := obj.Update(id)
    if err != nil {
        if err.Error() == "no rows in result set" {
            c.JSON(404, "Object not found")
            return
        }
        log.Println("Error updating object: ", err)
        c.JSON(500, err)
        return
    }
    c.JSON(200, obj_hydrated)
}
func DeleteItm_route(c *gin.Context) {
    id := c.Param("id")
    err := models.DeleteItm(id)
    if err != nil {
        if err.Error() == "no rows in result set" {
            c.JSON(404, "Object not found")
            return
        }
        log.Println("Error deleting object: ", err)
        c.JSON(500, err)
        return
    }
    log.Println("Deleted object with id: ", id)
    c.JSON(200, "Deleted")
}
