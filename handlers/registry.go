package handlers

import "errors"

type Entry struct {
	Parse func(payload []byte) (any, error)
}

var registry = map[int32]Entry{}

func Register[T any](id int32, fn func([]byte) (*T, error)) {
	registry[id] = Entry{Parse: func(payload []byte) (any, error) {
		return fn(payload)
	}}
}

func Get(id int32) (Entry, bool) {
	e, ok := registry[id]
	return e, ok
}

var ErrUnknownMessage = errors.New("unknown message")
