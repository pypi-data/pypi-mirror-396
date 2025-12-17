* Top:     `None`
* Defines: `None`
* Size:    `268 KB`

| Addrspace | Type | Base      | Size             | Infos | Attributes |
| --------- | ---- | --------- | ---------------- | ----- | ---------- |
| one       | -    | `0x11000` | `512x32 (2 KB)`  |       |            |
| two       | -    | `0x12000` | `1024x32 (4 KB)` |       |            |
| one       | -    | `0x41000` | `512x32 (2 KB)`  |       |            |
| two       | -    | `0x42000` | `1024x32 (4 KB)` |       |            |


| Addrspace | Word  | Field  | Offset       | Access | Reset | Infos | Attributes |
| --------- | ----- | ------ | ------------ | ------ | ----- | ----- | ---------- |
| one       |       |        | `0x11000`    |        |       |       |            |
| one       | word0 |        | `  +4`       |        |       |       |            |
| one       | word0 | field0 | `    [3:0]`  | RW/-   | `0x0` |       |            |
| two       |       |        | `0x12000`    |        |       |       |            |
| two       | word1 |        | `  +1008`    |        |       |       |            |
| two       | word1 | field1 | `    [31:0]` | RO/-   | `0x0` | CONST |            |
| one       |       |        | `0x41000`    |        |       |       |            |
| one       | word0 |        | `  +4`       |        |       |       |            |
| one       | word0 | field0 | `    [3:0]`  | RW/-   | `0x0` |       |            |
| two       |       |        | `0x42000`    |        |       |       |            |
| two       | word1 |        | `  +1008`    |        |       |       |            |
| two       | word1 | field1 | `    [31:0]` | RO/-   | `0x0` | CONST |            |
