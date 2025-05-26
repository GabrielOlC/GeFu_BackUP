# File objective

> on documentation

### Observations

* [x] Query snippets have been left out. Check the files directly.

* [x] Some Excel functions have been left out. Check the files directly.

* [x] Some VBA worksheet triggers have been left out. Check the files directly

* [x] Some VBA Sub or Functions have been left out. Check the file directly

## Update notes



---

# ⚙️VBA

## Buttons

```visual-basic
Sub vbaSortingError_Type4()
'
' This button will remove all filters on the table, then sort it the right way and copy the SortErrors_Type4 to SortErrors_Type4 as string and set all the ID with error as ID with errors so we can sort all the IDS
'

'
Dim tbl As ListObject
Dim sortColumn(1 To 3) As Range

Application.ScreenUpdating = False
Application.Calculation = xlCalculationManual
Application.EnableEvents = False

On Error GoTo restore

Set tbl = stCheckDataStructure.ListObjects("Check_Data_Structure")
Set sortColumn(1) = tbl.ListColumns("File Block").Range
Set sortColumn(2) = tbl.ListColumns("Governor ID").Range
        
    'sorting table so equation will work
    tbl.AutoFilter.ShowAllData
    
    With tbl.Sort
        .SortFields.Clear
        .SortFields.Add Key:=sortColumn(1), SortOn:=xlSortOnValues, Order:=xlAscending
        .Apply
        .SortFields.Clear
        .SortFields.Add Key:=sortColumn(2), SortOn:=xlSortOnValues, Order:=xlAscending
        .Apply
    End With
    
    'copying values from column with equation to
    Application.Calculate
    stCheckDataStructure.Range("Check_Data_Structure[SortErrors_Type4]").Copy
    stCheckDataStructure.Range("Check_Data_Structure[[#Headers],[SortErrors_Type4 As string]]").Offset(1).PasteSpecial xlPasteValues
    Application.CutCopyMode = False
    
    MsgBox "Recalculation complete"
    
    Application.ScreenUpdating = True
    Application.Calculation = xlCalculationAutomatic
    Application.EnableEvents = True
    
Exit Sub
'---------------------
restore:

MsgBox "An unexpected error has happened, and the operation was cancelled", vbCritical, "Error"
Application.ScreenUpdating = True
Application.Calculation = xlCalculationAutomatic
Application.EnableEvents = True
End Sub

Sub ClearAllFiltersatCheckDataStructure()
'
' This button will clear all filters from table stCheckDataStructure
'

'
   
Dim qt As ListObject
Set qt = stCheckDataStructure.ListObjects("Check_Data_Structure")
    
    qt.AutoFilter.ShowAllData
        
    
End Sub

Sub Sortinging_quickly()
'
' This code will sort the table to the format below aka "sort active status"
'

'
    ActiveSheet.ListObjects("Check_Data_Structure").Range.AutoFilter Field:=1, _
        Criteria1:=Array("Active", "Active - Flag and data teams", "Active - Rally/Garrison Leaders", "Alt", "Alt - Shaw improve all", "Farm Top 300"), _
        Operator:=xlFilterValues
End Sub

Sub ClearAllFiltersAtCheckSourceData()
'
' This will clean the filters at Check Source Data
'

'
    Dim qt As ListObject
    Set qt = stCheckSourceData.ListObjects("Source_Treated")
            
        qt.AutoFilter.ShowAllData
                       
End Sub
Sub TurningValuesTOtext()
'
' This will get the ids on the 'Summed Data' and repast them as text... to fix, incase excel CRAZY think it is numberrrr againnnnnnnnnnn -> note for my future self, never use id as number on excel, especially if you need share it, and can't set all excels to not change number to scientific
'

'

Application.ScreenUpdating = False
Application.Calculation = xlCalculationManual

    Dim vCellValue As String
    
    ' Loop through each cell in the ID column of the table
    For Each cell In Union(tbSummedData.Range("tbDash[ID]"), tbSummedData.Range("tbDash[Main acc ID]"))
        vCellValue = CStr(cell.Value)
        
        cell.Value = vCellValue
    Next

Application.ScreenUpdating = True
Application.Calculation = xlCalculationAutomatic

    MsgBox "IDs updated"
End Sub

Sub CopyUniquePlayerIDsToClipboard()
'
' this extracts unique values as an array from the filtered data on the set table and copy to the clipboard.
'

'

    Dim ws As Worksheet
    Dim tb As ListObject
    Dim dict As Object
    Dim cell As Range, rngName As Range, rngID As Range
    Dim data As String
    
    ' Initialize the dictionary object
    Set dict = CreateObject("Scripting.Dictionary")
    
    ' Set the worksheet and table by its name
    Set ws = stCheckDataStructure
    Set tb = ws.ListObjects("Check_Data_Structure")
    
    ' Define ranges for "Governor ID" and "Governor Name" columns, only considering visible cells (filtered) and run through them
    Set rngID = tb.ListColumns("Governor ID").DataBodyRange.SpecialCells(xlCellTypeVisible)
    Set rngName = tb.ListColumns("Governor Name").DataBodyRange.SpecialCells(xlCellTypeVisible)
    
    For Each cell In rngID
        If Not dict.Exists(cell.Value) And cell.Value <> "" Then
            dict.Add cell.Value, rngName.Cells(cell.Row - rngName.Cells(1).Row + 1).Value
            
        End If
    Next cell
    
    ' Building a string to copy to clipboard
    For Each Key In dict.Keys
        data = data & dict(Key) & vbTab & Key & vbCrLf ' Name and ID separated by a tab, each pair in new line. You may like to change tab to ' - ' if you're not planning to past at another excel or something
        
    Next Key
    
    ' Copy the data to clipboard
    With New DataObject
        .SetText data
        .PutInClipboard
        
    End With
    
    ' Confirmation message
    MsgBox "Unique ID's have been copied to the clipboard"
    
End Sub
```



## Crossmodule

```visual-basic
Function CopyToClipboard(ByVal bvValues As String)
'
' This code will copy the sent value to the clipboard
'

'

Dim ClipboardData As New MSForms.DataObject

    With ClipboardData
        .SetText bvValues
        .PutInClipboard
    End With

End Function

```



## In sheet events

### stCheckDataStructure

```visual-basic
Private Sub Worksheet_BeforeDoubleClick(ByVal Target As Range, Cancel As Boolean)
'
' This code will filter the table to the ID I double clicked
'

'
    If Not Intersect(Target, Me.Range("Check_Data_Structure[Governor ID]")) Is Nothing Then
    
    Dim qt As ListObject
    Set qt = Me.ListObjects("Check_Data_Structure")
    
        qt.AutoFilter.ShowAllData
        qt.Range.AutoFilter Field:=qt.ListColumns("Governor ID").Index, Criteria1:=Target.Value
        
        CopyToClipboard (Target.Value)
        
        Cancel = True
    End If
'
' This code will filter the table to the ID I double click for error type 6
'

'
    If Not Intersect(Target, Me.Range("Check_Data_Structure[SortErrors_Type6]")) Is Nothing And Target.Value <> "Clean" Then
    
    Dim qt1 As ListObject
    Set qt1 = Me.ListObjects("Check_Data_Structure")
    
    
        qt1.AutoFilter.ShowAllData
        qt1.Range.AutoFilter Field:=qt1.ListColumns("Governor ID").Index, Criteria1:=Array(CStr(Target.Value), CStr(Me.Cells(Target.Row, qt1.ListColumns("Governor ID").Index).Value)), Operator:=xlFilterValues
        CopyToClipboard (Me.Cells(Target.Row, qt1.ListColumns("Governor ID").Index).Value)
        
        Cancel = True
    End If
    
End Sub

```



