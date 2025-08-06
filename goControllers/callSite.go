package controllers

import (
	"encoding/json"
	"fmt"
	mo "hakuGO/goModels"
	"io"
	"log"
	"maps"
	"net/http"
	"slices"
	"strconv"
)

func GetList(tag string) mo.ItemMap {
	url := fmt.Sprintf("https://api.hakush.in/hsr/data/%s.json", tag)

	resp, err := http.Get(url)
	if err != nil {
		log.Fatal(err)
	}

	content := resp.Body
	if content != nil {
		// shut everything down once finished
		defer content.Close()
	}

	body, err := io.ReadAll(content)
	if err != nil {
		log.Fatal(err)
	}

	var items mo.ItemMap
	jsonErr := json.Unmarshal(body, &items)
	if jsonErr != nil {
		log.Fatal(jsonErr)
	}

	// default map implementation is hashmap,
	// so keys need to be sorted manually
	keys := slices.Sorted(maps.Keys(items))

	// fmt.Printf("%s\n", tag)
	for _, k := range keys {
		if tag == "character" {
			tbName := fixName(k)
			if tbName != "" {
				tb := items[k]
				tb.Name = tbName
				items[k] = tb
			}
		}
		// fmt.Println(k, ":", items[k].Name)
	}
	// fmt.Println()

	return items
}

func GetNew() mo.NewLists {
	url := "https://api.hakush.in/hsr/new.json"

	resp, err := http.Get(url)
	if err != nil {
		log.Fatal(err)
	}

	content := resp.Body
	if content != nil {
		defer content.Close()
	}

	body, err := io.ReadAll(content)
	if err != nil {
		log.Fatal(err)
	}

	var clr mo.NewLists
	jsonErr := json.Unmarshal(body, &clr)
	if jsonErr != nil {
		log.Fatal(jsonErr)
	}

	fmt.Println(clr.Character)
	fmt.Println(clr.Lightcone)
	fmt.Println(clr.Relicset)

	return clr

}

func fixName(key string) string {
	id, err := strconv.Atoi(key)
	var gender string
	var element string
	if err != nil {
		return ""
	}
	// check March 7th types
	mar7th := map[int]string{
		1001: "March 7th (Ice, Preservation)",
		1224: "March 7th (Imaginary, Hunt)",
	}

	found, ok := mar7th[id]
	if ok {
		return found
	}

	// return if id is char & not TB (< 8001) OR id is not char (> 9999)
	if id < 8001 || id > 9999 {
		return ""
	} else {
		// get gender (even = F, odd = M)
		if id%2 == 0 {
			gender = "F"
		} else {
			gender = "M"
		}

		// get element
		if id < 8003 {
			element = "Des"
		} else if id < 8005 {
			element = "Pre"
		} else if id < 8007 {
			element = "Har"
		} else {
			element = "Rem"
		}

		name := fmt.Sprintf("Trailblazer %s (%s)", element, gender)
		return name
	}
}
