Option Explicit

' Continuing Feed
Public Sub callCreditEngine()

    Application.ScreenUpdating = True
    'clear cumulative che vector
    objContinuingFeed.Range("AB4:AB9999").ClearContents

    If objContinuingFeed.Range("C7").Value <> 0 Then
        objIns.Range("M8").Value = "Running Credit Engine at Professional Level"
        creditEngine (7)
    End If
    If objContinuingFeed.Range("C8").Value <> 0 Then
        objIns.Range("M8").Value = "Running Credit Engine at Ph.D. Level"
        creditEngine (8)
    End If
    If objContinuingFeed.Range("C9").Value <> 0 Then
        objIns.Range("M8").Value = "Running Credit Engine at Masters Level"
        creditEngine (9)
    End If
    If objContinuingFeed.Range("C10").Value <> 0 Then
        objIns.Range("M8").Value = "Running Credit Engine at Bachelors Level"
        creditEngine (10)
    End If
    If objContinuingFeed.Range("C11").Value <> 0 Then
        objIns.Range("M8").Value = "Running Credit Engine at Associates Level"
        creditEngine (11)
    End If
    If objContinuingFeed.Range("C12").Value <> 0 Then
        objIns.Range("M8").Value = "Running Credit Engine at Certificate Level"
        creditEngine (12)
    End If
    Application.ScreenUpdating = False
    
End Sub

Sub creditEngine(categoryRow)

    Dim startRow, achievementRow, curMean, rangeLength, chiStartRow, studentsCol
    Dim chiCol, finalCHECol, numStudents, rowCounter, finalCHEVal, lastNumStudents
    Dim endYrPos, chiCounter, curNumStudents, lastEndYrPos
    Dim normDistCol, normDistNormCol, studentDistCol, stdDevCell, availableRange, custMean
    Dim counter, i, j, deflator, finalCHE, curDeflator
    
    objContinuingFeed.Calculate
    
    If objContinuingFeed.Range("B" & categoryRow).Value = "Professional" Then
        startRow = 275
        achievementRow = 334
    Else
        startRow = objContinuingFeed.Range("G" & categoryRow).Value
        achievementRow = objContinuingFeed.Range("H" & categoryRow).Value
    End If
    
    curMean = objContinuingFeed.Range("D" & categoryRow).Value
    rangeLength = 42
    chiStartRow = 18
    
    studentsCol = objContinuingFeed.Range("I" & categoryRow).Value
    chiCol = "D"
    finalCHECol = "AB"
    
    'update mean for this category
    objContinuingFeed.Range("C14").Value = curMean
    objContinuingFeed.Calculate
    
    'Loop for as many steps as we have in the ladder minus 3 steps away from achievement
    For i = startRow To (achievementRow - rangeLength - 3)
        
        'find the number of students at this step
        numStudents = objContinuingFeed.Range(studentsCol & i).Value
        
        'add 3 steps to the counter and begin multiplying the number of students by the normalized chi squared vector (for the length of the range)
        rowCounter = i + 3
        
        'Update the first two rows of this set with the number of students
        For j = i + 1 To i + 2
            finalCHEVal = objContinuingFeed.Range(finalCHECol & j).Value
            objContinuingFeed.Range(finalCHECol & j).Value = finalCHEVal + numStudents
        Next
        
        'by now we should have the distribution of the students (from our current step) at the end of the analysis year
        chiCounter = chiStartRow
        lastNumStudents = numStudents
        For j = rowCounter To (i + rangeLength - 1)
        
            endYrPos = objContinuingFeed.Range(chiCol & chiCounter).Value * numStudents
            
            'objContinuingFeed.Range(endYearCol & j).Value = endYrPos
            chiCounter = chiCounter + 1
            
            'grab our final che col value to add to
            finalCHEVal = objContinuingFeed.Range(finalCHECol & j).Value
            
            curNumStudents = lastNumStudents - lastEndYrPos
            objContinuingFeed.Range(finalCHECol & j).Value = curNumStudents + finalCHEVal
            
            lastEndYrPos = endYrPos
            lastNumStudents = curNumStudents
        Next
    
    Next
    
    objContinuingFeed.Calculate

    '=======================================================================================
    'we've now exhausted the usefulness of the CHI distribution
    'from here on out we need to make up our own average based
    'on the amount of steps left before achievement.  We will
    'figure a new average and use a normal distribution on the
    'range left
    normDistCol = "AD"
    normDistNormCol = "AE"
    studentDistCol = "AF"
    stdDevCell = "G14"
    
    If objContinuingFeed.Range("B" & categoryRow).Value = "Professional" Then
        startRow = 275
        achievementRow = 334

        For i = (achievementRow - 60 - 2) To (achievementRow - 4)

            'inside here we need to take the range left and find the average
            'number of credits they can move, then normal dist them

            'number of students at this level
            numStudents = objContinuingFeed.Range(studentsCol & i - 60).Value

            'available steps to distribute over
            availableRange = (achievementRow) - i - 3

            'because we have the length of the available range
            'we can now get the mean
            custMean = (availableRange - 3) / 2

            'set the standardDeviation
            objContinuingFeed.Range(stdDevCell).Value = "=STDEV(M1:M" & (availableRange) & ")"

            'now go through and do a temp row for the normdist
            objContinuingFeed.Range(normDistCol & "4:" & studentDistCol & "334").ClearContents
            counter = 0

            For j = (i + 3) To (i + availableRange)
                objContinuingFeed.Range(normDistCol & j).Value = "=NORMDIST(" & counter & ", " & custMean & ", " & stdDevCell & ",false)"
                objContinuingFeed.Range(normDistNormCol & j).Value = "=" & normDistCol & j & "/SUM(" & normDistCol & (i + 3) & ":" & normDistCol & (i + availableRange) & ")"
                objContinuingFeed.Range(studentDistCol & j).Value = "=" & normDistNormCol & j & "*" & numStudents
                counter = counter + 1
            Next

            objContinuingFeed.Calculate

            'After we have our numbers, update the final che col
            deflator = 0
            For j = i To (i + availableRange)
                finalCHE = objContinuingFeed.Range(finalCHECol & j).Value
                If j <= i + 2 Or availableRange <= 4 Then
                    objContinuingFeed.Range(finalCHECol & j) = finalCHE + numStudents
                Else
                    curDeflator = objContinuingFeed.Range(studentDistCol & j).Value
                    deflator = deflator + curDeflator
                    objContinuingFeed.Range(finalCHECol & j) = finalCHE + (numStudents - deflator)
                End If
            Next
        Next

    Else
        startRow = objContinuingFeed.Range("G" & categoryRow).Value
        achievementRow = objContinuingFeed.Range("H" & categoryRow).Value

        For i = (achievementRow - rangeLength - 2) To (achievementRow - 4)
            'inside here we need to take the range left and find the average
            'number of credits they can move, then normal dist them

            'number of students at this level
            numStudents = objContinuingFeed.Range(studentsCol & i).Value

            'available steps to distribute over
            availableRange = (achievementRow) - i - 3

            'because we have the length of the available range
            'we can now get the mean
            custMean = (availableRange - 3) / 2

            'set the standardDeviation
            objContinuingFeed.Range(stdDevCell).Value = "=STDEV(M1:M" & (availableRange) & ")"

            'now go through and do a temp row for the normdist
            objContinuingFeed.Range(normDistCol & "4:" & studentDistCol & "275").ClearContents
            counter = 0

            For j = (i + 3) To (i + availableRange)
                objContinuingFeed.Range(normDistCol & j).Value = "=NORMDIST(" & counter & ", " & custMean & ", " & stdDevCell & ",false)"
                objContinuingFeed.Range(normDistNormCol & j).Value = "=" & normDistCol & j & "/SUM(" & normDistCol & (i + 3) & ":" & normDistCol & (i + availableRange) & ")"
                objContinuingFeed.Range(studentDistCol & j).Value = "=" & normDistNormCol & j & "*" & numStudents
                counter = counter + 1
            Next

            objContinuingFeed.Calculate

            'After we have our numbers, update the final che col
            deflator = 0
            For j = i To (i + availableRange)
                finalCHE = objContinuingFeed.Range(finalCHECol & j).Value
                If j <= i + 2 Or availableRange <= 4 Then
                    objContinuingFeed.Range(finalCHECol & j) = finalCHE + numStudents
                Else
                    curDeflator = objContinuingFeed.Range(studentDistCol & j).Value
                    deflator = deflator + curDeflator
                    objContinuingFeed.Range(finalCHECol & j) = finalCHE + (numStudents - deflator)
                End If
            Next
        Next
    End If

    Application.Calculate

End Sub

' Credit Engine
Sub callCategories()
    
    'Clear the box
    objCreditEngine.Range("O7:Z278").ClearContents

    'Category 1
    Call callRange(7, False, False, False)

    'Category 2
    Call callRange(8, False, False, False)
 
    'Category 3
    Call callRange(9, False, False, False)

    'Category 4
    Call callRange(10, False, False, False)

    'Category 5
    Call callRange(11, False, False, False)
    
    'Category 6
    Call callRange(12, False, False, False)
    
    
    Application.Calculate
        
End Sub

Function myFact(inVal As Double) As Double
  If inVal <= 1 Then
    myFact = 1
  Else
    myFact = inVal * myFact(inVal - 1)
  End If
End Function

Function handlerange(startRow, endRow, category, categoryRow, numStudents, customMean)

    Dim aCats, categoryCol2, startValue, a1, catCol2
    Dim aB, aA
    
    aCats = Split(category, "|")
    category = aCats(0)
    categoryCol2 = aCats(1)
    
    If customMean < 3 Then
        customMean = 3
    End If
  
    startValue = objCreditEngine.Range(categoryCol2 & startRow).Value
 
    a1 = objCreditEngine.Range(categoryCol2 & startRow & ":" & categoryCol2 & endRow).Value
    Dim z, y, x As Integer
    Dim aAB() As Double
    Dim aAA() As Double
    Dim aAFinal() As Double
    ReDim aAB(1 To UBound(a1)) As Double
    ReDim aAA(1 To UBound(a1)) As Double
    ReDim aAFinal(1 To UBound(a1)) As Double
    Dim a1Total As Double
    z = 1
    y = 1
    x = 1
    
    For Each catCol2 In a1
       aAB(z) = ((0.5 ^ ((customMean / 2) - 1)) / myFact((customMean / 2) - 1)) * (catCol2 ^ ((customMean / 2) - 1)) * Exp(-catCol2 / 2)
       z = z + 1
    Next catCol2
    
    For Each aB In aAB
      a1Total = a1Total + aB 'get sum
    Next aB
    
    For Each aB In aAB
      aAA(y) = aB / a1Total
      y = y + 1
    Next aB
    
    For Each aA In aAA
       aAFinal(x) = aA * numStudents
       x = x + 1
    Next aA

    objCreditEngine.Range(category & startRow & ":" & category & endRow).Value = WorksheetFunction.transpose(aAFinal)
    
    objCreditEngine.Calculate

End Function

Sub callRange(categoryRow, numStudents, categoryCol, customMean)

    Dim startRow, endRow
    
    objCreditEngine.Activate
    
    startRow = objCreditEngine.Range("H" & categoryRow).Value
    endRow = objCreditEngine.Range("I" & categoryRow).Value
        
    If numStudents = False Then
        numStudents = objCreditEngine.Range("C" & categoryRow).Value
    End If
    
    If categoryCol = False Then
        categoryCol = objCreditEngine.Range("J" & categoryRow).Value
    End If
    
    If customMean = False Then
        customMean = objCreditEngine.Range("D" & categoryRow).Value
    End If

    Call handlerange(startRow, endRow, categoryCol, categoryRow, numStudents, customMean)

End Sub


