' RUN SCRIPT IN TERMINAL BY: "cscript RunExcelMacro.vbs"
' SHOULD OUTPUT: "Hello! This macro is working correctly."

Set objExcel = CreateObject("Excel.Application")
objExcel.Visible = False

' Get the script's directory
strPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Construct the full path to the Excel file
strExcelFile = strPath & "\US_EIS_sharable.xlsm"

Set objWorkbook = objExcel.Workbooks.Open(strExcelFile)

objExcel.Run "TestMacro"

objWorkbook.Save
objWorkbook.Close

objExcel.Quit

Set objWorkbook = Nothing
Set objExcel = Nothing
