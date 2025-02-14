Sub Run_EIS()
    Dim python_version
    'python_version = calculate_data_run
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import run_eis; run_eis();")
End Sub

Sub Run_PSEIS()
    Dim python_version
    'python_version = calculate_data_run
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import run_pseis; run_pseis();")
End Sub

Sub Run_Region_and_State_Income()
    Dim python_version
    'python_version = calculate_data_run
    Main.DefineSheetNames
    Application.Calculation = xlManual
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_state_and_region_incomes; import_state_and_region_incomes();")
    objIns.Range("M8").Value = "Done!"
    Application.Calculation = xlAutomatic
End Sub

Sub Run_Credit_Engine()
    Dim python_version
    'python_version = calculate_data_run
    Main.DefineSheetNames
    objIns.Range("M10").Value = ""
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_credit_engine; import_credit_engine();")
    objIns.Range("M8").Value = "Done!"
End Sub

Sub Run_Config()
    Dim python_version
    'python_version = calculate_data_run
    Main.DefineSheetNames
    objIns.Range("M12").Value = ""
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_config; import_config();")
    objIns.Range("M8").Value = "Done!"
End Sub

Sub Run_EIS_Part()
    Dim python_version
    'python_version = calculate_data_run
    Main.DefineSheetNames
    objIns.Range("M13").Value = ""
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_eis; import_eis();")
    objIns.Range("M8").Value = "Done!"
End Sub
 
Sub Run_ERN()
    Dim python_version
    'python_version = calculate_data_run
    Main.DefineSheetNames
    objIns.Range("M14").Value = ""
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_ern; import_ern();")
    objIns.Range("M8").Value = "Done!"
End Sub

Sub Run_GRP()
    Dim python_version
    'python_version = calculate_data_run
    Main.DefineSheetNames
    objIns.Range("M15").Value = ""
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_grp; import_grp();")
    objIns.Range("M8").Value = "Done!"
End Sub

Sub Run_JOB()
    Dim python_version
    'python_version = calculate_data_run
    Main.DefineSheetNames
    objIns.Range("M16").Value = ""
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_job; import_job();")
    objIns.Range("M8").Value = "Done!"
End Sub

Sub Run_MIG()
    Dim python_version
    'python_version = calculate_data_run
    Main.DefineSheetNames
    objIns.Range("M17").Value = ""
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_mig; import_mig();")
    objIns.Range("M8").Value = "Done!"
End Sub

Sub Run_POP()
    Dim python_version
    'python_version = calculate_data_run
    Main.DefineSheetNames
    objIns.Range("M18").Value = ""
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_pop; import_pop();")
    objIns.Range("M8").Value = "Done!"
End Sub

Sub Run_RID()
    Dim python_version
    'python_version = calculate_data_run
    Main.DefineSheetNames
    objIns.Range("M19").Value = ""
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_rid; import_rid();")
    objIns.Range("M8").Value = "Done!"
End Sub

Sub Run_TAX()
    Dim python_version
    'python_version = calculate_data_run
    Main.DefineSheetNames
    objIns.Range("M20").Value = ""
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_tax; import_tax();")
    objIns.Range("M8").Value = "Done!"
End Sub

Sub Run_SPE()
    Dim python_version
    'python_version = calculate_data_run
    Main.DefineSheetNames
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_spe; import_spe(run_type = 'EIS');")
    objIns.Range("M8").Value = "Done!"
End Sub

Sub Run_SPE_completions()
    Dim python_version
    'python_version = calculate_data_run
    Main.DefineSheetNames
    objIns.Range("M26").Value = ""
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_spe; import_spe(run_type = 'completers only');")
    objIns.Range("M8").Value = "Done!"
End Sub

Sub Run_MTX()
    Dim python_version
    'python_version = calculate_data_run
    Main.DefineSheetNames
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_mtx; import_mtx();")
    objIns.Range("M8").Value = "Done!"
End Sub

Sub Run_OCC_EARNINGS()
    Dim python_version
    'python_version = calculate_data_run
    Main.DefineSheetNames
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_occ_earnings; import_occ_earnings();")
    objIns.Range("M8").Value = "Done!"
End Sub

Sub Run_OCC_OPENINGS()
    Dim python_version
    'python_version = calculate_data_run
    Main.DefineSheetNames
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_occ_openings; import_occ_openings();")
    objIns.Range("M8").Value = "Done!"
End Sub

Sub Run_REGION_UNEMP()
    Dim python_version
    'python_version = calculate_data_run
    Main.DefineSheetNames
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_region_unemp; import_region_unemp();")
    objIns.Range("M8").Value = "Done!"
End Sub
Sub Run_MINWAGE()
    Dim python_version
    Main.DefineSheetNames
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_minwage; import_minwage();")
    objIns.Range("M8").Value = "Done!"
End Sub
Sub Run_MINCER()
    Dim python_version
    Main.DefineSheetNames
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_mincer; import_mincer();")
    objIns.Range("M8").Value = "Done!"
End Sub
Sub Run_PSEIS_OCC()
    Main.DefineSheetNames
    objIns.Range("P11").Value = ""
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_pseis_occ_data; import_pseis_occ_data();")
    objIns.Range("P9").Value = "Done!"
End Sub

Sub Run_PSEIS_OCC_ED()
    Main.DefineSheetNames
    objIns.Range("P12").Value = ""
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_pseis_occ_ed_data; import_pseis_occ_ed_data();")
    objIns.Range("P9").Value = "Done!"
End Sub

Sub Run_PSEIS_ED_DEMO()
    Main.DefineSheetNames
    objIns.Range("P13").Value = ""
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_pseis_ed_demo_data; import_pseis_ed_demo_data();")
    objIns.Range("P9").Value = "Done!"
End Sub
Sub Run_PSEIS_COMPLETIONS()
    Main.DefineSheetNames
    objIns.Range("P14").Value = ""
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_pseis_completions_data; import_pseis_completions_data();")
    objIns.Range("P9").Value = "Done!"
End Sub
Sub Run_PSEIS_MAP_OCCS()
    Main.DefineSheetNames
    objIns.Range("P15").Value = ""
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_pseis_occ_mapping; import_pseis_occ_mapping();")
    objIns.Range("P9").Value = "Done!"
End Sub
Sub Run_PSEIS_JOB_GROWTH()
    Main.DefineSheetNames
    objIns.Range("P16").Value = ""
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_pseis_job_growth_data; import_pseis_job_growth_data();")
    objIns.Range("P9").Value = "Done!"
End Sub
Sub Run_PSEIS_UNIQUE_POST()
    Main.DefineSheetNames
    objIns.Range("P17").Value = ""
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_pseis_unique_postings_data; import_pseis_unique_postings_data();")
    objIns.Range("P9").Value = "Done!"
End Sub
Sub Run_PSEIS_TOP_EMPLOYERS()
    Main.DefineSheetNames
    objIns.Range("P18").Value = ""
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_pseis_top_employers_data; import_pseis_top_employers_data();")
    objIns.Range("P9").Value = "Done!"
End Sub
Sub Run_PSEIS_OCC_DEMO()
    Main.DefineSheetNames
    objIns.Range("P19").Value = ""
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.new_run_eis import import_pseis_occ_demo_data; import_pseis_occ_demo_data();")
    objIns.Range("P9").Value = "Done!"
End Sub

Sub Run_formula_insertion_for_income_sheet()
    Dim python_version
    Main.DefineSheetNames
    
    Dim sheetName As String
    sheetName = GetSheetName()

    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.region_and_state_income.xl_formula_revert import main; main(income_sheet_name='" & sheetName & "');")
End Sub

Function GetSheetName() As String
    GetSheetName = ActiveSheet.Name
End Function

Sub Write_Short_Results()
    Main.DefineSheetNames
    RunPython ("import sys; sys.path.append('C:\\EIS'); from Processes.eis_automation.eis_api.short_sheet import main; main();")
End Sub

'Should no longer need this function since the eis_automation folder no longer exists as of 2020.3
Function calculate_data_run()
    Dim dataRunRow
    Dim datarun
    If Sheets("Ins").Range("g3").Value = 1 Then
        datarun = Sheets("Ins").Range("F20").Value
    Else
        dataRunRow = 18 + Sheets("Ins").Range("g3").Value
        datarun = Sheets("Ins").Range("F" & dataRunRow).Value
    End If
    
    'datarun = Replace(datarun, "sa_us_", "")
    'datarun = Replace(datarun, "_", "")
    datarun = Replace(datarun, ".", "")
    datarun = CLng(datarun)
    
    If datarun <= 20201 Then
        calculate_data_run = "eis_automation"
    Else
        calculate_data_run = "eis_automation"
    End If
        
End Function

