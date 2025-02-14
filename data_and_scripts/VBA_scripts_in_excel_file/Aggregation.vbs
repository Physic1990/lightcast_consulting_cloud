Public blnAgg
Dim obj

Sub GetStates()
    'Declare variables
    Dim i
    Dim newListItem
    
    'Clear the cells
    
    Worksheets("Ins").Shapes("List Box 2051").ControlFormat.RemoveAllItems
        
    'Loop through all cells that have State names in them
    For i = 4 To 256
        newListItem = Worksheets("UI").Cells(9, i).Value
        If Worksheets("UI").Cells(9, i).Value <> "" Then
            Worksheets("Ins").Shapes("List Box 2051").ControlFormat.AddItem newListItem
            'Worksheets("Ins").Cells(j, 11).Value = Worksheets("UI").Cells(9, i).Value
        End If
    Next
    
End Sub

Sub StateAgg()
    
    Dim State As String
    
    With Worksheets("Ins").Shapes("List Box 2051").ControlFormat
        State = .List(.Value)
    End With
            
    Dim i As Integer
    Dim column As Integer
    
    Dim bar_prog As Single
    Dim bar_message As String
    Dim Numselections As Single
    
    For i = 4 To 256
        If Worksheets("UI").Cells(9, i).Value = State Then
            Numselections = Numselections + 1
        End If
    Next i
    
    column = 20
    
    'Clear the cells
    Worksheets("Ins").Range(Cells(8, 20), Cells(2218, 119)).ClearContents
    
    'Loop through all cells that have State names in them
    For i = 4 To 256
        If Worksheets("UI").Cells(9, i).Value = State Then
            
            bar_prog = (column - 20) * 100 / Numselections
            bar_message = "Completed " + CStr(column - 20) + "/" + CStr(Numselections) + " institutions"
            state_agg_progress bar_prog, bar_message
            
            'Get the college name
            'strCollege = Worksheets("UI").Cells(4, i).Value
        
            'pop it in
            Worksheets("Ins").Range("D3").Value = i - 3 'everything above this line is essentially instantaneous
            
            'Run the model
            Main.MainProcess '19 seconds to perform
            
            'Now copy the calculated something-or-other to the other place under the stuff on that one page
            Worksheets("Ins").Range(Cells(8, column), Cells(5008, column)).Value = Worksheets("Agg Vector").Range("C2:C5002").Value
            
            'Increment
            column = column + 1
                

        End If
    Next
    
    bar_prog = 100
    bar_message = "Completed " + CStr(Numselections) + "/" + CStr(Numselections) + " institutions"
    state_agg_progress bar_prog, bar_message
    state_agg_updates "Done!"

End Sub


Sub CustomAgg()
    
    Dim i As Long
    
    Dim column As Integer
    
    Dim bar_prog As Single
    Dim bar_message As String
    Dim Numselections As Single
    
    Application.Calculate
    
    With ActiveSheet.ListBoxes("List Box 2052")
        For i = 1 To .ListCount
            If .Selected(i) Then
                Numselections = Numselections + 1
            End If
        Next i
    End With
    
    column = 20
    
    'Clear the cells
    Worksheets("Ins").Range(Cells(8, 20), Cells(2218, 119)).ClearContents
    
    With ActiveSheet.ListBoxes("List Box 2052")
        For i = 1 To .ListCount
            If .Selected(i) Then
                'MsgBox .List(i) 'item i selected
                
                bar_prog = (column - 20) * 100 / Numselections
                bar_message = "Completed " + CStr(column - 20) + "/" + CStr(Numselections) + " institutions"
                agg_progress bar_prog, bar_message
                
                'pop it in
                Worksheets("Ins").Range("D3").Value = i 'everything above this line is essentially instantaneous
                
                'Run the model
                Main.MainProcess '19 seconds to perform
                
                'Now copy the calculated something-or-other to the other place under the stuff on that one page
                Worksheets("Ins").Range(Cells(8, column), Cells(5008, column)).Value = Worksheets("Agg Vector").Range("C2:C5002").Value
                
                'Increment
                column = column + 1
                
                
            End If
        Next i
    End With
    
    bar_prog = 100
    bar_message = "Completed " + CStr(Numselections) + "/" + CStr(Numselections) + " institutions"
    agg_progress bar_prog, bar_message
    agg_updates "Done!"

End Sub

Sub agg_progress(pctCompl As Single, progressReport As String)

UserForm2.Text.Caption = progressReport
UserForm2.Bar.Width = pctCompl * 2

DoEvents

End Sub

Sub agg_updates(progressReport As String)

UserForm2.Update.Caption = progressReport

End Sub

Sub state_agg_progress(pctCompl As Single, progressReport As String)

UserForm3.Text.Caption = progressReport
UserForm3.Bar.Width = pctCompl * 2

DoEvents

End Sub

Sub state_agg_updates(progressReport As String)

UserForm3.Update.Caption = progressReport

End Sub

Sub run_agg()

Application.Calculate

UserForm2.Show

End Sub

Sub run_state_agg()

Application.Calculate

UserForm3.Show

End Sub




