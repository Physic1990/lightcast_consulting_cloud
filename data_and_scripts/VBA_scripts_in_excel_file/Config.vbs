Option Explicit
#Const App = "Microsoft Excel" 'Adjust when using outside of Excel

Function GetDirectoryPath() As String
    ' Leaving this here for now because we currently don't have #Const App in Utils
    Dim Path As String
    #If App = "Microsoft Excel" Then
        On Error Resume Next 'On Mac, this is called when exiting the Python interpreter
            Path = ActiveWorkbook.Path
        On Error GoTo 0
    #ElseIf App = "Microsoft Word" Then
        Path = ActiveDocument.Path
    #ElseIf App = "Microsoft Access" Then
        Path = CurrentProject.Path ' Won't be transformed for standalone module as ThisProject doesn't exit
    #ElseIf App = "Microsoft PowerPoint" Then
        Path = ActivePresentation.Path ' Won't be transformed for standalone module ThisPresentation doesn't exist
    #Else
        Exit Function
    #End If
    GetDirectoryPath = Path
End Function

Function GetConfigFilePath() As String
    #If Mac Then
        #If MAC_OFFICE_VERSION >= 15 Then
            ' ~/Library/Containers/com.microsoft.Excel/Data/xlwings.conf
            GetConfigFilePath = GetMacDir("Home") & "/" & "xlwings.conf"
        #Else
            ' True home dir
            GetConfigFilePath = GetMacDir("Home") & "/" & ".xlwings/xlwings.conf"
        #End If
    #Else
        GetConfigFilePath = Environ("USERPROFILE") & "\.xlwings\" & "xlwings.conf"
    #End If
End Function

Function GetDirectoryConfigFilePath() As String
    Dim pathSeparator As String
    
    #If Mac Then ' Application.PathSeparator doesn't seem to exist in Access...
        pathSeparator = "/"
    #Else
        pathSeparator = "\"
    #End If
    
    GetDirectoryConfigFilePath = GetDirectoryPath() & pathSeparator & "xlwings.conf"
End Function

Function GetConfigFromSheet()
    Dim lastCell As Range, cell As Range
    #If Mac Then
    Dim d As Dictionary
    Set d = New Dictionary
    #Else
    Dim d As Object
    Set d = CreateObject("Scripting.Dictionary")
    #End If
    Dim sht As Worksheet
    Set sht = ActiveWorkbook.Sheets("xlwings.conf")

    If sht.Range("A2") = "" Then
        Set lastCell = sht.Range("A1")
    Else
        Set lastCell = sht.Range("A1").End(xlDown)
    End If

    For Each cell In Range(sht.Range("A1"), lastCell)
        d.Add UCase(cell.Value), cell.Offset(0, 1).Value
    Next cell
    Set GetConfigFromSheet = d
End Function

Function GetConfig(configKey As String, Optional default As String = "") As Variant
    ' An entry in xlwings.conf sheet overrides the config file/ribbon
    Dim configValue As String
    
    If Application.Name = "Microsoft Excel" Then
    
        If SheetExists("xlwings.conf") = True Then
            GetConfig = GetConfigFromSheet.Item(configKey)
        End If
    End If

    ' An entry in the workbook directory's optional xlwings.conf file overrides the config file/ribbon
    If GetConfig = "" And FileExists(GetDirectoryConfigFilePath()) = True Then
        If GetConfigFromFile(GetDirectoryConfigFilePath(), configKey, configValue) Then
            GetConfig = configValue
        End If
    End If

    ' Global Config
    If GetConfig = "" And FileExists(GetConfigFilePath()) = True Then
        If GetConfigFromFile(GetConfigFilePath(), configKey, configValue) Then
            GetConfig = configValue
        End If
    End If

    ' Defaults
    If GetConfig = "" Then
        GetConfig = default
    End If
    
    ' Expand environment variables
    GetConfig = ExpandEnvironmentStrings(GetConfig)
End Function

Function SaveConfigToFile(sFileName As String, sName As String, Optional sValue As String) As Boolean
'Adopted from http://peltiertech.com/save-retrieve-information-text-files/

  Dim iFileNumA As Long, iFileNumB As Long, lErrLast As Long
  Dim sFile As String, sXFile As String, sVarName As String, sVarValue As String
    
  #If Mac Then
    #If MAC_OFFICE_VERSION < 15 Then
      sFileName = ToMacPath(sFileName)
    #End If
  #End If
      
    
  #If Mac Then
    If Not FileOrFolderExistsOnMac(ParentFolder(sFileName)) Then
  #Else
    If Len(Dir(ParentFolder(sFileName), vbDirectory)) = 0 Then
  #End If
     MkDir ParentFolder(sFileName)
  End If

  ' assume false unless variable is successfully saved
  SaveConfigToFile = False

  ' temporary file
  sFile = sFileName
  sXFile = sFileName & "_temp"

  ' open text file to read settings
  If FileExists(sFile) Then
    'replace existing settings file
    iFileNumA = FreeFile
    Open sFile For Input As iFileNumA
    iFileNumB = FreeFile
    Open sXFile For Output As iFileNumB
      Do While Not EOF(iFileNumA)
        Input #iFileNumA, sVarName, sVarValue
        If sVarName <> sName Then
          Write #iFileNumB, sVarName, sVarValue
        End If
      Loop
      Write #iFileNumB, sName, sValue
      SaveConfigToFile = True
    Close #iFileNumA
    Close #iFileNumB
    FileCopy sXFile, sFile
    Kill sXFile
  Else
    ' make new file
    iFileNumB = FreeFile
    Open sFile For Output As iFileNumB
      Write #iFileNumB, sName, sValue
      SaveConfigToFile = True
    Close #iFileNumB
  End If

End Function

Function GetConfigFromFile(sFile As String, sName As String, Optional sValue As String) As Boolean
'Adopted from http://peltiertech.com/save-retrieve-information-text-files/

  Dim iFileNum As Long, lErrLast As Long
  Dim sVarName As String, sVarValue As String

  #If Mac Then
    #If MAC_OFFICE_VERSION < 15 Then
      sFile = ToMacPath(sFile)
    #End If
  #End If

  ' assume false unless variable is found
  GetConfigFromFile = False

  ' open text file to read settings
  If FileExists(sFile) Then
    iFileNum = FreeFile
    Open sFile For Input As iFileNum
      Do While Not EOF(iFileNum)
        Input #iFileNum, sVarName, sVarValue
        If sVarName = sName Then
          sValue = sVarValue
          GetConfigFromFile = True
          Exit Do
        End If
      Loop
    Close #iFileNum
  End If

End Function


