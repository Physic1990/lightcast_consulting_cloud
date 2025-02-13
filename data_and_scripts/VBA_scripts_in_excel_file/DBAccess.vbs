Option Explicit

Dim strConn, objRS, objRSConnect, strSQL, DBName, fRegionToggle, StateToggle, StateName, sRegion, sZIPCodes, startTime, endTime


Sub updateDataRunList()
     'Dim curRow
    'strConn = ConnectionString
    'Set objRSConnect = New ADODB.Recordset
    'strSQL = "SELECT dbname " & _
        "FROM hub.tbldataruns " & _
        "WHERE isAvailable = 1 AND dbname LIKE 'sa_us_20__\__' " & _
        "ORDER BY datarunID DESC"
    'objRSConnect.Open strSQL, strConn

    'curRow = 20
    'Sheets("Ins").Range("F" & curRow & ":F" & (curRow + 7)).ClearContents
    'Do While Not objRSConnect.EOF
        'Sheets("Ins").Range("F" & curRow).Value = objRSConnect("dbname")
        'curRow = curRow + 1
        'objRSConnect.MoveNext
    'Loop
    
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.eis_api.get_datarun import get_datarun; get_datarun();")

End Sub


Public Sub SetDataRun()

    Dim dataRunRow
    'This function gets called right after the rerun button is clicked
    'This makes sure the table in the eis database gets set to the right datarun
    'It also sets the data run variable which is used in several other places
    'As well as the get vector page
    
    'Get the connection string
    strConn = ConnectionString
    
    Set objRS = New ADODB.Recordset
    If Sheets("Ins").Range("g3").Value = 1 Then
        'choose current data run
        Dim curRow
        strSQL = "SELECT dbname FROM hub.tbldataruns where isCurrent = 1 and nationid = 3 AND dbname LIKE 'sa_us_20__\__'"
        objRS.Open strSQL, strConn
        
        DBName = objRS("dbname")
        objRS.Close
    Else
        dataRunRow = 18 + Sheets("Ins").Range("g3").Value
        DBName = Sheets("Ins").Range("F" & dataRunRow).Value
        DBName = "sa_ca_" & Replace(DBName, ".", "_")
    End If

End Sub

Public Sub CloseDBConnection()

    Set objRS = Nothing

End Sub

Private Function ConnectionString()

    Dim dbServerHost

    dbServerHost = "hqdb.ccb"
    
    Set objRS = New ADODB.Recordset
    strConn = "DRIVER={MySQL ODBC 5.3 Unicode Driver};SERVER=" & dbServerHost & ";PORT=3306;DATABASE=hub;USER=seim;PASSWORD=report5;OPTION=3;"
    
    ConnectionString = strConn

End Function



