package main

import (
	"fmt"
	co "hakuGO/goControllers"
	vi "hakuGO/goViews"
	"os"
)

func main() {
	createFolders()
	display()
}

func display() {
	c := co.GetList("character")
	l := co.GetList("lightcone")
	r := co.GetList("relicset")
	fmt.Println("New Items:")
	n := co.GetNew()
	vi.GetApp(c, l, r, n)
}

func createFolders() {
	l1Folders := []string{"./_results/", "./_changes/"}
	l2Folders := []string{"character/", "lightcone/", "relicset/"}

	for _, l1 := range l1Folders {
		for _, l2 := range l2Folders {
			path := fmt.Sprintf("%s%s", l1, l2)
			if _, err := os.Stat(path); os.IsNotExist(err) {
				err := os.MkdirAll(path, os.ModeAppend)
				if err != nil {
					fmt.Println(err)
				}
			}
		}
	}
}
