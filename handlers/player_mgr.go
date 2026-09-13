package handlers

import (
	"github.com/Asnxthaony/NTE-Network-Analysis/pkg/types/player_mgr"
)

func init() {
	Register(2010, handleUpdateReconnectToken)
}

// [2010] UpdateReconnectToken

type UpdateReconnectToken struct {
	ReconnectToken string
}

func handleUpdateReconnectToken(payload []byte) (*UpdateReconnectToken, error) {
	req := player_mgr.GetRootAsUpdateReconnectToken(payload, 0)

	return &UpdateReconnectToken{
		ReconnectToken: string(req.ReconnectToken()),
	}, nil
}
