package routes

import (
   "github.com/gin-gonic/gin"
   "log"

   "lists/models"
)
func CreateChildTest_route(c *gin.Context) {
    var obj models.ChildTest
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
func ReadChildTest_route(c *gin.Context) {
    id := c.Param("id")
    obj, err := models.ReadChildTest(id)
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
func UpdateChildTest_route(c *gin.Context) {
    id := c.Param("id")
    var obj struct{
      Obj models.ChildTest
      LA_MyList []string
      LD_MyList []int
    }
    c.BindJSON(&obj)
    log.Println("Updating object: ", obj)
    obj_hydrated, err := obj.Obj.Update(id,
        obj.LA_MyList,
        obj.LD_MyList,
    )
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
func DeleteChildTest_route(c *gin.Context) {
    id := c.Param("id")
    err := models.DeleteChildTest(id)
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
func CreateParentTest_route(c *gin.Context) {
    var obj models.ParentTest
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
func ReadParentTest_route(c *gin.Context) {
    id := c.Param("id")
    obj, err := models.ReadParentTest(id)
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
func UpdateParentTest_route(c *gin.Context) {
    id := c.Param("id")
    var obj struct{
      Obj models.ParentTest
      LA_MyChildTests []int
      LD_MyChildTests []int
    }
    c.BindJSON(&obj)
    log.Println("Updating object: ", obj)
    obj_hydrated, err := obj.Obj.Update(id,
        obj.LA_MyChildTests,
        obj.LD_MyChildTests,
    )
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
func DeleteParentTest_route(c *gin.Context) {
    id := c.Param("id")
    err := models.DeleteParentTest(id)
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
