Option Explicit

#If VBA7 Then
    #If Mac Then
        Private Declare PtrSafe Function system Lib "libc.dylib" (ByVal Command As String) As Long
    #End If
    #If Win64 Then
        Const XLPyDLLName As String = "xlwings64-0.19.4.dll"
        Declare PtrSafe Function XLPyDLLActivateAuto Lib "xlwings64-0.19.4.dll" (ByRef result As Variant, Optional ByVal Config As String = "", Optional ByVal mode As Long = 1) As Long
        Declare PtrSafe Function XLPyDLLNDims Lib "xlwings64-0.19.4.dll" (ByRef src As Variant, ByRef dims As Long, ByRef transpose As Boolean, ByRef dest As Variant) As Long
        Declare PtrSafe Function XLPyDLLVersion Lib "xlwings64-0.19.4.dll" (tag As String, VERSION As Double, arch As String) As Long
    #Else
        Private Const XLPyDLLName As String = "xlwings32-0.19.4.dll"
        Declare PtrSafe Function XLPyDLLActivateAuto Lib "xlwings32-0.19.4.dll" (ByRef result As Variant, Optional ByVal Config As String = "", Optional ByVal mode As Long = 1) As Long
        Private Declare PtrSafe Function XLPyDLLNDims Lib "xlwings32-0.19.4.dll" (ByRef src As Variant, ByRef dims As Long, ByRef transpose As Boolean, ByRef dest As Variant) As Long
        Private Declare PtrSafe Function XLPyDLLVersion Lib "xlwings32-0.19.4.dll" (tag As String, VERSION As Double, arch As String) As Long
    #End If
    Private Declare PtrSafe Function LoadLibrary Lib "kernel32" Alias "LoadLibraryA" (ByVal lpLibFileName As String) As Long
#Else
    #If Mac Then
        Private Declare Function system Lib "libc.dylib" (ByVal Command As String) As Long
    #End If
    Private Const XLPyDLLName As String = "xlwings32-0.19.4.dll"
    Private Declare Function XLPyDLLActivateAuto Lib "xlwings32-0.19.4.dll" (ByRef result As Variant, Optional ByVal Config As String = "", Optional ByVal mode As Long = 1) As Long
    Private Declare Function XLPyDLLNDims Lib "xlwings32-0.19.4.dll" (ByRef src As Variant, ByRef dims As Long, ByRef transpose As Boolean, ByRef dest As Variant) As Long
    Private Declare Function LoadLibrary Lib "kernel32" Alias "LoadLibraryA" (ByVal lpLibFileName As String) As Long
    Declare Function XLPyDLLVersion Lib "xlwings32-0.19.4.dll" (tag As String, VERSION As Double, arch As String) As Long
#End If

Public Const XLWINGS_VERSION As String = "0.19.4"

Public Function RunPython(PythonCommand As String)
    ' Public API: Runs the Python command, e.g.: to run the function foo() in module bar, call the function like this:
    ' RunPython ("import bar; bar.foo()")

    Dim INTERPRETER As String, PYTHONPATH As String
    Dim OPTIMIZED_CONNECTION As Boolean
    Dim sht As Worksheet

    INTERPRETER = GetConfig("INTERPRETER", "python")
    PYTHONPATH = GetDirectoryPath() & ";" & GetBaseName(ActiveWorkbook.FullName) & ".zip;" & GetConfig("PYTHONPATH")
    OPTIMIZED_CONNECTION = GetConfig("USE UDF SERVER", False)

    ' Handle embedded Python code
    For Each sht In ActiveWorkbook.Worksheets
        If Right$(sht.Name, 3) = ".py" Then
            PythonCommand = "import xlwings.pro;xlwings.pro.runpython_embedded_code('" & PythonCommand & "')"
            Exit For
        End If
    Next

    ' Call Python platform-dependent
    #If Mac Then
        Application.StatusBar = "Running..."  ' Non-blocking way of giving feedback that something is happening
        ExecuteMac PythonCommand, INTERPRETER, PYTHONPATH
    #Else
        If OPTIMIZED_CONNECTION = True Then
            Py.SetAttr Py.Module("xlwings._xlwindows"), "BOOK_CALLER", ActiveWorkbook
            Py.Exec "" & PythonCommand & ""
        Else
            ExecuteWindows False, PythonCommand, INTERPRETER, PYTHONPATH
        End If
    #End If
End Function


Sub ExecuteMac(PythonCommand As String, PYTHON_MAC As String, Optional PYTHONPATH As String)
    #If Mac Then
    Dim PythonInterpreter As String, RunCommand As String, Log As String
    Dim ParameterString As String, ExitCode As String, CondaCmd As String, CondaPath As String, CondaEnv As String, LOG_FILE As String

    ' Transform paths
    PYTHONPATH = ToPosixPath(PYTHONPATH)

    If PYTHON_MAC <> "" Then
        If PYTHON_MAC <> "python" And PYTHON_MAC <> "pythonw" Then
            PythonInterpreter = ToPosixPath(PYTHON_MAC)
        Else
            PythonInterpreter = PYTHON_MAC
        End If
    Else
        PythonInterpreter = "python"
    End If

    ' Sandbox location that requires no file access confirmation
    ' TODO: Use same logic with GUID like for Windows. Only here the GUID will need to be passed back to CleanUp()
    LOG_FILE = Environ("HOME") + "/xlwings.log" '/Users/<User>/Library/Containers/com.microsoft.Excel/Data/xlwings.log

    ' Delete Log file just to make sure we don't show an old error
    On Error Resume Next
        Kill LOG_FILE
    On Error GoTo 0

    ' ParameterSting with all paramters (AppleScriptTask only accepts a single parameter)
    ParameterString = PYTHONPATH + ";"
    ParameterString = ParameterString + "|" + PythonInterpreter
    ParameterString = ParameterString + "|" + PythonCommand
    ParameterString = ParameterString + "|" + ActiveWorkbook.Name
    ParameterString = ParameterString + "|" + Left(Application.Path, Len(Application.Path) - 4)
    ParameterString = ParameterString + "|" + LOG_FILE

    On Error GoTo AppleScriptErrorHandler
        ExitCode = AppleScriptTask("xlwings.applescript", "VbaHandler", ParameterString)
    On Error GoTo 0

    ' If there's a log at this point (normally that will be from the shell only, not Python) show it and reset the StatusBar
    On Error Resume Next
        Log = ReadFile(LOG_FILE)
        If Log = "" Then
            Exit Sub
        Else
            ShowError (LOG_FILE)
            Application.StatusBar = False
        End If
        Exit Sub
    On Error GoTo 0

AppleScriptErrorHandler:
    MsgBox "To enable RunPython, please run 'xlwings runpython install' in a terminal once and try again.", vbCritical
    #End If
End Sub

Sub ExecuteWindows(IsFrozen As Boolean, PythonCommand As String, PYTHON_WIN As String, _
                   Optional PYTHONPATH As String, Optional FrozenArgs As String)
    ' Call a command window and change to the directory of the Python installation or frozen executable
    ' Note: If Python is called from a different directory with the fully qualified path, pywintypesXX.dll won't be found.
    ' This seems to be a general issue with pywin32, see http://stackoverflow.com/q/7238403/918626

    Dim Wsh As Object
    Dim WaitOnReturn As Boolean: WaitOnReturn = True
    Dim WindowStyle As Integer: WindowStyle = 1
    Set Wsh = CreateObject("WScript.Shell")
    Dim DriveCommand As String, RunCommand As String
    Dim PythonInterpreter As String, PythonDir As String, CondaCmd As String, CondaPath As String, CondaEnv As String
    Dim ExitCode As Integer
    Dim LOG_FILE As String
    
    LOG_FILE = Environ("Temp") & "\xlwings-" & CreateGUID() & ".log"

    If Not IsFrozen And (PYTHON_WIN <> "python" And PYTHON_WIN <> "pythonw") Then
        If FileExists(PYTHON_WIN) Then
            PythonDir = ParentFolder(PYTHON_WIN)
        Else
            MsgBox "Could not find Interpreter!", vbCritical
            Exit Sub
        End If
    Else
        PythonDir = ""  ' TODO: hack
    End If

    If Left$(PYTHON_WIN, 2) Like "[A-Za-z]:" Then
        ' If Python is installed on a mapped or local drive, change to drive, then cd to path
        DriveCommand = Left$(PYTHON_WIN, 2) & " & cd """ & PythonDir & """ & "
    ElseIf Left$(PYTHON_WIN, 2) = "\\" Then
        ' If Python is installed on a UNC path, temporarily mount and activate a drive letter with pushd
        DriveCommand = "pushd """ & PythonDir & """ & "
    End If

    ' Run Python with the "-c" command line switch: add the path of the python file and run the
    ' Command as first argument, then provide the Name and "from_xl" as 2nd and 3rd arguments.
    ' Then redirect stderr to the LOG_FILE and wait for the call to return.

    If PYTHON_WIN <> "python" And PYTHON_WIN <> "pythonw" Then
        PythonInterpreter = Chr(34) & PYTHON_WIN & Chr(34)
    Else
        PythonInterpreter = "python"
    End If

    CondaPath = GetConfig("CONDA PATH")
    CondaEnv = GetConfig("CONDA ENV")
    
    ' Handle spaces in path (for UDFs, this is handled via nested quotes instead, see XLPyCommand)
    CondaPath = Replace(CondaPath, " ", "^ ")
    
    If CondaPath <> "" And CondaEnv <> "" Then
        CondaCmd = CondaPath & "\condabin\conda activate " & CondaEnv & " && "
    Else
        CondaCmd = ""
    End If

    If IsFrozen = False Then
        RunCommand = CondaCmd & PythonInterpreter & " -B -c ""import sys, os; sys.path[0:0]=os.path.normcase(os.path.expandvars(r'" & PYTHONPATH & "')).split(';'); " & PythonCommand & """ "
    ElseIf IsFrozen = True Then
        RunCommand = Chr(34) & PythonCommand & Chr(34) & " " & FrozenArgs & " "
    End If

    ExitCode = Wsh.Run("cmd.exe /C " & DriveCommand & _
                   RunCommand & _
                   " --wb=" & """" & ActiveWorkbook.Name & """ --from_xl=1" & " --app=" & Chr(34) & _
                   Application.Path & "\" & Application.Name & Chr(34) & " --hwnd=" & Chr(34) & Application.Hwnd & Chr(34) & _
                   " 2> """ & LOG_FILE & """ ", _
                   WindowStyle, WaitOnReturn)

    'If ExitCode <> 0 then there's something wrong
    If ExitCode <> 0 Then
        Call ShowError(LOG_FILE)
    End If

    ' Delete file after the error message has been shown
    On Error Resume Next
        Kill LOG_FILE
    On Error GoTo 0

    ' Clean up
    Set Wsh = Nothing
End Sub

Public Function RunFrozenPython(Executable As String, Optional Args As String)
    ' Runs a Python executable that has been frozen by PyInstaller and the like. Call the function like this:
    ' RunFrozenPython "C:\path\to\frozen_executable.exe", "arg1 arg2". Currently not implemented for Mac.

    ' Call Python
    #If Mac Then
        MsgBox "This functionality is not yet supported on Mac." & vbNewLine & _
               "Please run your scripts directly in Python!", vbCritical + vbOKOnly, "Unsupported Feature"
    #Else
        ExecuteWindows True, Executable, ParentFolder(Executable), , Args
    #End If
End Function

Function GetUdfModules() As String
    Dim UDF_MODULES As String
    Dim sht As Worksheet
    GetUdfModules = GetConfig("UDF MODULES")
    ' Remove trailing ";"
    If Right$(GetUdfModules, 1) = ";" Then
        GetUdfModules = Left$(GetUdfModules, Len(GetUdfModules) - 1)
    End If
    ' Automatically add embedded code sheets
    For Each sht In ActiveWorkbook.Worksheets
        If Right$(sht.Name, 3) = ".py" Then
            If GetUdfModules = "" Then
                GetUdfModules = Left$(sht.Name, Len(sht.Name) - 3)
            Else
                GetUdfModules = GetUdfModules & ";" & Left$(sht.Name, Len(sht.Name) - 3)
            End If
        End If
    Next
    If GetUdfModules = "" Then
        GetUdfModules = Left$(ActiveWorkbook.Name, Len(ActiveWorkbook.Name) - 5) ' assume that it ends in .xlsm
    End If
    
End Function

Private Sub CleanUp()
    'On Mac only, this function is being called after Python is done (using Python's atexit handler)
    Dim LOG_FILE As String

    #If MAC_OFFICE_VERSION >= 15 Then
        LOG_FILE = Environ("HOME") + "/xlwings.log" '~/Library/Containers/com.microsoft.Excel/Data/xlwings.log
    #Else
        LOG_FILE = "/tmp/xlwings.log"
    #End If

    'Show the LOG_FILE as MsgBox if not empty
    On Error Resume Next
    If ReadFile(LOG_FILE) <> "" Then
        Call ShowError(LOG_FILE)
    End If
    On Error GoTo 0

    'Clean up
    Application.StatusBar = False
    Application.ScreenUpdating = True
    On Error Resume Next
        #If MAC_OFFICE_VERSION >= 15 Then
            Kill LOG_FILE
        #Else
            KillFileOnMac ToMacPath(ToPosixPath(LOG_FILE))
        #End If
    On Error GoTo 0
End Sub

Function XLPyCommand()
    Dim PYTHON_WIN As String, PYTHONPATH As String, LOG_FILE As String, tail As String, LicenseKey As String, LicenseKeyEnvString As String
    Dim CondaCmd As String, CondaPath As String, CondaEnv As String
    Dim DEBUG_UDFS As Boolean

    If GetDirectoryPath() <> "" Then
        PYTHONPATH = GetDirectoryPath() & ";" & GetBaseName(ActiveWorkbook.FullName) & ".zip;" & GetConfig("PYTHONPATH")
    Else
        PYTHONPATH = GetConfig("PYTHONPATH")
    End If


    PYTHON_WIN = GetConfig("INTERPRETER", "pythonw")
    DEBUG_UDFS = GetConfig("DEBUG UDFS", False)


    CondaPath = GetConfig("CONDA PATH")
    CondaEnv = GetConfig("CONDA ENV")

    If (PYTHON_WIN = "python" Or PYTHON_WIN = "pythonw") And (CondaPath <> "" And CondaEnv <> "") Then
        CondaCmd = Chr(34) & Chr(34) & CondaPath & "\condabin\conda" & Chr(34) & " activate " & CondaEnv & " && "
        PYTHON_WIN = "cmd.exe /K " & CondaCmd & PYTHON_WIN
    End If

    If SheetExists("xlwings.conf") = True Then
        LicenseKey = GetConfigFromSheet.Item("LICENSE_KEY")
        If LicenseKey <> "" Then
            LicenseKeyEnvString = "os.environ['XLWINGS_LICENSE_KEY']='" & LicenseKey & "';"
        Else
            LicenseKeyEnvString = ""
        End If
    Else
        LicenseKeyEnvString = ""
    End If
    

    If DEBUG_UDFS = True Then
        XLPyCommand = "{506e67c3-55b5-48c3-a035-eed5deea7d6d}"
    Else
        tail = " -B -c ""import sys, os;" & LicenseKeyEnvString & "sys.path[0:0]=os.path.normcase(os.path.expandvars(r'" & PYTHONPATH & "')).split(';');import xlwings.server; xlwings.server.serve('$(CLSID)')"""
        XLPyCommand = PYTHON_WIN & tail
    End If
End Function

Private Sub XLPyLoadDLL()
    Dim PYTHON_WIN As String, CondaCmd As String, CondaPath As String, CondaEnv As String

    PYTHON_WIN = GetConfig("INTERPRETER", "pythonw")
    CondaPath = GetConfig("CONDA PATH")
    CondaEnv = GetConfig("CONDA ENV")

    If (PYTHON_WIN = "python" Or PYTHON_WIN = "pythonw") And (CondaPath <> "" And CondaEnv <> "") Then
        ' This only works if the envs are in their default location
        ' Otherwise you'll have to add the full path for the interpreter in addition to the conda infos
        If CondaEnv = "base" Then
            PYTHON_WIN = CondaPath & "\" & PYTHON_WIN
        Else
            PYTHON_WIN = CondaPath & "\envs\" & CondaEnv & "\" & PYTHON_WIN
        End If
    End If

    If (PYTHON_WIN <> "python" And PYTHON_WIN <> "pythonw") Or (CondaPath <> "" And CondaEnv <> "") Then
        If LoadLibrary(ParentFolder(PYTHON_WIN) + "\" + XLPyDLLName) = 0 Then  ' Standard installation
            If LoadLibrary(ParentFolder(ParentFolder(PYTHON_WIN)) + "\" + XLPyDLLName) = 0 Then  ' Virtualenv
                Err.Raise 1, Description:= _
                    "Could not load " + XLPyDLLName + " from either of the following folders: " _
                    + vbCrLf + ParentFolder(PYTHON_WIN) _
                    + vbCrLf + ", " + ParentFolder(ParentFolder(PYTHON_WIN))
            End If
        End If
    End If
End Sub

Function NDims(ByRef src As Variant, dims As Long, Optional transpose As Boolean = False)
    XLPyLoadDLL
    If 0 <> XLPyDLLNDims(src, dims, transpose, NDims) Then Err.Raise 1001, Description:=NDims
End Function

Function Py()
    XLPyLoadDLL
    If 0 <> XLPyDLLActivateAuto(Py, XLPyCommand, 1) Then Err.Raise 1000, Description:=Py
End Function

Sub KillPy()
    XLPyLoadDLL
    Dim unused
    If 0 <> XLPyDLLActivateAuto(unused, XLPyCommand, -1) Then Err.Raise 1000, Description:=unused
End Sub

Sub ImportPythonUDFs()
    Dim tempPath As String, errorMsg As String
    On Error GoTo ImportError
        tempPath = Py.Str(Py.Call(Py.Module("xlwings"), "import_udfs", Py.Tuple(GetUdfModules, ActiveWorkbook)))
    Exit Sub
ImportError:
    errorMsg = Err.Description & " " & Err.Number
    MsgBox errorMsg, vbCritical, "Error"
End Sub

Private Sub GetDLLVersion()
    ' Currently only for testing
    Dim tag As String, arch As String
    Dim ver As Double
    XLPyDLLVersion tag, ver, arch
    Debug.Print tag
    Debug.Print ver
    Debug.Print arch
End Sub





