Option Explicit

'These objects are the worksheets touched by the macros. They are declared here, and because they are
'public, they do not need to be declared anywhere else. See the note below for more information.
Public objBook, objUI, objIns, objContinuingFeed, objCreditEngine, objRawData, objShort

Sub MainProcess()
                                        
    Application.Calculation = xlCalculationManual
    Application.ScreenUpdating = False
    
    '* * * * * * * * * * * * * * * I M P O R T A N T * * * * * * * * * * * * * * *
    '* * * All of the sheet names for the entire process are set right here. * * *
    '* * * This assures that all sheet names are consistent and avoids error * * *
    '* * * in the future. If you would like to add another sheet, add it to  * * *
    '* * * the ñPublic ...î list and define it in DefineSheetNames below.    * * *
    '* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
    DefineSheetNames
    Application.ScreenUpdating = True
    objIns.Range("M10:M28").Value = ""
    
    'Check to see if the correct data is in the 'Research Spending' tab
    If Sheets("Ins").Range("f28").Value = 1 And Sheets("Ins").Range("f29").Value = 0 Then
        MsgBox ("Enter the R&D production functions in the 'Research Spending' tab.")
    End If
    If Sheets("Ins").Range("f28").Value = 1 And Sheets("Ins").Range("f30").Value <> Sheets("Ins").Range("f10") Then
        MsgBox ("The R&D production functions in the 'Research Spending' tab do not reflect the correct state.")
    End If

    'Set the datarun
    DBAccess.SetDataRun
    
    Application.Calculate
               
    'Run new CHE data
    
    objIns.Range("M8").Value = "Starting Credit Engine"
    
    'Get the datarun
    Dim dataRunRow
    Dim datarun
    dataRunRow = 18 + Sheets("Ins").Range("g3").Value
    datarun = Sheets("Ins").Range("F" & dataRunRow).Value
    
    datarun = Replace(datarun, ".", "")
    datarun = CLng(datarun)
    
    objIns.Range("M8").Value = "Beginning Raw Data Import Stream"

    'Get the raw data
    'DBAccess.ImportRawData 'takes 11 seconds to run
    Application.ScreenUpdating = True
    EIS_Python_Automation.Run_EIS
    
    objIns.Range("M8").Value = "Cleaning Data"
    
    'clear all the queries (for some reason the queries pile up each time we run the model, especially in the raw data sheet. And if left unchecked they can slow down Excel tremendously. Therefore, clear them each time we're done with them.)
    Dim iX As Integer
    Dim iY As Integer
    For iY = 1 To Worksheets.Count
        Worksheets(iY).Activate
        For iX = ActiveSheet.QueryTables.Count To 1 Step -1
            ActiveSheet.QueryTables(iX).Delete
        Next
    Next
  
  
    objIns.Activate
    Application.Calculation = xlCalculationAutomatic
    Application.ScreenUpdating = True
    
    objIns.Range("M8").Value = "Writing Short Sheet"
    
    EIS_Python_Automation.Write_Short_Results
    
    objIns.Range("M8").Value = "Done!"
                                                
End Sub

Sub DefineSheetNames()
    
    'Get the necessary worksheet objects
    Set objBook = Application.ActiveWorkbook
    Set objIns = objBook.Sheets("Ins")
    Set objContinuingFeed = objBook.Sheets("Continuing Feed")
    Set objCreditEngine = objBook.Sheets("Credit Engine")
    Set objUI = objBook.Sheets("UI")
    Set objRawData = objBook.Sheets("Raw Data")
    Set objShort = objBook.Sheets("Short")

End Sub

Sub Run_Several()

    'Calculate
    Counties.CountyData
    
    Application.ScreenUpdating = False
    
    Application.Calculate

End Sub

Sub Export()
    
'this macro is called by the VBScript to export data that InDesign can parse and use
'the reason I'm putting the code here instead of in the VBScript itself is because it's faster here
'in internal VBA it takes less than a second, whereas in external VBScript it takes over 9 minutes!
'also, internal VBA allows the CSV export to be customized to suit each unique model (worksheets, etc.)

'****PRELIMINARIES****
Dim ultimateFolder As String
ultimateFolder = "C:\Scripts" 'this is the folder where everything will be exported
If Len(Dir(ultimateFolder, vbDirectory)) = 0 Then 'if the destination folder doesn't exist yet...
   MkDir ultimateFolder '...then make it
End If

'prepare for the CSV file
Dim OutputSheet As String
OutputSheet = "Text" 'this is the name of the worksheet containing the data and variables

Dim fs, a As Object
Dim i, j, x, y, RowCount As Integer

Dim TheArray() As String
RowCount = Worksheets(OutputSheet).Cells(Rows.Count, 3).End(xlUp).Row 'determine how long Column C is, and go with that
ReDim TheArray(1 To RowCount, 1 To 2) 'define the dimensions of the array, making it just big enough for the desired data

Set fs = CreateObject("Scripting.FileSystemObject")
Set a = fs.CreateTextFile(ultimateFolder & "\ExcelData.csv", True) 'this file name must agree with the name assumed in the ExtendScript code

'make a two-dimensional array including all the desired CSV data
For i = 1 To RowCount
    TheArray(i, 1) = Worksheets(OutputSheet).Cells(i, 2).Text 'grabs displayed text in cell, not values
    TheArray(i, 2) = LCase(Worksheets(OutputSheet).Cells(i, 3).Text) 'grabs displayed text and makes it lowercase, effectively making this operation case insensitive (because ExtendScript assumes lowercase, too)
Next i

'loop through array and export it to the CSV file
For j = 1 To RowCount
    a.WriteLine TheArray(j, 1) & "~" & TheArray(j, 2) & "~"
Next j

a.WriteLine Application.ActiveWorkbook.Path & "~Excel doc folder~" 'append this so that we know which folder to save the InDesign document in

End Sub


Sub Write_Short_Results_Old()
    Application.Calculation = xlCalculationAutomatic
    Application.ScreenUpdating = True
    
    Dim wb As Workbook
    Dim ws As Worksheet
    Dim objUI As Worksheet
    Dim objShort As Worksheet
    
    Set wb = ActiveWorkbook
    Set ws = wb.Sheets("Ins")
    Set objUI = wb.Sheets("UI")
    Set objShort = wb.Sheets("Short")
    
    Dim FindShort As Range
    Const WHAT_TO_FIND As String = """SHORT"" SHEET RESULTS"
    Set FindShort = Sheets("UI").Columns("B").Find(What:=WHAT_TO_FIND, LookIn:=xlValues)
    
    Dim findRow
    findRow = FindShort.Row
    'copy short results to UI Sheet
    Application.Calculate
    Dim instName
    Dim tempInstName
    'instName = ws.Range("F8")

    Dim i
    'i = 3
    'Do
        'i = i + 1
        'tempInstName = wb.Sheets("UI").Cells(4, i)
    'Loop Until instName = tempInstName
    
    i = ws.Range("D3") + 3
    
    'Economic Impact Analysis
    objUI.Cells(2 + findRow, i) = objShort.Range("E7") 'Operations
    objUI.Cells(3 + findRow, i) = objShort.Range("E8") 'Construction
    objUI.Cells(4 + findRow, i) = objShort.Range("E9") 'Research
    objUI.Cells(5 + findRow, i) = objShort.Range("E10") 'Students
    objUI.Cells(6 + findRow, i) = objShort.Range("E11") 'Visitors
    objUI.Cells(7 + findRow, i) = objShort.Range("E12") 'Hospital
    objUI.Cells(8 + findRow, i) = objShort.Range("E14") 'Start-up companies
    objUI.Cells(9 + findRow, i) = objShort.Range("E15") 'Spin-off companies
    objUI.Cells(10 + findRow, i) = objShort.Range("E17") 'Volunteerism
    objUI.Cells(11 + findRow, i) = objShort.Range("E18") 'Alumni
    objUI.Cells(12 + findRow, i) = objShort.Range("E19") 'Total effect
    objUI.Cells(13 + findRow, i) = objShort.Range("E20") 'Percent of regional income
    objUI.Cells(14 + findRow, i) = objShort.Range("C19") 'Total job equivalents
    

    'Student Perspective
    objUI.Cells(16 + findRow, i) = objShort.Range("C32") 'Rate of return
    objUI.Cells(17 + findRow, i) = objShort.Range("C33") 'Benefit/cost ratio
    objUI.Cells(18 + findRow, i) = objShort.Range("C35") 'Payback period
    objUI.Cells(19 + findRow, i) = objShort.Range("C29") 'Total Benefits
    objUI.Cells(20 + findRow, i) = objShort.Range("C30") 'Total Costs

    'Taxpayer Perspective
    objUI.Cells(22 + findRow, i) = objShort.Range("D32") 'Rate of return
    objUI.Cells(23 + findRow, i) = objShort.Range("D33") 'Benefit/cost ratio
    objUI.Cells(24 + findRow, i) = objShort.Range("D35") 'Payback period
    objUI.Cells(25 + findRow, i) = objShort.Range("D29") 'Total Benefits
    objUI.Cells(26 + findRow, i) = objShort.Range("D30") 'Total Costs
    
    'Social Perspective
    objUI.Cells(28 + findRow, i) = objShort.Range("E33") 'Benefit/cost ratio
    objUI.Cells(29 + findRow, i) = objShort.Range("E29") 'Total Benefits
    objUI.Cells(30 + findRow, i) = objShort.Range("E30") 'Total Costs
    
End Sub




