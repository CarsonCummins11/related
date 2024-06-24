package main

import (
   "github.com/gin-gonic/gin"
   "lists/routes"
)

func main() {
   router := gin.Default()

  ChildTest := router.Group("/ChildTest")
  ChildTest.POST("/create", routes.CreateChildTest_route)
  ChildTest.GET("/read/:id", routes.ReadChildTest_route)
  ChildTest.PUT("/update/:id", routes.UpdateChildTest_route)
  ChildTest.DELETE("/delete/:id", routes.DeleteChildTest_route)
  ParentTest := router.Group("/ParentTest")
  ParentTest.POST("/create", routes.CreateParentTest_route)
  ParentTest.GET("/read/:id", routes.ReadParentTest_route)
  ParentTest.PUT("/update/:id", routes.UpdateParentTest_route)
  ParentTest.DELETE("/delete/:id", routes.DeleteParentTest_route)
router.Run("localhost:8080")
}
