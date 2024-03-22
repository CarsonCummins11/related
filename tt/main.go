package main

import (
    "github.com/gin-gonic/gin"
    "tt/objects"
)

func main() {
    router := gin.Default()

    t1 := router.Group("/t1")
    t1.POST("/create", objects.Createt1_route)
    t1.GET("/read", objects.Readt1_route)
    t1.POST("/update", objects.Updatet1_route)
    t1.POST("/delete", objects.Deletet1_route)

    t2 := router.Group("/t2")
    t2.POST("/create", objects.Createt2_route)
    t2.GET("/read", objects.Readt2_route)
    t2.POST("/update", objects.Updatet2_route)
    t2.POST("/delete", objects.Deletet2_route)


    router.Run("localhost:8080")
}
