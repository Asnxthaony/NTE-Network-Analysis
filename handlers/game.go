package handlers

import (
	"fmt"

	"github.com/Asnxthaony/NTE-Network-Analysis/pkg/types/game"
	"github.com/Asnxthaony/NTE-Network-Analysis/util"
)

func init() {
	Register(1649, handleGameDataFirstSync)
}

// [1649] GameDataFirstSync

type GameDataFirstSync struct {
	RoleId   uint64
	GameData []byte
}

func handleGameDataFirstSync(payload []byte) (*GameDataFirstSync, error) {
	data, err := util.UncompressLz4(payload)
	if err != nil {
		return nil, fmt.Errorf("failed to uncompress game data: %w", err)
	}

	cmd := game.GetRootAsGameDataFirstSync(data, 0)

	return &GameDataFirstSync{
		RoleId:   cmd.RoleId(),
		GameData: cmd.Unk1Bytes(),
	}, nil
}
