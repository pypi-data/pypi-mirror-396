* Top:     `None`
* Defines: `None`
* Size:    `16.25 KB`

| Addrspace | Type | Base     | Size                | Infos | Attributes |
| --------- | ---- | -------- | ------------------- | ----- | ---------- |
| one       | -    | `0x0`    | `64x32 (256 bytes)` |       |            |
| other     | -    | `0x1000` | `64x32 (256 bytes)` |       |            |
| one       | -    | `0x2800` | `64x32 (256 bytes)` |       |            |
| other     | -    | `0x4000` | `64x32 (256 bytes)` |       |            |


| Addrspace | Word | Field | Offset   | Access | Reset | Infos | Attributes |
| --------- | ---- | ----- | -------- | ------ | ----- | ----- | ---------- |
| one       |      |       | `0x0`    |        |       |       |            |
| one       | one  |       | `  +0`   |        |       |       |            |
| one       | two  |       | `  +7`   |        |       |       |            |
| other     |      |       | `0x1000` |        |       |       |            |
| other     | one  |       | `  +0`   |        |       |       |            |
| other     | two  |       | `  +7`   |        |       |       |            |
| one       |      |       | `0x2800` |        |       |       |            |
| one       | one  |       | `  +0`   |        |       |       |            |
| one       | two  |       | `  +7`   |        |       |       |            |
| other     |      |       | `0x4000` |        |       |       |            |
| other     | one  |       | `  +0`   |        |       |       |            |
| other     | two  |       | `  +7`   |        |       |       |            |
