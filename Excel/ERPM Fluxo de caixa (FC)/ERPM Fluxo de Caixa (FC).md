# File objective

> This application is designed to serve as a cash flow management tool with a 12-month forecast. It features control columns, customizable and automatic adjustments for past, current, or future projections and provisions. Additionally, it includes control tables for statement files and enables the extraction in formats such as XLS, CSV, and PDF.

### Observations

- [x] Query snippets have been left out. Check the files directly.

- [x] Some Excel functions have been left out. Check the files directly.

- [x] Some VBA worksheet triggers have been left out. Check the files directly

- [x] Some VBA Sub or Functions have been left out. Check the file directly

## Update notes

- [ ] Configurar as células numéricas para aceitar apenas números

- [ ] Criar um painel (forms) para selecionar rapidamente o modelo de análise  

- [ ] Criar uma rotina para atualizar todas as fórmulas de correção e ajuste da previsão, provisão e realizado

- [ ] Criar uma rotina para zerar todos os valores e formatos variáveis da planilha (não os tópicos, manter manual ou colocar opção de apagar ou n)

- [ ] Adicionar modulo de previsão com charts

---

![](https://github.com/GabrielOlC/GeFu_BackUP/blob/main/.Images/Picture7.jpg?raw=true)

---

# ⚙️VBA

## Buttons

```visual-basic

Sub TurnCorrectionONOFF()
'
' This sub will active the correction or disable it if it is active. It will also change the button name on the cash flow table
'
' OBS: Do not lock the sheet... as we will have copies the name will change including the VBA name! As it is a button, the active sheet will be the one.

'
    'Changing the Cell Setup and button Value
    If Range("B12").Value Then
        Range("B12").Value = "FALSE"
        ActiveSheet.Shapes.Range(Array("ObjTurnCorrectionONOFF")).TextFrame.Characters.Text = "Ativar Alinhamento"

    Else
        Range("B12").Value = "TRUE"
        ActiveSheet.Shapes.Range(Array("ObjTurnCorrectionONOFF")).TextFrame.Characters.Text = "Desativar Alinhamento"

    End If

End Sub

```

## CrossModules

```visual-basic
'General obs:
    ' The manual table is the "Fluxo de caixa anual", note that the total of totals aren't part of the manual table

Public Function FindingOutRanges() As Range
'
' This function will set into a range all the lines that are titles for the manual table
'
' To Add more titles, you need to add a new Address for each one with the same structure and then add it to the Function setting

'
Dim Address(1 To 5) As Range
    Set Address(1) = Nothing
    Set Address(2) = Nothing
    Set Address(3) = Nothing
    Set Address(4) = Nothing
    Set Address(5) = Nothing

    Set Address(1) = Range("E:E").Find("Entradas", LookIn:=xlValues)

    Set Address(2) = Range("E:E").Find(" TOTAL DE ENTRADAS", LookIn:=xlValues)
    Set Address(2) = Address(2).Resize(4)

    Set Address(3) = Range("E:E").Find("Total: Variáveis", LookIn:=xlValues)
    Set Address(3) = Address(3).Resize(3)

    Set Address(4) = Range("E:E").Find("Total: Fixas", LookIn:=xlValues)
    Set Address(4) = Address(4).Resize(3)

    Set Address(5) = Range("E:E").Find("Total: Sociedades e Benefícios", LookIn:=xlValues)
    Set Address(5) = Address(5).Resize(3)

    Set FindingOutRanges = Union(Address(1).EntireRow, Address(2).EntireRow, Address(3).EntireRow, Address(4).EntireRow, Address(5).EntireRow)

End Function

Public Function FindingOutTable() As Range
'
' This function will tell the range for the data in the manual table
'
' if you don't change the last title ("impostos"), nothing has to be changed

'

Dim Address(1 To 2) As Range

    Set Address(1) = Range("E:E").Find("Entradas", LookIn:=xlValues)

    Set Address(2) = Range("E:E").Find("TOTAL: Impostos", LookIn:=xlValues)
    Set Address(1) = Address(1).Resize(Address(2).Row - Address(1).Row)

    Set FindingOutTable = Address(1).EntireRow

End Function

Public Function FindingOut_Realizados() As Range
'
'This function will tell where the columns “Realizado” are in the table and return it into a unique range
'

'

'in For Dims
Dim Address(1 To 12) As Range, FinalRange As Range, MaximumRange As Range, FindingTitle As Range
Dim FirstFind As String

'Defining the table current range
    For Each Title In Range("F11:XFD11")
        If Title.Value = "" And Title.Offset(, 1).Value = "" Then

            Exit For

        End If
    Next Title

'Setting the Finding range
    Set MaximumRange = Range(Cells(11, 6), Cells(11, Title.Column - 1))

    Set FindingTitle = MaximumRange.Find("Realizado", LookIn:=xlValues)

    If Not FindingTitle Is Nothing Then
        FirstFind = FindingTitle.Address

'In do dims
Dim i As Integer
i = 0
        Do
            i = i + 1 'runs up to 12

            Set Address(i) = FindingTitle.EntireColumn

            If FinalRange Is Nothing Then
                Set FinalRange = Address(i)

            Else
                Set FinalRange = Union(FinalRange, Address(i))

            End If

            Set FindingTitle = MaximumRange.FindNext(FindingTitle)

        Loop While FirstFind <> FindingTitle.Address

    End If

    Set FindingOut_Realizados = FinalRange
End Function


```

## Worksheet Functions

```visual-basic

Sub SetAsChecked(RelocatedTarget As Range)
'
' This will get the target from a trigger and change its layout for an X in the cell desing, or take the X out in case it is already there (with a check yes/no)
'

'
    If Not RelocatedTarget.Borders(xlDiagonalDown).LineStyle = xlNone Then
        If MsgBox("Confirme para remover a confirmação de pagamento do item", vbYesNo, "Remover Confirmação?") = vbYes Then
            RelocatedTarget.Borders(xlDiagonalDown).LineStyle = xlNone
            RelocatedTarget.Borders(xlDiagonalUp).LineStyle = xlNone

        End If
    Else
        With RelocatedTarget.Borders(xlDiagonalDown)
            .LineStyle = xlContinuous
            .Color = -11489280
            .TintAndShade = 0
            .Weight = xlThin
        End With
        With RelocatedTarget.Borders(xlDiagonalUp)
            .LineStyle = xlContinuous
            .Color = -11489280
            .TintAndShade = 0
            .Weight = xlThin
        End With

    End If

End Sub


```

## In sheet Events

### stCashFlow

```visual-basic
Private Sub Worksheet_BeforeDoubleClick(ByVal Target As Range, Cancel As Boolean)

'
' This will check if the click cell was in the column "Realizado", out of the titles and in the manual table. _
    This will also check if the target is not empty
'

'

    If Not Intersect(Target, FindingOut_Realizados) Is Nothing And _
        Intersect(Target, FindingOutRanges) Is Nothing And _
        Not Intersect(Target, FindingOutTable) Is Nothing And _
        Target.Value <> "" Then

        SetAsChecked RelocatedTarget:=Target.Offset(, 3)

    End If

    Cancel = True

End Sub


```

# 🧮Excel functions

## Fluxo de caixa anual

```excel-formula
=IF(
    AND(
        J14<>"",
        OR(
            AND(SysConf!$F$16, MONTH(TODAY())<>H$12),
            AND(SysConf!$F$16, MONTH(TODAY())=H$12, SysConf!$F$26)
        ),
        OR(
            AND(H$12<MONTH(TODAY())-SysConf!$I$16, SysConf!$F$20),
            AND(H$12=MONTH(TODAY()), SysConf!$F$22),
            AND(H$12>MONTH(TODAY())+SysConf!$I$18, SysConf!$F$24)
        )
    ),
    SUM(F14:G14)-J14,
    0
)
```
