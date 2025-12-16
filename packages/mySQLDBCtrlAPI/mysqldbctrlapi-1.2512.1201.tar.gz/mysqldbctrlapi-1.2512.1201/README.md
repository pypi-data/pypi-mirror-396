#mySQLDBCtrlAPI

## History of version
Version 1.2512.1201: 2025/12/12<BR>
Fixed encode 2 problem (UTF-8) CLASS_mySQLxJson.CUF_jsonContent_to_mysql()<BR>

Version 1.2512.1103: 2025/12/11<BR>
Fixed encode problem (UTF-8) CLASS_mySQLxJson.CUF_jsonContent_to_mysql()<BR>

Version 1.2512.1102: 2025/12/11<BR>
Improve CLASS_mySQLxJson function:CUF_jsonContent_to_mysql(...)<BR>

Version 1.2512.1101: 2025/12/11<BR>
1) Add enumerate property in CLASS_mySQLDBCtrl<BR>
2) Add Table tools for create / drop / find / list.<BR>
3) Add Index tools for create / drop.<BR>
4) Fixed bugs in ssh algorithm.<BR>
5) Tunning performance for query procedure.<BR>

Version 1.2512.0403: 2025/12/04<BR>
Fixed ssh tunnel service thread fault.

Version 1.2512.0401: 2025/12/04<BR>
Add Advance ssh tunnel service (ver2.0) package.

Version 1.2512.0302: 2025/12/03<BR>
Add ssh tunnel service package.

Version 1.2512.0301: 2025/12/03<BR>
Add CLASS_mySQLxJson Library for convert json data into mysql each other.

Version 1.2512.0101: 2025/12/01<BR>
Fixed error CUF_GetServerDateTime(...) when error on fetch data from dataset

Version 1.2511.28: 2025/11/28<BR>
Fixed error CUF_GET_Blob(...) will disturbe cursor position.

Version 1.2511.27: 2025/11/27<BR>
Fixed error CUF_DB_Eof(...) and CUF_Eof(...) --> When DataSet was empty.

Version 1.2511.26: 2025/11/26<BR>
Fixed CUF_DB_OpenSQL(...) return failure when Null data.

Version 1.2511.06: 2025/11/25<BR>
Fixed Eof() bugs.


Version 1.2511.06: 2025/11/06<BR>
Fixed utf8 and big5(latin) encode bugs.

Version 1.2510.23: 2025/10/22<BR>
Fixed version bugs.

Version 1.2510.22: 2025/10/22<BR>
1.Add string decode method (translage utf8 charset -> utf-8)
2.Add Eof() procedure 
3.Fixed CUF_DB_ExecSQL() and CUF_DB_OpenSQL() bugs.


Version 0.1.2: 2025/10/09<BR>
Add string decode method (translage big5 charset -> utf-8)

Version 0.1.1: 2025/09/19<BR>
Fixed some bugs.
