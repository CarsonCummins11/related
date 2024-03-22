package objects

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

type t1 struct {
	name string
	data string
	ID   string
}

func Createt1_route(c *gin.Context) {
	var new_t1 t1
	c.BindJSON(&new_t1)
	//TODO: insert obj into db
	c.JSON(http.StatusOK, gin.H{"status": "ok"})
}

func Readt1_route(c *gin.Context) {
	//TODO: read obj from db
	c.JSON(http.StatusOK, gin.H{"status": "ok"})
}
func Updatet1_route(c *gin.Context) {
	//TODO: update obj
	c.JSON(http.StatusOK, gin.H{"status": "ok"})
}
func Deletet1_route(c *gin.Context) {
	//TODO: delete obj
	c.JSON(http.StatusOK, gin.H{"status": "ok"})
}
