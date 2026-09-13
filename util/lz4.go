package util

import (
	"encoding/binary"
	"errors"
	"fmt"

	"github.com/pierrec/lz4/v4"
)

func UncompressLz4(data []byte) ([]byte, error) {
	dataLen := len(data)
	uncompressedLength := binary.LittleEndian.Uint32(data[dataLen-4:])
	compressed := data[:dataLen-4]
	dst := make([]byte, uncompressedLength)

	n, err := lz4.UncompressBlock(compressed, dst)
	if err != nil {
		return nil, fmt.Errorf("lz4 decompress: %w", err)
	}
	if n != int(uncompressedLength) {
		return nil, errors.New("lz4: uncompressed size mismatch")
	}

	return dst, nil
}
