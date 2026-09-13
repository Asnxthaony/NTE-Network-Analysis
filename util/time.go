package util

import "time"

const epochTicks = int64(621355968000000000)

func TicksToUnixTime(ticks int64) time.Time {
	millisFromTicks := (ticks - epochTicks) / 10000

	return time.UnixMilli(millisFromTicks).UTC()
}
