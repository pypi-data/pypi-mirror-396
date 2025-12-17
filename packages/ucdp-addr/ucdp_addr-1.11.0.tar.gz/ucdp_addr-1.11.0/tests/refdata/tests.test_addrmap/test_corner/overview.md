* Top:     `None`
* Defines: `None`
* Size:    `8 KB`

| Addrspace | Type | Base      | Size             | Infos        | Attributes |
| --------- | ---- | --------- | ---------------- | ------------ | ---------- |
| zero      | -    | `+0x0`    | `1024x32 (4 KB)` | Sub          |            |
| one       | -    | `+0x1000` | `1024x32 (4 KB)` | Sub,Volatile | a=1; b     |


| Addrspace | Word  | Field | Offset      | Access | Reset | Infos    | Attributes |
| --------- | ----- | ----- | ----------- | ------ | ----- | -------- | ---------- |
| zero      |       |       | `+0x0`      |        |       |          |            |
| one       |       |       | `+0x1000`   |        |       | Volatile | a=1; b     |
| one       | word0 |       | `  +0`      |        |       | Volatile |            |
| one       | word0 | field | `    [2:0]` | RW/-   | `0x0` | Volatile | foo        |
| one       | word1 |       | `  +4:1`    |        |       | Volatile | bar=4      |
| one       | word1 | field | `    [2:0]` | RW/-   | `0x0` | Volatile |            |
