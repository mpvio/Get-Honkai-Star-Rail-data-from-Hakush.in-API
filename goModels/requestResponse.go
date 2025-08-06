package models

import (
	"bytes"
	"encoding/json"
	"fmt"

	orderedmap "github.com/wk8/go-ordered-map/v2"
)

type Request struct {
	Character []PyObj `json:"character,omitempty"`
	Lightcone []PyObj `json:"lightcone,omitempty"`
	Relicset  []PyObj `json:"relicset,omitempty"`
	Relics    ItemMap `json:"relics,omitempty"`
	Summary   string  `json:"Summary,omitempty"` // testing only
}

func (r Request) String() string {
	jsonData, err := json.MarshalIndent(r, "", "    ")
	if err != nil {
		return fmt.Sprintf("error formatting PyObj: %v", err)
	}
	return string(jsonData)
}

type PyObj struct {
	Id      string                              `json:"id"`
	Item    AnyItem                             `json:"item,omitempty,omitzero"`
	Changes *orderedmap.OrderedMap[string, any] `json:"changes,omitzero"`
}

func (p PyObj) String() string {
	jsonData, err := json.MarshalIndent(p, "", "    ")
	if err != nil {
		return fmt.Sprintf("error formatting PyObj: %v", err)
	}
	return string(jsonData)
}

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

func (p PyObj) GetChangesByte() ([]byte, error) {
	if p.Changes == nil {
		return []byte("{}"), nil
	}

	var buf bytes.Buffer
	buf.WriteString("{\n")

	// Create a custom JSON encoder for values
	valueEncoder := json.NewEncoder(&buf)
	valueEncoder.SetEscapeHTML(false) // Prevent escaping of >, <, &

	first := true
	for pair := p.Changes.Oldest(); pair != nil; pair = pair.Next() {
		if !first {
			buf.WriteString(",\n")
		}

		// Write key
		buf.WriteString(`    "`)
		buf.WriteString(pair.Key)
		buf.WriteString(`": `)

		// Marshal value with custom settings
		switch v := pair.Value.(type) {
		case json.RawMessage:
			// Write raw JSON directly
			buf.Write(v)
		case *orderedmap.OrderedMap[string, any]:
			// Recursively handle nested ordered maps
			nested, err := marshalOrderedMap(v)
			if err != nil {
				return nil, err
			}
			buf.Write(nested)
		default:
			// Use encoder for other types
			if err := valueEncoder.Encode(pair.Value); err != nil {
				return nil, err
			}
			// Remove newline added by encoder
			buf.Truncate(buf.Len() - 1)
		}

		first = false
	}

	buf.WriteString("\n}")
	return buf.Bytes(), nil
}

// Helper function to marshal nested ordered maps
func marshalOrderedMap(om *orderedmap.OrderedMap[string, any]) ([]byte, error) {
	var buf bytes.Buffer
	buf.WriteString("{")

	first := true
	for pair := om.Oldest(); pair != nil; pair = pair.Next() {
		if !first {
			buf.WriteString(", ")
		}

		// Write key
		buf.WriteString(`"`)
		buf.WriteString(pair.Key)
		buf.WriteString(`": `)

		// Marshal value
		switch v := pair.Value.(type) {
		case json.RawMessage:
			buf.Write(v)
		case *orderedmap.OrderedMap[string, any]:
			nested, err := marshalOrderedMap(v)
			if err != nil {
				return nil, err
			}
			buf.Write(nested)
		default:
			valBytes, err := json.Marshal(v)
			if err != nil {
				return nil, err
			}
			buf.Write(valBytes)
		}

		first = false
	}

	buf.WriteString("}")
	return buf.Bytes(), nil
}

func (p PyObj) HasChanges() bool {
	return p.Changes != nil && p.Changes.Len() > 0
}

func (p PyObj) HasItem() bool {
	return p.Item != nil
}

// Implement UnmarshalJSON for PyObj to handle AnyItem
func (p *PyObj) UnmarshalJSON(data []byte) error {
	// cast the original PyObj to an alias that replaces Item for raw Json
	type Alias PyObj
	temp := struct {
		*Alias
		Item json.RawMessage `json:"item"`
	}{
		Alias: (*Alias)(p),
	}

	// unmarshaling to the alias means the item is stored as raw json (untyped)
	if err := json.Unmarshal(data, &temp); err != nil {
		return err
	}

	// Now determine what type item should be
	if len(temp.Item) == 0 {
		return nil // No item to unmarshal
	}

	// Try unmarshaling as Character
	var char CharacterObj
	// check for the presence of a field unique to character
	if err := json.Unmarshal(temp.Item, &char); err == nil && char.Kit != nil {
		// if "kit" exists, save item as a character to the original pyObj and end the function
		p.Item = char
		return nil
	}

	// Try unmarshaling as Lightcone
	var lc LightconeObj
	// check for the presence of a field unique to lightcone
	if err := json.Unmarshal(temp.Item, &lc); err == nil && lc.Path != "" {
		// if "path" exists, save item as a character to the original pyObj and end the function
		p.Item = lc
		return nil
	}

	// Try unmarshaling as Relicset
	var rs RelicsetObj
	// check for the presence of a field unique to relicset
	if err := json.Unmarshal(temp.Item, &rs); err == nil && rs.Effect != nil {
		// if "effect" exists, save item as a character to the original pyObj and end the function
		p.Item = rs
		return nil
	}

	return fmt.Errorf("could not determine item type")
}

type CharacterObj struct {
	Name       string
	Stats      *orderedmap.OrderedMap[string, any]
	Enhanced   []string                            `json:"Enhanced,omitempty,omitzero"`
	Kit        json.RawMessage                     //todo
	Memosprite json.RawMessage                     `json:"Memosprite,omitempty"` //todo
	Minor      *orderedmap.OrderedMap[string, any] `json:"Minor Traces"`
	Tree       json.RawMessage                     `json:"Trace Tree"` //todo
	Materials  []string
	Eidolons   *orderedmap.OrderedMap[string, any]
	Terms      json.RawMessage
	Relics     *orderedmap.OrderedMap[string, []string]
	Skin       *orderedmap.OrderedMap[string, string] `json:"Skin,omitempty,omitzero"`
}

type LightconeObj struct {
	Name      string
	Rarity    int
	Path      string
	Desc      string
	Stats     *orderedmap.OrderedMap[string, any]
	Materials []string
}

type RelicsetObj struct {
	Name   string
	Effect *orderedmap.OrderedMap[string, string] `json:"Relic Effect/s"`
}

type Changes struct {
	Values_changed          *orderedmap.OrderedMap[string, any] `json:"values_changed,omitempty"`
	Type_changes            []any                               `json:"type_changes,omitempty"`
	Dictionary_item_added   []any                               `json:"dictionary_item_added,omitempty"`
	Dictionary_item_removed []any                               `json:"dictionary_item_removed,omitempty"`
}

type AnyItem interface {
	GetMyName() string
}

func (o CharacterObj) GetMyName() string {
	return o.Name
}

func (o LightconeObj) GetMyName() string {
	return o.Name
}

func (o RelicsetObj) GetMyName() string {
	return o.Name
}
