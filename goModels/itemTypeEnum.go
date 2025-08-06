package models

type ItemHSR int

const (
	CHARACTER ItemHSR = iota
	LIGHTCONE
	RELICSET
)

func (s ItemHSR) String() string {
	switch s {
	case CHARACTER:
		return "character"
	case LIGHTCONE:
		return "lightcone"
	case RELICSET:
		return "relicset"
	}
	return "unknown"
}
