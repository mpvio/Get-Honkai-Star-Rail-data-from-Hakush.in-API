package views

import (
	"fmt"
	"slices"
	"strconv"

	co "hakuGO/goControllers"
	mo "hakuGO/goModels"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/widget"
)

func GetApp(c mo.ItemMap, l mo.ItemMap, r mo.ItemMap, n mo.NewLists) {
	a := app.New()
	w := a.NewWindow("Lists")

	chr, chrGroup, _ := makeCheckWidgetGeneric(c)
	lie, lieGroup, _ := makeCheckWidgetGeneric(l)
	ret, retGroup, _ := makeCheckWidgetGeneric(r)

	lists := container.NewGridWithColumns(3, chr, lie, ret)
	updates, updateGroups := makeNewListsWidget(n)

	// make three groups
	chs := []*widget.CheckGroup{chrGroup, updateGroups[0]}
	lcs := []*widget.CheckGroup{lieGroup, updateGroups[1]}
	rss := []*widget.CheckGroup{retGroup, updateGroups[2]}
	// make super group
	all := [][]*widget.CheckGroup{chs, lcs, rss}

	// using vsplit with offset
	top := container.NewVSplit(lists, updates)
	top.Offset = 0.8

	// buttons & results
	results := widget.NewLabel("")

	confirmFunction := func() {
		_, chObj := co.GetNamesFromMap(chs, c, mo.CHARACTER)
		_, lcObj := co.GetNamesFromMap(lcs, l, mo.LIGHTCONE)
		_, rsObj := co.GetNamesFromMap(rss, r, mo.RELICSET)
		//output := fmt.Sprintf("chars: %v, cones: %v, sets: %v", _ch, _lc, _rs)
		//_results.SetText(output)

		reqObj := mo.Request{
			Character: chObj,
			Lightcone: lcObj,
			Relicset:  rsObj,
			Relics:    r,
		}

		resp, err := co.ContactPython(reqObj)
		if err != nil {
			fmt.Println(err)
		}
		// fmt.Println(resp.Character)
		// fmt.Println(resp.Lightcone)
		// fmt.Println(resp.Relicset)

		// write to files and write result to ui
		finalResult := co.WriteResponseToFiles(resp, c, l, r)
		labelString := co.GetStringForLabel(finalResult)
		results.SetText(labelString)

		for _, character := range resp.Character {
			fmt.Println(character.Id, character.HasChanges())
		}
		fmt.Println(resp.Summary)
	}
	confirm := widget.NewButton("Query", confirmFunction)

	clear := widget.NewButton("Clear", func() {
		// clear all checkgroups
		for _, cg := range all {
			for _, g := range cg {
				g.SetSelected([]string{})
			}
		}
		results.SetText("")
	})

	resultsScroll := container.NewVScroll(results)
	buttons := container.NewCenter(container.NewHBox(confirm, clear))
	bottom := container.NewVSplit(buttons, resultsScroll)
	bottom.Offset = 0.1

	content := container.NewVSplit(top, bottom)
	content.Offset = 0.8

	w.SetContent(content)
	w.Resize(fyne.NewSize(1200, 700))

	w.ShowAndRun()
}

func makeNewListsWidget(items mo.NewLists) (*fyne.Container, []*widget.CheckGroup) {
	chr, chrGroup, _ := makeCheckWidgetGeneric(items.Character)
	lie, lieGroup, _ := makeCheckWidgetGeneric(items.Lightcone)
	ret, retGroup, _ := makeCheckWidgetGeneric(items.Relicset)

	groups := []*widget.CheckGroup{chrGroup, lieGroup, retGroup}
	lists := container.NewGridWithColumns(3, chr, lie, ret)
	return lists, groups
}

func makeCheckWidgetGeneric[T any](input T) (*container.Scroll, *widget.CheckGroup, error) {
	var options []string

	switch any(input).(type) {
	case []int:
		nums := any(input).([]int)
		options = make([]string, 0, len(nums))
		for _, num := range nums {
			options = append(options, strconv.Itoa(num))
		}
	case mo.ItemMap:
		items := any(input).(mo.ItemMap)
		options = make([]string, 0, len(items))
		for k, item := range items {
			options = append(options, fmt.Sprintf("%s: %s", k, item.Name))
		}
		slices.Sort(options)
	default:
		return nil, nil, fmt.Errorf("invalid type: %T", input)
	}

	group := widget.NewCheckGroup(options, nil)
	return container.NewVScroll(group), group, nil
}
