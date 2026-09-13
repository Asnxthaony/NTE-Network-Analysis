package handlers

import (
	"time"

	"github.com/Asnxthaony/NTE-Network-Analysis/pkg/types/gateway"
	"github.com/Asnxthaony/NTE-Network-Analysis/util"
)

func init() {
	Register(1106, handleClientLoginReq)
	Register(1117, handleClientTravelCmd)
	Register(1120, handleServerVersionCmd)
	Register(1122, handleServerKeepAliveCmd)
}

// [1106] ClientLoginReq

type ClientLoginReq struct {
	ClientVersion string
	Username      string
	Password      string
	AuthType      int32
	Unk1          string
	GameId        string
	ChannelId     string
	NoticeChannel string
	Unk2          string
	ClientWanIp   string
	DeviceId1     string
	DeviceId2     string
	OsBrand       string
	OsVersion     string
}

func handleClientLoginReq(payload []byte) (*ClientLoginReq, error) {
	req := gateway.GetRootAsClientLoginReq(payload, 0)

	return &ClientLoginReq{
		ClientVersion: string(req.ClientVersion()),
		Username:      string(req.Username()),
		Password:      string(req.Password()),
		AuthType:      req.AuthType(),
		Unk1:          string(req.Unk1()),
		GameId:        string(req.GameId()),
		ChannelId:     string(req.ChannelId()),
		NoticeChannel: string(req.NoticeChannel()),
		Unk2:          string(req.Unk2()),
		ClientWanIp:   string(req.ClientWanIp()),
		DeviceId1:     string(req.DeviceId1()),
		DeviceId2:     string(req.DeviceId2()),
		OsBrand:       string(req.OsBrand()),
		OsVersion:     string(req.OsVersion()),
	}, nil
}

// [1117] ClientTravelCmd

type ClientTravelCmd struct {
	Unk1        int32
	Uid         string
	Unk2        int32
	ActorTag    string
	ServerAddr  string
	Location    string
	Unk3        int32
	RoleId      uint64
	CharacterBp string
	Unk4        int32
	Unk5        int32
	Unk6        int32
	Unk7        int32
}

func handleClientTravelCmd(payload []byte) (*ClientTravelCmd, error) {
	cmd := gateway.GetRootAsClientTravelCmd(payload, 0)

	return &ClientTravelCmd{
		Unk1:        cmd.Unk1(),
		Uid:         string(cmd.Uid()),
		Unk2:        cmd.Unk2(),
		ActorTag:    string(cmd.ActorTag()),
		ServerAddr:  string(cmd.ServerAddr()),
		Location:    string(cmd.Location()),
		Unk3:        cmd.Unk3(),
		RoleId:      cmd.RoleId(),
		CharacterBp: string(cmd.CharacterBp()),
		Unk4:        cmd.Unk4(),
		Unk5:        cmd.Unk5(),
		Unk6:        cmd.Unk6(),
		Unk7:        cmd.Unk7(),
	}, nil
}

// [1120] ServerVersionCmd

type ServerVersionCmd struct {
	ServerVersion       string
	ClientWanIp         string
	ClientWanPort       int32
	HeartType           uint8
	HeartClientInterval int32
	CheckServerInterval int32
	ServerId            int32
	ServerTimeUtc       time.Time
	ServerTime          time.Time
	Unk1                []byte
	Unk2                []byte
}

func handleServerVersionCmd(payload []byte) (*ServerVersionCmd, error) {
	cmd := gateway.GetRootAsServerVersionCmd(payload, 0)

	return &ServerVersionCmd{
		ServerVersion:       string(cmd.ServerVersion()),
		ClientWanIp:         string(cmd.ClientWanIp()),
		ClientWanPort:       cmd.ClientWanPort(),
		HeartType:           cmd.HeartType(),
		HeartClientInterval: cmd.HeartClientInterval(),
		CheckServerInterval: cmd.CheckServerInterval(),
		ServerId:            cmd.ServerId(),
		ServerTimeUtc:       util.TicksToUnixTime(cmd.ServerTimeUtc()),
		ServerTime:          util.TicksToUnixTime(cmd.ServerTime()),
		Unk1:                cmd.Unk1Bytes(),
		Unk2:                cmd.Unk2Bytes(),
	}, nil
}

// [1122] ServerKeepAliveCmd

type ServerKeepAliveCmd struct {
	Unk1          uint32
	ServerTimeUtc time.Time
	ServerTime    time.Time
}

func handleServerKeepAliveCmd(payload []byte) (*ServerKeepAliveCmd, error) {
	cmd := gateway.GetRootAsServerKeepAliveCmd(payload, 0)

	return &ServerKeepAliveCmd{
		Unk1:          cmd.Unk1(),
		ServerTimeUtc: util.TicksToUnixTime(cmd.ServerTimeUtc()),
		ServerTime:    util.TicksToUnixTime(cmd.ServerTime()),
	}, nil
}
