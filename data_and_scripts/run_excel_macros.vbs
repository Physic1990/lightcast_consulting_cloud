Option Explicit

' Variables
Dim ExcelApp
Dim ExcelWorkbook
Dim MacroToRun
Dim ExcelFile
'Dim objShell, scriptPath 

' Set relative file path - does not work
'Set objShell = CreateObject("WScript.Shell")
'scriptPath = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\") - 1)  ' Get directory of VBScript
'objShell.CurrentDirectory = scriptPath  ' Set the working directory

' Adjust variables
ExcelFile = "C:\Users\plumz\OneDrive\Documents\GitHub\lightcast_consulting_cloud\data_and_scripts\US_EIS_sharable_INIT.xlsm"  
MacroToRun = "MainProcess"        

' Create the Excel application object
Set ExcelApp = CreateObject("Excel.Application")

' Make Excel visible (optional)
ExcelApp.Visible = True  ' Set to False to run in the background

' Open the Excel workbook
Set ExcelWorkbook = ExcelApp.Workbooks.Open(ExcelFile)

' Run the macro
ExcelApp.Run MacroToRun

' Save the workbook (optional)
'ExcelWorkbook.Save

' Close the workbook
'ExcelWorkbook.Close False ' False = don't save changes if prompted

' Quit Excel
'ExcelApp.Quit

' Clean up objects
Set ExcelWorkbook = Nothing
Set ExcelApp = Nothing

WScript.Echo "Macro '" & MacroToRun & "' executed in '" & ExcelFile & "'"
WScript.Quit
