package codec

import "errors"

var (
	ErrPacketTooShort    = errors.New("codec: packet too short")
	ErrPacketLenMismatch = errors.New("codec: packet length mismatch")
)
