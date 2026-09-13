package main

import (
	"fmt"
	"os"

	"encoding/json"

	"github.com/Asnxthaony/NTE-Network-Analysis/codec"
)

func main() {
	files := []string{
		"data/01_1120_ServerVersionCmd.bin",
		"data/02_1106_ClientLoginReq.bin",
		"data/03_2010_UpdateReconnectToken.bin",
		"data/04_1117_ClientTravelCmd.bin",
		"data/05_1122_ServerKeepAliveCmd.bin",
		"data/06_1649_GameDataFirstSync.bin",
		"data/07_1649_GameDataFirstSync.bin",
	}

	for _, f := range files {
		fmt.Printf("=== %s ===\n", f)
		res, err := codec.Decode(f)
		if err != nil {
			fmt.Fprintf(os.Stderr, "decode %q: %v\n", f, err)
			continue
		}
		jsonData, err := json.MarshalIndent(res.Body, "", "  ")
		fmt.Println(string(jsonData))
	}

}
