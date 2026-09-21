package codec

import (
	"encoding/binary"
	"fmt"
	"os"

	"github.com/Asnxthaony/NTE-Network-Analysis/handlers"
	"github.com/Asnxthaony/NTE-Network-Analysis/pkg/types/packet"
)

type Result struct {
	MsgCode   int32 `json:"msg_code"`
	ErrorCode int32 `json:"error_code,omitempty"`
	Body      any   `json:"body"`
}

func Decode(filename string) (*Result, error) {
	buf, err := os.ReadFile(filename)
	if err != nil {
		return nil, fmt.Errorf("read file %q: %w", filename, err)
	}
	return DecodeBytes(buf)
}

func DecodeBytes(buf []byte) (*Result, error) {
	if len(buf) < 4 {
		return nil, ErrPacketTooShort
	}

	packetLen := int32(binary.LittleEndian.Uint32(buf[:4]))
	packetBuf := buf[4:]
	if int(packetLen) > len(packetBuf) {
		return nil, ErrPacketLenMismatch
	}
	packetBuf = packetBuf[:packetLen]

	head := packet.GetRootAsPacketHead(packetBuf, 0)
	msgCode := head.MsgCode()
	errorCode := head.ErrorCode()
	msgSize := head.MsgSize()

	offset := packetLen - msgSize
	payload := packetBuf[offset:]

	h, ok := handlers.Get(msgCode)
	if !ok {
		return nil, fmt.Errorf("%w: %d", handlers.ErrUnknownMessage, msgCode)
	}

	msg, err := h.Parse(payload)
	if err != nil {
		return nil, err
	}

	return &Result{
		MsgCode:   msgCode,
		ErrorCode: errorCode,
		Body:      msg,
	}, nil
}
