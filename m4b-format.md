Endian order: little endian

**FILE HEADER**

|  Type  | Count | Description |
| :----- | ----: | :---------- |
| uint32 |  0x01 | Signature string length = 0x0b |
| char   |  0x0b | Signature string = "UBI_BF_SIG" + 0x0 |
| uint32 |  0x01 | file format version? = 0x1 |
| uint32 |  0x01 | unknown = 0x0|
| DIR    |  0x01 | Root directory entry |
| DATA   |  ??   | Determined by file entries. can actually contain "slack space" |

**DIR structure**

|  TYPE    | Count | Description |
| :-----   | ----: | :---------- |
| uint8    | 0x01  | Number of subdirectories (call this "sd") |
| DIRINFO  | sd    | Directory information structures for all subdirectories |
| uint32   | 0x01  | Number of files in this directory (call this "fc") |
| FILEINFO | fc    | File information structures |

**DIRINFO structure**

|  Type  | Count | Description |
| :----- | ----: | :---------- |
| uint32 | 0x01  | Directory name length (dnl) |
| char   | dnl   | Directory name (null terminated, counted in dnl) |
| DIR    | 0x01  | Directory contents struct |

**FILEINFO structure**

|  Type  | Count | Description |
| :----- | ----: | :---------- |
| uint32 | 0x01  | File name length (fnl) |
| char   | fnl   | File name (null terminated, counted in fnl) |
| uint32 | 0x01  | file length |
| uint32 | 0x01  | file offset (from start of m4b file) |
