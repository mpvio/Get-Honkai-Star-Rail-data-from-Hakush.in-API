package controllers

import (
	"strings"

	mo "hakuGO/goModels"

	"fyne.io/fyne/v2/widget"
)

// remove duplicates from selected
func RemoveDuplicate[T comparable](sliceList []T) []T {
	allKeys := make(map[T]bool)
	list := []T{}
	for _, item := range sliceList {
		if _, value := allKeys[item]; !value {
			allKeys[item] = true
			list = append(list, item)
		}
	}
	return list
}

func GetNamesFromMap(group []*widget.CheckGroup, im mo.ItemMap, typ mo.ItemHSR) ([]string, []mo.PyObj) {
	var output []string
	for _, check := range group {
		for _, str := range check.Selected {
			s, _, _ := strings.Cut(str, ":")
			//name := im[s].Name
			output = append(output, s)
		}
	}

	return RemoveDuplicate(output), getFiles(output, im, typ)
}

func GetStringForLabel(response []mo.ResponseTuple) string {
	outputs := []string{}

	for _, r := range response {
		outputs = append(outputs, r.Output)
	}

	return strings.Join(outputs, "\n")
}
