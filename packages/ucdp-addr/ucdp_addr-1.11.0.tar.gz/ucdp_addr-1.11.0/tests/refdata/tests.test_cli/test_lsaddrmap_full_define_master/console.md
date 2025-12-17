* Top:     `top_lib.top`
* Defines: `master='apps'`
* Size:    `262 KB`

| Addrspace | Type | Base      | Size            | Infos | Attributes |
| --------- | ---- | --------- | --------------- | ----- | ---------- |
| one       | -    | `0x11000` | `512x32 (2 KB)` |       |            |
| one       | -    | `0x41000` | `512x32 (2 KB)` |       |            |


| Addrspace | Word  | Field  | Offset      | Access | Reset | Infos | Attributes |
| --------- | ----- | ------ | ----------- | ------ | ----- | ----- | ---------- |
| one       |       |        | `0x11000`   |        |       |       |            |
| one       | word0 |        | `  +4`      |        |       |       |            |
| one       | word0 | field0 | `    [3:0]` | RW/-   | `0x0` |       |            |
| one       |       |        | `0x41000`   |        |       |       |            |
| one       | word0 |        | `  +4`      |        |       |       |            |
| one       | word0 | field0 | `    [3:0]` | RW/-   | `0x0` |       |            |
