package handlers

import (
	"fmt"

	"github.com/Asnxthaony/NTE-Network-Analysis/pkg/types/game"
	"github.com/Asnxthaony/NTE-Network-Analysis/util"
)

func init() {
	Register(1649, handleGameDataFirstSync)
	Register(1650, handleSingleRecordSync)
}

// [1649] GameDataFirstSync

type GameDataFirstSync struct {
	RoleID uint64
	Data   []byte
}

func handleGameDataFirstSync(payload []byte) (*GameDataFirstSync, error) {
	data, err := util.UncompressLz4(payload)
	if err != nil {
		return nil, fmt.Errorf("failed to uncompress game data: %w", err)
	}

	cmd := game.GetRootAsGameDataFirstSync(data, 0)

	return &GameDataFirstSync{
		RoleID: cmd.RoleId(),
		Data:   cmd.DataBytes(),
	}, nil
}

// [1650] SingleRecordSync

type SingleRecordSync struct {
	RoleID uint64
	Name   string
	Data   []byte
}

func handleSingleRecordSync(payload []byte) (*SingleRecordSync, error) {
	cmd := game.GetRootAsSingleRecordSync(payload, 0)

	return &SingleRecordSync{
		RoleID: cmd.RoleId(),
		Name:   string(cmd.Name()),
		Data:   cmd.DataBytes(),
	}, nil
}
