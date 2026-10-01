import json

result = []

UNUSED_TREASURE_BOX = [
    "ChameleonBox_A_Area01_007",
    "ChameleonBox_A_Area01_008",
    "ChameleonBox_A_Area01_009",
    "ChameleonBox_A_Area01_010",
    "ChameleonBox_A_Area01_011",
    "ChameleonBox_A_Area01_012",
    "ChameleonBox_A_Area01_013",
    "ChameleonBox_A_Area01_014",
    "ChameleonBox_A_Area01_015",
    "ChameleonBox_A_Area03_006",
    "ChameleonBox_A_Area03_007",
    "ChameleonBox_A_Area03_008",
    "ChameleonBox_A_Area03_009",
    "ChameleonBox_A_Area03_010",
    "ChameleonBox_A_Area03_011",
    "ChameleonBox_A_Area03_012",
    "ChameleonBox_A_Area03_013",
    "ChameleonBox_A_Area03_014",
    "ChameleonBox_A_Area03_015",
    "PropBox_Geft_A_Area01_010",
]

# StaticTreasureBoxDataRec_Envir_{AreaId}
DataRec = {
    "001": {
        0: 285974182586482687,
        2: 32736,
        3: 1040187392,
    },
    "002": {
        0: 18158513701852807168,
        1: 2047,
        3: 3221225472,
    },
    "003": {
        1: 9232379236109514752,
        2: 31,
        3: 133143986176,
    },
    "004": {
        2: 4503599627337728,
        3: 140600049401856
    },
    "005": {
        2: 18442240474082181120,
        3: 1296895955227901951,
    },
    "006": {
        3: 17149707381026848768,
        4: 134217727
    },
}


def getbit(t, nBitIndex):
    assert nBitIndex >= 0
    idx = nBitIndex // 64
    offset = nBitIndex % 64
    qwData = t.get(idx, 0)
    return ((qwData >> offset) & 1) == 1


with open("data/DT_EnvirTreasureBoxConfig.json", "r") as f:
    EnvirTreasureBoxConfig = json.load(f)[0]["Rows"]


for key, value in EnvirTreasureBoxConfig.items():
    if key in UNUSED_TREASURE_BOX:
        continue

    index = value["Index"]
    areaId = value["AreaId"]

    rec = DataRec.get(areaId, {})
    isObtained = getbit(rec, index)

    if not isObtained:
        loc = value["Location"]
        result.append(
            {
                "id": key,
                "name": key,
                "types": ["env-treasure"],
                "district": "未获取",
                "tags": [],
                "images": [],
                "x": loc["X"],
                "y": loc["Y"],
            }
        )

    print(f"{key}: {'✔️' if isObtained else '❌'}")


print(json.dumps(result, ensure_ascii=False, indent=4))
