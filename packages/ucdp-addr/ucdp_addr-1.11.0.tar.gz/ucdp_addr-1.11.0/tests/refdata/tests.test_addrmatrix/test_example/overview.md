| Master > Slave | ram | periph | misc |
| -------------- | --- | ------ | ---- |
| ext            | X   |        | X    |
| dsp            | X   | X      |      |



* Top:     `None`
* Defines: `None`
* Size:    `3932352 KB`

| Addrspace | Type     | Base         | Size                      | Infos | Attributes |
| --------- | -------- | ------------ | ------------------------- | ----- | ---------- |
| reserved0 | Reserved | `0x0`        | `1006632960x32 (3.75 GB)` |       |            |
| ram       | Slave    | `0xF0000000` | `16384x32 (64 KB)`        |       |            |
| periph    | Slave    | `0xF0010000` | `8192x32 (32 KB)`         |       |            |
| reserved1 | Reserved | `0xF0018000` | `8192x32 (32 KB)`         |       |            |
| misc      | Slave    | `0xF0020000` | `16384x32 (64 KB)`        |       |            |
| reserved2 | Reserved | `0xF0030000` | `67059712x32 (261952 KB)` |       |            |
