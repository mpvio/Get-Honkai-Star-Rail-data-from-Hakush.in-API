package models

type Item struct {
	Name string              `json:"en"`
	Set  map[string]RelicSet `json:"set,omitempty"`
}

type RelicSet struct {
	En        string `json:"en"`
	ParamList []any
}

type ItemMap = map[string]Item

type NewLists struct {
	Character []int
	Lightcone []int
	Relicset  []int
}
