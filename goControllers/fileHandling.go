package controllers

import (
	"bytes"
	"encoding/json"
	"fmt"
	mo "hakuGO/goModels"
	"os"
	"time"
)

func getFiles(ids []string, im mo.ItemMap, typ mo.ItemHSR) []mo.PyObj {
	folder := fmt.Sprintf("./_results/%s/", typ)
	var objs []mo.PyObj
	for _, id := range ids {
		name := im[id].Name
		fileName := fmt.Sprintf("%s%s.json", folder, name)
		content, err := os.ReadFile(fileName)

		if err != nil {
			fmt.Println(name, "not found")
		} else {
			fmt.Println(string(content))
		}

		var obj mo.PyObj

		switch typ {
		case mo.CHARACTER:

			var c mo.CharacterObj
			if err == nil {
				err = json.Unmarshal(content, &c)
			}
			if err == nil {
				obj = mo.PyObj{
					Id:   id,
					Item: c,
				}
				// // for testing only
				// // add changes file to Phainon and see if it renders properly
				// if id == "1408" {
				// 	obj = mo.PyObj{
				// 		Id:      id,
				// 		Item:    c,
				// 		Changes: changesTest(),
				// 	}
				// } else {
				// 	obj = mo.PyObj{
				// 		Id:   id,
				// 		Item: c,
				// 	}
				// }
			}

		case mo.LIGHTCONE:
			var l mo.LightconeObj
			if err == nil {
				err = json.Unmarshal(content, &l)
			}
			if err == nil {
				obj = mo.PyObj{
					Id:   id,
					Item: l,
				}
			}

		case mo.RELICSET:
			var r mo.RelicsetObj
			if err == nil {
				err = json.Unmarshal(content, &r)
			}
			if err == nil {
				obj = mo.PyObj{
					Id:   id,
					Item: r,
				}
			}

		default:
			continue
		}

		fmt.Println("----")
		if err != nil {
			// file wasn't found
			obj = mo.PyObj{
				Id: id,
			}
		}

		objs = append(objs, obj)

	}
	return objs
}

// looks through
func GiveNamesToResponses(responses []mo.ResponseTuple, c, l, r mo.ItemMap) []mo.ResponseTuple {
	for _, response := range responses {
		if !response.Written {
			var name string
			switch response.Typ {
			case "character":
				name = c[response.Id].Name
			case "lightcone":
				name = l[response.Id].Name
			default:
				name = r[response.Id].Name
			}
			response.Output = fmt.Sprintf("%s %s", name, response.Output)
		}
	}
	return responses
}

func GiveNameToResponse(response mo.ResponseTuple, im mo.ItemMap) string {
	return fmt.Sprintf("%s %s", im[response.Id].Name, response.Output)
}

func WriteResponseToFiles(resp mo.Request, c, l, r mo.ItemMap) []mo.ResponseTuple {
	results := []mo.ResponseTuple{}

	characters := writeOnePartOfResponseToFiles(resp.Character, "character", c)
	results = append(results, characters...)

	lightcones := writeOnePartOfResponseToFiles(resp.Lightcone, "lightcone", l)
	results = append(results, lightcones...)

	relicsets := writeOnePartOfResponseToFiles(resp.Relicset, "relicset", r)
	results = append(results, relicsets...)

	// write response to json too, for testing
	// var buf bytes.Buffer
	// encoder := json.NewEncoder(&buf)
	// encoder.SetEscapeHTML(false)
	// encoder.SetIndent("", "    ")
	// encoder.Encode(resp)
	// os.WriteFile("./sample.json", buf.Bytes(), 0644)

	return results
}

/*
func (p PyObj) GetItemByte() ([]byte, error) {
	// use buffer to retain symbols like ">"
	var buf bytes.Buffer
	// write to it with an encoder
	encoder := json.NewEncoder(&buf)
	encoder.SetEscapeHTML(false) // retains symbols
	encoder.SetIndent("", "    ")
	// encode data
	if err := encoder.Encode(p.Item); err != nil {
		return nil, err
	}
	// remove newline from encoder and return
	result := bytes.TrimSpace(buf.Bytes())
	return result, nil
}
*/

func writeOnePartOfResponseToFiles(objs []mo.PyObj, folder string, im mo.ItemMap) []mo.ResponseTuple {
	results := []mo.ResponseTuple{}
	for _, obj := range objs {
		current := writeToFolder(obj, folder)
		if !current.Written {
			current.Output = fmt.Sprintf("%s %s", im[current.Id].Name, current.Output)
		}
		results = append(results, current)
	}
	return results
}

/*
item Y, change N -> write item
item Y, change Y -> write item AND change
item N, change N -> abort [done]
item N, change Y -> error [done]
*/

// returns result message and "was something written"
func writeToFolder(item mo.PyObj, folder string) mo.ResponseTuple {
	hasChange, hasItem := item.HasChanges(), item.HasItem()

	if !hasChange && !hasItem {
		// if there is no change AND no item, there is nothing to do so
		// don't need to write anything (get item name from parent function)
		return mo.ResponseTuple{Output: "was unchanged.", Written: false, Typ: folder, Id: item.Id}
	}

	if !hasItem && hasChange {
		return mo.ResponseTuple{Output: "caused an error.", Written: false, Typ: folder, Id: item.Id}
	}

	// item.Item exists
	name := item.Item.GetMyName()

	// write main file
	filename := fmt.Sprintf("%s.json", name)
	filepath := fmt.Sprintf("./_results/%s/%s", folder, filename)
	obj, err := item.GetItemByte()
	if err != nil {
		return mo.ResponseTuple{Output: fmt.Sprintf("caused %s.", err.Error()), Written: false, Typ: folder, Id: item.Id}
	} else {
		os.WriteFile(filepath, obj, 0644)
	}

	endText := ""

	if hasChange {
		// write changes file
		tempPath := fmt.Sprintf("./_changes/%s/", folder)
		datedName := fmt.Sprintf("%s %s", name, time.Now().Format("06-01-02"))
		usableName, usablePath := findValidFilename(tempPath, datedName, 0)
		obj, err = item.GetChangesByte()
		if err != nil {
			endText = fmt.Sprintf(" created and %s.", err.Error())
		} else {
			os.WriteFile(usablePath, obj, 0644)
			endText = fmt.Sprintf(" updated and %s created.", usableName)
		}
	} else {
		endText = " created."
	}

	return mo.ResponseTuple{Output: fmt.Sprintf("%s%s", filename, endText), Written: true, Typ: folder, Id: item.Id}
}

func findValidFilename(path, name string, copy int) (string, string) {
	var filename string
	if copy == 0 {
		// try default name first
		filename = fmt.Sprintf("%s.json", name)
	} else {
		filename = fmt.Sprintf("%s (%d).json", name, copy)
	}

	// create and check filepath
	filepath := fmt.Sprintf("%s%s", path, filename)
	_, err := os.Stat(filepath)

	if err != nil && os.IsNotExist(err) {
		// this error was thrown because the attempted filename doesn't exist
		return filename, filepath
	} else {
		// else try again with copy incremented
		return findValidFilename(path, name, copy+1)
	}
}

func SaveJsonToFile(rawJSON json.RawMessage, filename string) error {
	// first convert to "pretty" []bytes
	var out bytes.Buffer
	json.Indent(&out, rawJSON, "", "    ")
	return saveBytesToFile(out.Bytes(), filename)
}

func saveBytesToFile(b []byte, filename string) error {
	return os.WriteFile(filename, b, 0644)
}

// // remove once finished testing
// func changesTest() *orderedmap.OrderedMap[string, any] {
// 	filepath := "./_changes/character/Phainon 25-08-04 (6).json"
// 	obj := orderedmap.New[string, any]()
// 	content, err := os.ReadFile(filepath)
// 	if err != nil {
// 		fmt.Println("read error:", err)
// 	}
// 	err = json.Unmarshal(content, &obj)
// 	if err != nil {
// 		fmt.Println("marshal error:", err)
// 	}
// 	return obj
// }
