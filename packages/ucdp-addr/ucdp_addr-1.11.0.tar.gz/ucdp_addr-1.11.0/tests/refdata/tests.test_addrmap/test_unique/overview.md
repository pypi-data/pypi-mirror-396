* Top:     `None`
* Defines: `None`
* Size:    `2080772 KB`

| Addrspace | Type | Base         | Size             | Infos        | Attributes |
| --------- | ---- | ------------ | ---------------- | ------------ | ---------- |
| one       | -    | `+0x1000`    | `1024x32 (4 KB)` | Sub,Volatile | a=1; b     |
| two       | -    | `+0x3000`    | `1024x32 (4 KB)` | Sub          |            |
| three     | -    | `0x7F000000` | `1024x32 (4 KB)` |              |            |


| Addrspace | Word  | Field | Offset       | Access | Reset | Infos    | Attributes |
| --------- | ----- | ----- | ------------ | ------ | ----- | -------- | ---------- |
| one       |       |       | `+0x1000`    |        |       | Volatile | a=1; b     |
| one       | word0 |       | `  +0`       |        |       | Volatile |            |
| one       | word0 | field | `    [2:0]`  | RW/-   | `0x0` | Volatile | foo        |
| one       | word1 |       | `  +4:1`     |        |       | Volatile | bar=4      |
| one       | word1 | field | `    [2:0]`  | RW/-   | `0x0` | Volatile |            |
| two       |       |       | `+0x3000`    |        |       |          |            |
| two       | word  |       | `  +8`       |        |       |          |            |
| two       | word  | field | `    [8:6]`  | RW/-   | `0x0` |          |            |
| three     |       |       | `0x7F000000` |        |       |          |            |
