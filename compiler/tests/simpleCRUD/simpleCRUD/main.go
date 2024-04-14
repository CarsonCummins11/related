package main

import (
   "github.com/gin-gonic/gin"
   "simpleCRUD/routes"
)

func main() {
   router := gin.Default()

  Usr := router.Group("/Usr")
  Usr.POST("/create", routes.CreateUsr_route)
  Usr.GET("/read/:id", routes.ReadUsr_route)
  Usr.PUT("/update/:id", routes.UpdateUsr_route)
  Usr.DELETE("/delete/:id", routes.DeleteUsr_route)
  Itm := router.Group("/Itm")
  Itm.POST("/create", routes.CreateItm_route)
  Itm.GET("/read/:id", routes.ReadItm_route)
  Itm.PUT("/update/:id", routes.UpdateItm_route)
  Itm.DELETE("/delete/:id", routes.DeleteItm_route)
router.Run("localhost:8080")
}
