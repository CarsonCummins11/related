package objects

import (
    "net/http"

    "github.com/gin-gonic/gin"
)
type t2 struct {
    name string
    things t1
    videos string
    ID string
}
func Createt2_route(c *gin.Context) {
    var new_t2 t2
    c.BindJSON(&new_t2)
    //TODO: insert obj into db
    c.JSON(http.StatusOK, gin.H{"status": "ok"})
}

func Readt2_route(c *gin.Context) {
    //TODO: read obj from db
    c.JSON(http.StatusOK, gin.H{"status": "ok"})
}
func Updatet2_route(c *gin.Context) {
    //TODO: update obj
    c.JSON(http.StatusOK, gin.H{"status": "ok"})
}
func Deletet2_route(c *gin.Context) {
    //TODO: delete obj
    c.JSON(http.StatusOK, gin.H{"status": "ok"})
}
