package controllers

import (
	"bytes"
	"encoding/json"
	"fmt"
	mo "hakuGO/goModels"
	"log"
	"os"
	"os/exec"
	"strings"
)

// practice for Python integration
type Response struct {
	Typ     string         `json:"typ"`
	Id      string         `json:"id"`
	Name    string         `json:"name"`
	Num     int            `json:"num"`
	Struct  map[string]any `json:"struct"`
	Changes map[string]any `json:"changes,omitempty"`
}

/*
TODO:

1.
- split ids into types (char, lc, relic)
- check if files already saved for them
- if so, pass char label(?) AND IDs AND existing data e.g. {type: char, data: struct|None} to Python
- [also pass relic struct OR get it from python as Step 0]
-- nested struct -> {character: {{id: x, data: y|None}, {id: a, data: b|None}}, lightcone: {}, relicset: {}, relicData: {}}

2.
- python fetches data from apis
- does comparisons
- if changed, return new file AND change {type: char, data: struct|None, changes: struct|None}
-- nested struct -> {character: {{id: x, data: struct|None, changes: struct|None}}, lightcone: {}, relicset: {}}
- else return nothing

3.
- save structs in folders
*/

func CallPython(selected []string) (string, Response, error) {
	args := strings.Join(selected, " ")
	cmd := exec.Command("python", "./pythonPart.py", args)
	var resp Response

	// set where output goes to
	var stdout bytes.Buffer
	cmd.Stdout = &stdout

	// run command
	err := cmd.Run()
	if err != nil {
		return "", resp, fmt.Errorf("run error: %v", err)
	}

	// unmarshal response
	err = json.Unmarshal(stdout.Bytes(), &resp)
	if err != nil {
		return "", resp, fmt.Errorf("json error: %v", err)
	}

	fmt.Println(resp)
	output := fmt.Sprintf("%s: %d", args, resp.Num)
	return output, resp, nil
}

func JsonFileTest() (map[string]any, error) {
	// define output in advance
	var outcome map[string]any

	// read file
	fileName := "./_C1408_Phainon.json"
	content, err := os.ReadFile(fileName)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(string(content))

	// set cmd location
	cmd := exec.Command("python", "./pythonJson.py")
	// set cmd's input and output
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stdin = bytes.NewReader(content)
	cmd.Stderr = &stderr

	// run cmd
	err = cmd.Run()
	if err != nil {
		return outcome, fmt.Errorf("run error: %v", err)
	}

	// unmarshal to outcome
	err = json.Unmarshal(stdout.Bytes(), &outcome)
	if err != nil {
		return outcome, fmt.Errorf("unmarshal error: %v", err)
	}

	return outcome, nil
}

func JsonRawFile() (json.RawMessage, error) {
	// define output in advance
	var outcome json.RawMessage

	// read file
	fileName := "./_C1408_Phainon.json"
	content, err := os.ReadFile(fileName)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(string(content))

	// set cmd location
	cmd := exec.Command("python", "./pythonJson.py")
	// set cmd's input and output
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stdin = bytes.NewReader(content)
	cmd.Stderr = &stderr

	// run cmd
	err = cmd.Run()
	if err != nil {
		return outcome, fmt.Errorf("run error: %v", err)
	}

	// unmarshal to outcome
	err = json.Unmarshal(stdout.Bytes(), &outcome)
	if err != nil {
		return outcome, fmt.Errorf("unmarshal error: %v", err)
	}

	return outcome, nil
}

func ContactPython(req mo.Request) (mo.Request, error) {
	// define output in advance
	var outcome mo.Request

	// marshal req to json
	reqJson, err := json.Marshal(req)
	if err != nil {
		return outcome, fmt.Errorf("marshal error %w", err)
	}

	// set cmd location
	// os.Setenv("PYTHONPATH", "C:\\Users\\surya\\AppData\\Local\\Packages\\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\\LocalCache\\local-packages\\Python310\\Scripts\"")
	cmd := exec.Command("python", "./golangEntryPoint.py")
	// set cmd's input and output
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stdin = bytes.NewReader(reqJson)
	cmd.Stderr = &stderr

	// run cmd
	err = cmd.Run()
	if err != nil {
		return outcome, fmt.Errorf("run error: %v", err)
	}

	// unmarshal to outcome
	err = json.Unmarshal(stdout.Bytes(), &outcome)
	if err != nil {
		return outcome, fmt.Errorf("unmarshal error: %v| %s", err, stdout.String())
	}

	// todo: write to files
	// changes need to be timestamped AND with duplication enabled

	return outcome, nil
}

func PassDataTest() (mo.Request, error) {
	relics := GetList("relicset")

	// read files
	// character
	fileName := "./_C1408_Phainon.json"
	phainon, err := os.ReadFile(fileName)
	if err != nil {
		log.Fatal(err)
	}

	var ph mo.CharacterObj
	err = json.Unmarshal(phainon, &ph)
	if err != nil {
		log.Fatal(err)
	}

	obj := mo.PyObj{
		Id:   "1408",
		Item: ph,
	}

	// lightcone
	fileName = "./_L22005_The Forever Victual.json"
	forever, err := os.ReadFile(fileName)
	if err != nil {
		log.Fatal(err)
	}

	var fo mo.LightconeObj
	err = json.Unmarshal(forever, &fo)
	if err != nil {
		log.Fatal(err)
	}

	obj2 := mo.PyObj{
		Id:   "22005",
		Item: fo,
	}

	// relicset
	fileName = "./_R126_Wavestrider Captain.json"
	wave, err := os.ReadFile(fileName)
	if err != nil {
		log.Fatal(err)
	}

	var wa mo.RelicsetObj
	err = json.Unmarshal(wave, &wa)
	if err != nil {
		log.Fatal(err)
	}

	obj3 := mo.PyObj{
		Id:   "126",
		Item: wa,
	}

	// create request obj
	req := mo.Request{
		Character: []mo.PyObj{obj},
		Lightcone: []mo.PyObj{obj2},
		Relicset:  []mo.PyObj{obj3},
		Relics:    relics,
	}

	return ContactPython(req)
}
