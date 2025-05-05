# File objective

> This summarizes all reports available on Shopee, providing insights into any Sold IDs that haven't been properly paid for any reason, specialy if "antecipa" is on. It also manages the Dispute IDs and indicates whether they have been resolved or not.

### Observations

* [x] Query snippets have been left out. Check the files directly.

* [x] Excel functions have been left out. Check the files directly.

* [x] VBA worksheet triggers have been left out. Check the files directly

## Update notes

* [ ] Integrate it with FE to calculate the value loss of 'null' and if the product was or not returned to the store intact (tho it usually never come back)

---

# ⚙️VBA

## App

```visual-basic
Sub manuallunch()
    If MsgBox("Antes de continuar:" & Chr(10) & _
        "1. Adicione as novas movimentações e verifique se existe algum erro de estrutura em qualquer um dos 4 indicadores" & Chr(10) & _
        "2. Atualize as os arquivos nas fontes (relatório de ordem, relatório antecipa, relatório de disputa" & Chr(10) & _
        "3. Atualize os bancos de dados nesta planilha com o botão ""atualizar tudo """ & Chr(10) & _
        "4. OPICINAL - feche outros programas para melhor desepenho e não troque de janela durante a operação" & Chr(10) & Chr(10) & _
        "INFORMAÇÃO: Para cancelar a operação pressione esc (dependendo do lag, pressione sem parar)" & Chr(10) & Chr(10) & _
        ">> Esta operação pode demorar um tempo, deseja continuar?", vbYesNo, "Iniciar verificação de pagamentos para novos itens") = vbYes _
        Then

        If Range("F12").Value + Range("G12").Value + Range("H12").Value + Range("I12").Value <> 0 Then

            MsgBox "Existem erros dentro da planilha que precisam ser concertados para a execução do programa!" & Chr(10) & Chr(10) & _
                "Verifique os indicadores presentes na planilha e as linhas respectivas com erro.", vbCritical, "Operação cancelada"
        Else

        ERROFinder Paid:=True

        End If
    End If

End Sub
Sub ERROFinder(Optional ByVal Paid As Boolean)
'Delete this section after testes
Dim tTimer as Double, tStop As Double
    tTimer = Timer
'
' This program will get a trigger from a button module and run a checkup. This way will be easy control the inputs and outputs for each report type
'

'

If Paid Then
'
' This will check if each ID has been paid.
'   If it was paid it will set "PagoVBA" column as "Y", if only has the anticipation as "Ya", and if not paid at all "N"
'

'
Application.ScreenUpdating = False
Application.Calculation = xlCalculationManual
Application.EnableEvents = False

'Checking structures
    CheckGeneralStructure rcsRG:=True

    If rcsRGStructure(1) Then

'Getting the column address
    UpdatingColumnNumber rcsRG:=True, roOR:=True, raQFR:=True

'Getting the data into the Local Database
    GetTablesToRecordset bvQrAntecipaReport:=True, bvQrOrdemReport:=True

'Inloops dim
Dim FindingIDatRG As Range, FindingIDatOR As Range, FindingIDatQFR As Range
Dim FoundAddress(1 To 2) As String
Dim ExpectedReturn As Double, RGSumReturn As Double, QFRSumReturn As Double

'System counters
Dim IDWasFound(1 To 3) As Boolean, ClaimError_naRA(1) As Boolean
Dim IDWasFoundTwice(1) As Integer

'StatusBar Counters
Dim AllCellsCount as Long, IDRuns As Long
    AllCellsCount = WalletReportShopee.Range("TbRCSRelatorioGeral[Código]").Count
Dim NotFoundCount(1 To 2) As Integer, scNPaid(1 To 2), scNull(1 To 2) As Integer

        For Each ID In WalletReportShopee.Range("TbRCSRelatorioGeral[Código]")
        'For Each ID In Range("=H758,H791,H812,H830,H862,H899,H949,H971,H999") trying out erros
        IDRuns = IDRuns + 1 'Status bar counter

'OBS
'Let rcsRGColumnNumber(1)).Value = "" to check ever no error, set it as "y" to check the current erros that have been checked
'Let rcsRGColumnNumber(4)).Value <> "FPaid" to not check those that have been settled as FPaid, set it = to check them again but add a data sentece to check about the last 4 month only
            'this setting only check new ids, change it carefully and back up, it will write over.
            If Len(ID) = 14 And Mid(ID.Value, 1, 1) = 2 And Cells(ID.Row, rcsRGColumnNumber(4)).Value = "" Then
                'Cells(ID.Row, rcsRGColumnNumber(4)).Value = "" Then

            ' Check if the ID is as expected:
                ' Check if there's any value that was discounted on RG (IF yes, set ErrorVBA as Y and description as the STR)

Set FindingIDatRG = WalletReportShopee.Range("TbRCSRelatorioGeral[Código]").Find(ID.Value, LookIn:=xlValues, MatchCase:=False)

                If Not FindingIDatRG Is Nothing Then
                    FoundAddress(1) = FindingIDatRG.Address
                    RGSumReturn = 0
                    IDWasFound(1) = True

                    Do
                    IDWasFoundTwice(1) = IDWasFoundTwice(1) + 1

                        RGSumReturn = RGSumReturn + WalletReportShopee.Cells(FindingIDatRG.Row, rcsRGColumnNumber(3)).Value

                        If Cells(FindingIDatRG.Row, rcsRGColumnNumber(3)).Value < 0 Then 'Column "pagamento"

                            SetErrorAndDescription IDAddress:=FindingIDatRG, ErrorVBA:="Y", Description:="STR"

                        End If

                        Set FindingIDatRG = WalletReportShopee.Range("TbRCSRelatorioGeral[Código]").FindNext(FindingIDatRG)

                    Loop While FoundAddress(1) <> FindingIDatRG.Address

                End If


            ' Find the ID on OrderReport and save the expected full pay value
                ' if ID not found set ErrorVBA as "Y" and descrition as Descrition & "N/A - RO" (if is not set already)


                QrOrdemReport.Filter = "[ID do pedido] = " & ID.Value & ""

                If QrOrdemReport.RecordCount > 0 Then
                    ExpectedReturn = QrOrdemReport.Fields("Valor a receber Real").Value 'column "Valor a receber Real"
                    IDWasFound(2) = True

                Else
                    SetErrorAndDescription IDAddress:=ID, ErrorVBA:="Y", Description:="n/aRO"

                    NotFoundCount(1) = NotFoundCount(1) + 1

                End If


            ' Find the ID on QuickFoundReport and save the paid value and sum with RG paid value
                ' if ID not found set ErrorVBA as "Y" and description as Description & "N/A - RA" (if is not set already)

                QrAntecipaReport.Filter = "[ID do pedido] = " & ID.Value& & ""

                If QrAntecipaReport.RecordCount > 0 Then
                    QFRSumReturn = 0
                    IDWasFound(3) = True

                    QrAntecipaReport.MoveFirst

                    While Not QrAntecipaReport.EOF

                        QFRSumReturn = QFRSumReturn + QrAntecipaReport.Fields("Valor antecipado").Value

                        QrAntecipaReport.MoveNext

                    Wend

                Else
                    ClaimError_naRA(1) = True

                End If


'---------

                If IDWasFound(1) And IDWasFound(2) And IDWasFound(3) Then
                    Select Case ExpectedReturn

                        Case Is = 0
                            FoundAddress(1) = FindingIDatRG.Address
                            scNull(1) = scNull(1) + 1

                            If Mid(WalletReportShopee.Cells(FindingIDatRG.Row, rcsRGColumnNumber(1)).Value, 1, 1) <> "Y" Or _
                                WalletReportShopee.Cells(FindingIDatRG.Row, rcsRGColumnNumber(7)).Value <> "" _
                                Then 'Counter for Only new itens

                                scNull(2) = scNull(2) + 1
                            End If

                            If IDWasFoundTwice(1) > 1 Then
                                Do
                                    SetSpecificStatusNull bvIDRow:=FindingIDatRG.Row

                                    Set FindingIDatRG = WalletReportShopee.Range("TbRCSRelatorioGeral[Código]").FindNext(FindingIDatRG)

                                Loop While FoundAddress(1) <> FindingIDatRG.Address

                            Else
                                SetSpecificStatusNull bvIDRow:=ID.Row

                            End If


                        Case Is <= RGSumReturn + QFRSumReturn + 0.1 '- 0.1 to match cases where there are cents less then expected, remove for 100% precision
                            FoundAddress(1) = FindingIDatRG.Address

                            If IDWasFoundTwice(1) > 1 Then
                                Do
                                    SetSpecificStatusFpaid bvIDRow:=FindingIDatRG.Row, bvIDAddress:=FindingIDatRG

                                    Set FindingIDatRG = WalletReportShopee.Range("TbRCSRelatorioGeral[Código]").FindNext(FindingIDatRG)

                                Loop While FoundAddress(1) <> FindingIDatRG.Address

                            Else
                                SetSpecificStatusFpaid bvIDRow:=ID.Row, bvIDAddress:=ID

                            End If

                        Case Is > RGSumReturn + QFRSumReturn + 0.1
                            FoundAddress(1) = FindingIDatRG.Address
                            scNPaid(1) = scNPaid(1) + 1

                            If Mid(WalletReportShopee.Cells(FindingIDatRG.Row, rcsRGColumnNumber(1)).Value, 1, 1) <> "Y" Or _
                                WalletReportShopee.Cells(FindingIDatRG.Row, rcsRGColumnNumber(7)).Value <> "" _
                                Then 'Counter for Only new itens

                                scNPaid(2) = scNPaid(2) + 1
                            End If

                            If IDWasFoundTwice(1) > 1 Then
                                Do

                                    SetSpecificStatusNpaid bvIDRow:=FindingIDatRG.Row

                                    Set FindingIDatRG = WalletReportShopee.Range("TbRCSRelatorioGeral[Código]").FindNext(FindingIDatRG)

                                Loop While FoundAddress(1) <> FindingIDatRG.Address

                            Else
                                SetSpecificStatusNpaid bvIDRow:=ID.Row

                            End If

                        Case Else
                            FoundAddress(1) = FindingIDatRG.Address

                            If IDWasFoundTwice(1) > 1 Then
                                Do
                                    WalletReportShopee.Cells(FindingIDatRG.Row, rcsRGColumnNumber(4)).Value = "Else"

                                    Set FindingIDatRG = WalletReportShopee.Range("TbRCSRelatorioGeral[Código]").FindNext(FindingIDatRG)

                                Loop While FoundAddress(1) <> FindingIDatRG.Address
                            Else
                                WalletReportShopee.Cells(ID.Row, rcsRGColumnNumber(4)).Value = "Else"

                            End If

                    End Select

'--------
                ElseIf IDWasFound(1) And IDWasFound(2) Then 'If there is no 'antecipa' for the code
' There is no 'Npaid' here because it is not possible to know if there is a data missing in the 'antecipa' or if we should use the current values to check if they have been paid
' To still make sure we check the values, the 'else' argument tells there is an error and its description is 'n/aRA'

                    Select Case ExpectedReturn
                        Case Is = 0
                            FoundAddress(1) = FindingIDatRG.Address
                            scNull(1) = scNull(1) + 1

                            If Mid(WalletReportShopee.Cells(FindingIDatRG.Row, rcsRGColumnNumber(1)).Value, 1, 1) <> "Y" Or _
                                WalletReportShopee.Cells(FindingIDatRG.Row, rcsRGColumnNumber(7)).Value <> "" _
                                Then 'Counter for Only new itens

                                scNull(2) = scNull(2) + 1
                            End If

                            If IDWasFoundTwice(1) > 1 Then
                                Do
                                    SetSpecificStatusNull bvIDRow:=FindingIDatRG.Row

                                    Set FindingIDatRG = WalletReportShopee.Range("TbRCSRelatorioGeral[Código]").FindNext(FindingIDatRG)

                                Loop While FoundAddress(1) <> FindingIDatRG.Address
                            Else
                                SetSpecificStatusNull bvIDRow:=ID.Row

                            End If

                        Case Is <= RGSumReturn + 0.1 '+ 0.1 to match cases where there are cents less then expected, remove for 100% precision
                            FoundAddress(1) = FindingIDatRG.Address

                            If IDWasFoundTwice(1) > 1 Then
                                Do
                                    SetSpecificStatusFpaid bvIDRow:=FindingIDatRG.Row, bvIDAddress:=FindingIDatRG

                                    Set FindingIDatRG = WalletReportShopee.Range("TbRCSRelatorioGeral[Código]").FindNext(FindingIDatRG)

                                Loop While FoundAddress(1) <> FindingIDatRG.Address

                            Else
                                SetSpecificStatusFpaid bvIDRow:=ID.Row, bvIDAddress:=ID

                            End If
                        Case Is > RGSumReturn + 0.1
                          FoundAddress(1) = FindingIDatRG.Address
                          scNPaid(1) = scNPaid(1) + 1

                         If Mid(WalletReportShopee.Cells(FindingIDatRG.Row, rcsRGColumnNumber(1)).Value, 1, 1) <> "Y" Or _
                                WalletReportShopee.Cells(FindingIDatRG.Row, rcsRGColumnNumber(7)).Value <> "" _
                                Then 'Counter for Only new itens

                                scNPaid(2) = scNPaid(2) + 1
                            End If

                          If IDWasFoundTwice(1) > 1 Then

                              Do

                                  SetSpecificStatusNpaid bvIDRow:=FindingIDatRG.Row

                                  Set FindingIDatRG = WalletReportShopee.Range("TbRCSRelatorioGeral[Código]").FindNext(FindingIDatRG)

                              Loop While FoundAddress(1) <> FindingIDatRG.Address

                          Else
                              SetSpecificStatusNpaid bvIDRow:=ID.Row

                          End If

                        Case Else
                            If ClaimError_naRA(1) Then
                                SetErrorAndDescription IDAddress:=ID, ErrorVBA:="Y", Description:="n/aRA"

                                NotFoundCount(2) = NotFoundCount(2) + 1

                            End If
                    End Select

                End If

            End If

‘Resetting Systems
        IDWasFound(1) = False
        IDWasFound(2) = False
        IDWasFound(3) = False
        IDWasFoundTwice(1) = 0
        ClaimError_naRA(1) = False

'Status bar updating
Application.StatusBar = "ID's proccessados: " & IDRuns & "/" & AllCellsCount & " | ID's não encontrados no OR/QFR: " & NotFoundCount(1) & "/" & NotFoundCount(2) _
    & " | ID's Não pagos / Nulos: " & scNPaid(1) & "/" & scNull(1)

        Next

        MsgBox "A verificação dos dados foi concluída. Relatório: " & Chr(10) & Chr(10) & _
            "ID's processados: " & IDRuns & Chr(10) & Chr(10) & _
            "ID's não encontrados no ""relatório de Ordem"" " & NotFoundCount(1) & Chr(10) & Chr(10) & _
            "ID's não encontrados no ""relatório Antecipa"" " & NotFoundCount(2) & Chr(10) & Chr(10) & _
            "Total de itens não pagos: " & scNPaid(2) & " (" & scNPaid(1) & ")" & Chr(10) & Chr(10) & _
            "Total de itens nulos: " & scNull(2) & " (" & scNull(1) & ")", Title:="Relatório do scaner"

    Else
        MsgBox "Alguns dados não estão no formato correto" & Chr(10) & Chr(10) & "Corrija o formato para continuar", vbCritical, "Existem erros na base de dados"
    End If


Application.Calculation = xlCalculationAutomatic
Application.ScreenUpdating = True
Application.EnableEvents = True

End If

Application.StatusBar = ""
End Sub

Sub PortrayID(ID As String, Optional ByVal Sign As String, Optional ByVal Details As String, Optional ByVal ProtocolNumber As String, Optional ByVal bvNotMsgBox As Boolean)
'
' This code will find all lines with a code, and set "retratado" as "Y"
'

'
Dim FindingID As Range
Dim FirstId As String
Dim Counter(1) As Integer

    With WalletReportShopee

Set FindingID = Range("TbRCSRelatorioGeral[Código]").Find(ID, LookIn:=xlValues, MatchCase:=False)

        If Not FindingID Is Nothing Then
            FirstId = FindingID.Address

            Do
                If Sign <> "" Then

                    .Cells(FindingID.Row, Range("TbRCSRelatorioGeral[Retratado?]").Column).Value = Sign

                    If Sign = "Y" Or Sign = "P" Then
                        .Cells(FindingID.Row, Range("TbRCSRelatorioGeral[ErroVBA]").Column).Value = ""
                    End If

                End If

                If Details <> "" Then
                    If .Cells(FindingID.Row, Range("TbRCSRelatorioGeral[Observação]").Column).Value <> "" Then
                        .Cells(FindingID.Row, Range("TbRCSRelatorioGeral[Observação]").Column).Value = _
                            .Cells(FindingID.Row, Range("TbRCSRelatorioGeral[Observação]").Column).Value & "; " & Chr(10) & Details

                    Else
                        .Cells(FindingID.Row, Range("TbRCSRelatorioGeral[Observação]").Column).Value = Details

                    End If

                End If

                If ProtocolNumber <> "" Then
                    .Cells(FindingID.Row, Range("TbRCSRelatorioGeral[N° Protocolo]").Column).Value = ProtocolNumber

                End If


            Counter(1) = Counter(1) + 1
            Set FindingID = .Range("TbRCSRelatorioGeral[Código]").FindNext(FindingID)

            Loop While FirstId <> FindingID.Address

            If Not bvNotMsgBox Then
                MsgBox Counter(1) & " Itens foram atualizados"
            End If

        Else
            If Not bvNotMsgBox Then
                MsgBox "Nenhum item com esse ID foi encontrado"

            End If

        End If

    End With

End Sub

Sub NormalizeStatus()
'
' Some of the ids have been done manually, what means that the same code may not have the status shared along the database. This code will make sure all codes have the status
'

'

'Setting the excel up
    'Performance
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual
    Application.EnableEvents = False

    'Collumn Adresses
    UpdatingColumnNumber rcsRG:=True

'Setting the code up
    'In loop Dim
    Dim FindingIDatRG As Range

    'System cache
    Dim FoundAddress(1) As String 'To save the first address found in the .find
    Dim StatusValue As String
        StatusValue = "Y"
    'FeedBack cache
    Dim IDRanCounter(1 To 2) As Integer
        '1 Count the total of code ran
        '2 Count the total of code that have been fixed

    For Each ErrorStatus In WalletReportShopee.Range("TbRCSRelatorioGeral[Retratado?]")
        If ErrorStatus = StatusValue Then
        IDRanCounter(1) = IDRanCounter(1) + 1

Set FindingIDatRG = WalletReportShopee.Range("TbRCSRelatorioGeral[Código]").Find(Cells(ErrorStatus.Row, rcsRGColumnNumber(5)).Value, LookIn:=xlValues, MatchCase:=False)

            If Not FindingIDatRG Is Nothing Then
                FoundAddress(1) = FindingIDatRG.Address

                Do
                    If WalletReportShopee.Cells(FindingIDatRG.Row, ErrorStatus.Column).Value <> StatusValue Then
                        IDRanCounter(2) = IDRanCounter(2) + 1

                        Debug.Print FindingIDatRG.Value

                        WalletReportShopee.Cells(FindingIDatRG.Row, ErrorStatus.Column).Value = StatusValue 'in here to optimaze as the if is here for the counter already

                    End If

                Set FindingIDatRG = WalletReportShopee.Range("TbRCSRelatorioGeral[Código]").FindNext(FindingIDatRG)

                Loop While FoundAddress(1) <> FindingIDatRG.Address
            End If
        End If

    Next

    MsgBox IDRanCounter(1) & " Itens foram verificados!" & Chr(10) & IDRanCounter(2) & " Total de correções", vbInformation, "Operação finalizada"

'Setting excel back
    Application.Calculation = xlCalculationAutomatic
    Application.ScreenUpdating = True
    Application.EnableEvents = True

End Sub













' PARA BAIXO É RASCUNHO!



Sub ErroEretratadoVBA()
'
' The code shall check each id on the manual financial report and check if it has been paid by shopee and if there's any error at it
'

'
Application.ScreenUpdating = False
UpdatingColumnNumber 'Getting the column number

Dim CounterCRICT(1), Counter(2 To 3), sum As Double 'Marker 1, 2
Dim FindingIDatRCSRG, FindingIDatQYAR As Range
Dim AddressCounter(1 To 2) As String

    'check all ids
    For Each CellID In WalletReportShopee.Range("TbRCSRelatorioGeral[Código]")
        sum = 0 'Reset the value of sum for the next ID
        Counter(2) = 0

        'check if the ID is a code
        If CellID.Value <> "" And Len(CellID.Value) = 14 Then 'Check if the ID is right

    'Find the ID on the RCSRG table
    Set FindingIDatRCSRG = WalletReportShopee.Range("TbRCSRelatorioGeral[Descrição]").Find(CellID.Value, LookIn:=xlValues, MatchCase:=True)
            If Not FindingIDatRCSRG Is Nothing Then
                AddressCounter(1) = FindingIDatRCSRG.Address

                Do
                    sum = sum + Cells(FindingIDatRCSRG.Row, rcsRGColumnNumber(7)).Value

                    Set FindingIDatRCSRG = WalletReportShopee.Range("TbRCSRelatorioGeral[Descrição]").FindNext(FindingIDatRCSRG)

                Loop While AddressCounter(1) <> FindingIDatRCSRG.Address

            Else
'Marker1
                CounterCRICT(1) = CounterCRICT(1) + 1 'ID not found at the general report

                Cells(CellID.Row, rcsRGColumnNumber(4)).Value = "CN/A"

            End If

    Set FindingIDatQYAR = AntecipaReport.Range("QYAntecipaReport[ID]").Find(CellID.Value, LookIn:=xlValues, MatchCase:=True)
            If Not FindingIDatQYAR Is Nothing Then
                AddressCounter(2) = FindingIDatQYAR.Address

                Do
                    sum = sum + Cells(FindingIDatQRAR.Row, Range("QYAntecipaReportReport [ID]").Column).Value

                Loop While AddressCounter(2) <> FindingIDatQYAR.Address

                'Report
                If sum <> Cells(FindingIDatQYAR, Range("QYAntecipaReportReport[Faturamento total2]").Column).Value Then
                    Cells(CellID.Row, rcsRGColumnNumber(4)).Value = "Y"

                    Cells(CellID.Row, rcsRGColumnNumber(8)).Value = "DV: " & sum & " / " & Cells(FindingIDatQYAR, Range("QYAntecipaReportReport[Faturamento total2]").Column).Value

                End If
            Else
'Marker 2
                Counter(2) = Counter(2) + 1 'ID not found at the AntecipaReport report
                Cells(CellID.Row, rcsRGColumnNumber(4)).Value = "N/A"

            End If

        ElseIf CellID.Value <> "Saque" And CellID.Value <> "AntecipaReportção númerica" And CellID.Value <> "Compra com carteira" Then
            CounterCRICT(1) = CounterCRICT(1) + 1 'IDs not right

            Cells(CellID.Row, rcsRGColumnNumber(8)).Value = "IDerro1"

        End If
'Marker 2
        Counter(3) = Counter(3) + 1 'Numb of ID that has been checked
    Next

    MsgBox "Total de códigos verificados: " & Counter(3) & Chr(10) & _
        "Total de códigos não encontrados na planilha AntecipaReport: " & Counter(2) & Chr(10) & Chr(10) & _
        ">> Total de erros não esperados" & Chr(10) & Chr(10) & _
        "Total de códigos não encontrados no relatório geral: " & CounterCRICT(1), Title:="Relatório"


Application.ScreenUpdating = True
End Sub
Sub saveit()
        'Will check if all reported cells are fixed
        If fErro.Value = "Y" And Cells(fErro.Row, rcsRGColumnNumber(2)) = "Y" And Cells(fErro.Row, rcsRGColumnNumber(5)) = "" Then

Dim FindingID As Range
    Set FindingID = WalletReportShopee.Range("TbRCSRelatorioGeral[Descrição]").Find(Cells(fErro.Row, rcsRGColumnNumber(6)).Value, LookIn:=xlValues, MatchCase:=True)

            If Not FindingID Is Nothing Then
                For Each ID In FindingID
                    sum = sum + Cells(ID.Row, rcsRGColumnNumber(7))

                Next

Dim FindingPayValue As Range

            End If

            Counter(1) = Counter(1) + 1 'Elements analyzed
        End If
End Sub

```

## Buttons

```visual-basic
Sub PortrayIDatA1C()
'
' This will active the Portray at RCS using the button at FindOneCode
'

'
Dim ibDetails As String

    If FindOneCode.Range("H2").Value <> "" And MsgBox("Deseja retratar o item?", vbYesNo, "Retratar item") = vbYes Then

        ibDetails = InputBox("", "De alguns detalhes", "Item já pago")
        ClearFilters bvTableName:="TbRCSRelatorioGeral", bvSheetName:=WalletReportShopee.Name

        If ibDetails <> "" Then
            PortrayID ID:=FindOneCode.Range("H2").Value, Sign:="Y", Details:=ibDetails

        Else
            PortrayID ID:=FindOneCode.Range("H2").Value, Sign:="Y"

        End If

        ReorderTable bvType:=1 ' this will restore manually the filters

    Else
        MsgBox "Operação cancelada"

    End If


End Sub

Sub SetIDAsForgivenAtA1C()
'
' This will active the Portray at RCS using the button at FindOneCode
'

'
Dim ibDetails As String

    If FindOneCode.Range("H2").Value <> "" And MsgBox("Deseja perdoar o item?", vbYesNo, "Retratar item") = vbYes Then

        ibDetails = InputBox("", "Qual a razão do perdão?")
        ClearFilters bvTableName:="TbRCSRelatorioGeral", bvSheetName:=WalletReportShopee.Name

        If ibDetails <> "" Then
            PortrayID ID:=FindOneCode.Range("H2").Value, Sign:="P", Details:=ibDetails

        Else
            PortrayID ID:=FindOneCode.Range("H2").Value, Sign:="P"

        End If

        ReorderTable bvType:=1 ' this will restore manually the filters

    Else
        MsgBox "Operação cancelada"

    End If


End Sub

Sub GiveIDDescription()
'
' This will give the respective ID a message (description)
'

'

Dim ibDetails As String

    If FindOneCode.Range("H2").Value <> "" Then
        ibDetails = InputBox("", "Adicionar qual descrição?")

        If ibDetails <> "" Then
            ClearFilters bvTableName:="TbRCSRelatorioGeral", bvSheetName:=WalletReportShopee.Name
            PortrayID ID:=FindOneCode.Range("H2").Value, Details:=ibDetails

        Else
            MsgBox "Operação cancelada: A descrição não pode ser vazia"
        End If

    Else
        MsgBox "Operação cancelada: não há um ID"

    End If


End Sub

Sub SetIndividualProtocolNumberAtA1C()
'
' This will attribute the protocol number to all matches of the ID in the RCS table, the default is '?'. This will be activated with a button at A1C Sheet
'

'
Dim ibProtocolNumb As String

    If FindOneCode.Range("H2").Value <> "" And MsgBox("Adicionar um protocolo ao item?", vbYesNo, "Atribuir protocolo item") = vbYes Then
    ClearFilters bvTableName:="TbRCSRelatorioGeral", bvSheetName:=WalletReportShopee.Name

        ibProtocolNumb = InputBox("", "Qual o número do protocolo?", "?")

        If ibProtocolNumb <> "" Then
            PortrayID ID:=FindOneCode.Range("H2").Value, ProtocolNumber:=ibProtocolNumb

        Else
            MsgBox "O número do protocolo não pode ser vazio!"

            Exit Sub

        End If

    Else
        MsgBox "Operação cancelada"

    End If

End Sub
Sub SetGroupOfProtocolNumberAtA1C()
'
' This code will get all the id's at 'TbProtocolToInsert' and set at the main table
'

'

'Setting the excel up
    'Performance
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual
    Application.EnableEvents = False

    'Collumn Adresses
    UpdatingColumnNumber rcsRG:=True

'Setting the code up
    'in loop dims
        Dim FindingIDatRG As Range

    'System cache
        Dim FoundAddress(1) As String
    'System counter
        Dim Counter(1 To 3) As Integer

    If MsgBox("Deseja atribuir os protocolos abaixo aos respectivos ID's?", vbYesNo) = vbYes Then
    ClearFilters bvTableName:="TbRCSRelatorioGeral", bvSheetName:=WalletReportShopee.Name
            For Each ID In FindOneCode.Range("TbProtocolToInsert[ID]")
                If ID.Value <> "" Then
Set FindingIDatRG = WalletReportShopee.Range("TbRCSRelatorioGeral[Código]").Find(ID.Value, LookIn:=xlValues, MatchCase:=True)

                    If Not FindingIDatRG Is Nothing Then
                        FoundAddress(1) = FindingIDatRG.Address
                        Counter(1) = Counter(1) + 1

                        FindOneCode.Cells(ID.Row, Range("TbProtocolToInsert[Status]").Column).Value = "OK"

                        Do
                            If WalletReportShopee.Cells(FindingIDatRG.Row, rcsRGColumnNumber(8)).Value <> "" And _
                                WalletReportShopee.Cells(FindingIDatRG.Row, rcsRGColumnNumber(8)).Value <> "?" _
                                Then

                                WalletReportShopee.Cells(FindingIDatRG.Row, rcsRGColumnNumber(9)).Value = WalletReportShopee.Cells(FindingIDatRG.Row, rcsRGColumnNumber(8)).Value

                            End If

                            WalletReportShopee.Cells(FindingIDatRG.Row, rcsRGColumnNumber(8)).Value = FindOneCode.Cells(ID.Row, Range("TbProtocolToInsert[Protocolo]").Column).Value

                        Counter(2) = Counter(2) + 1
                        Set FindingIDatRG = WalletReportShopee.Range("TbRCSRelatorioGeral[Código]").FindNext(FindingIDatRG)

                        Loop While FoundAddress(1) <> FindingIDatRG.Address
                    Else
                        Counter(3) = Counter(3) + 1

                        FindOneCode.Cells(ID.Row, Range("TbProtocolToInsert[Status]").Column).Value = "Não encontrado"

                    End If
                Else
                    FindOneCode.Cells(ID.Row, Range("TbProtocolToInsert[Status]").Column).Value = "Vazio"

                End If
            Next

            MsgBox "Foram atualizados um total de " & Counter(1) & " de " & FindOneCode.Range("TbProtocolToInsert[ID]").Count & " IDs com " & Counter(2) & " elementos." & Chr(10) & _
                Counter(3) & " Não foram encontrados"
    Else
        MsgBox "Operação cancelada"

End If

'Setting excel back
    Application.Calculation = xlCalculationAutomatic
    Application.ScreenUpdating = True
    Application.EnableEvents = True

End Sub

Sub GiveGroupIDDescription()
'
' This code will get all the id's at 'TbProtocolToInsert' and give them the respective description
'

'

'Setting the excel up
    'Performance
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual
    Application.EnableEvents = False

    'Collumn Adresses
    UpdatingColumnNumber rcsRG:=True

'Setting the code up
    'System cache
        Dim FoundAddress(1) As String
    'System counter
        Dim Counter(1 To 3) As Integer

    If MsgBox("Deseja atribuir as descrições abaixo aos respectivos ID's?", vbYesNo) = vbYes Then
    ClearFilters bvTableName:="TbRCSRelatorioGeral", bvSheetName:=WalletReportShopee.Name
            For Each ID In FindOneCode.Range("TbProtocolToInsert[ID]")
                If ID.Value <> "" Then
Set FindingIDatRG = WalletReportShopee.Range("TbRCSRelatorioGeral[Código]").Find(ID.Value, LookIn:=xlValues, MatchCase:=True)

                    If Not FindingIDatRG Is Nothing Then
                        FoundAddress(1) = FindingIDatRG.Address
                        Counter(1) = Counter(1) + 1

                        FindOneCode.Cells(ID.Row, Range("TbProtocolToInsert[Status]").Column).Value = "OK"

                        If FindOneCode.Cells(ID.Row, Range("TbProtocolToInsert[Descrição]").Column).Value <> "" Then
                            PortrayID ID:=ID.Value, Details:=FindOneCode.Cells(ID.Row, Range("TbProtocolToInsert[Descrição]").Column).Value, bvNotMsgBox:=True

                        Else
                            FindOneCode.Cells(ID.Row, Range("TbProtocolToInsert[Status]").Column).Value = "Mensagem vazia"

                        End If

                        WalletReportShopee.Cells(FindingIDatRG.Row, rcsRGColumnNumber(8)).Value = FindOneCode.Cells(ID.Row, Range("TbProtocolToInsert[Protocolo]").Column).Value

                    Else
                        Counter(3) = Counter(3) + 1

                        FindOneCode.Cells(ID.Row, Range("TbProtocolToInsert[Status]").Column).Value = "Não encontrado"

                    End If
                Else
                    FindOneCode.Cells(ID.Row, Range("TbProtocolToInsert[Status]").Column).Value = "Vazio"

                End If
            Next
            'o coutner 2 ta errado quando usa o give em grupo :v vou arrumar n
            MsgBox "Foram atualizados um total de " & Counter(1) & " de " & FindOneCode.Range("TbProtocolToInsert[ID]").Count & " IDs com " & Counter(2) & " elementos." & Chr(10) & _
                Counter(3) & " Não foram encontrados"
    Else
        MsgBox "Operação cancelada"

End If

'Setting excel back
    Application.Calculation = xlCalculationAutomatic
    Application.ScreenUpdating = True
    Application.EnableEvents = True

End Sub
Sub SinalizeIDAtA1C()
'
' This code will get the ids and put a signaling number at the signling column
'

'

'Setting the excel up
    'Performance
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual
    Application.EnableEvents = False

    'Collumn Adresses
    UpdatingColumnNumber rcsRG:=True

'Setting the code up
    'in loop dims
        Dim FindingIDatRG As Range

    'System cache
        Dim FoundAddress(1) As String
        Dim CheckInputbox(1) As Variant

    'System counter
        Dim Counter(1 To 3) As Integer

    'maximum value
        Dim maxvalue As Integer

    'Clear or not old value?
        Dim ClearOrNot As VbMsgBoxResult

    If MsgBox("Deseja sinalizar os IDs a abaixo?", vbYesNo) = vbYes Then

        'setting essential things up
        ClearFilters bvTableName:="TbRCSRelatorioGeral", bvSheetName:=WalletReportShopee.Name
        ClearOrNot = MsgBox("Deseja apagar os valores anteriores da sinalização?", vbYesNo + vbDefaultButton2)
        maxvalue = SheetReference.Range("tbMaxValueAtRG[MaxValueAtRG]").Value + 1

        If MsgBox("Deseja definir uma sinalização com valor específico?", vbYesNo + vbDefaultButton2) = vbYes Then
            Do
                CheckInputbox(1) = InputBox("Digite o número da sinalização", Default:=maxvalue)

                If CheckInputbox(1) = "" Then 'operation canceled by user
                    Exit Do

                ElseIf Not IsNumeric(CheckInputbox(1)) Then
                    MsgBox "O valor inserido não é um número"

                Else
                    maxvalue = CheckInputbox(1)
                    Exit Do

                End If
            Loop
        End If

        If CheckInputbox(1) <> "" Then 'updating last value accordingly to highest value
            If maxvalue > CheckInputbox(1) Then
                heetReference.Range("tbMaxValueAtRG[MaxValueAtRG]").Value = maxvalue

            Else
                SheetReference.Range("tbMaxValueAtRG[MaxValueAtRG]").Value = CheckInputbox(1)

            End If
        Else
            SheetReference.Range("tbMaxValueAtRG[MaxValueAtRG]").Value = maxvalue

        End If

        For Each ID In FindOneCode.Range("TbProtocolToInsert[ID]")
            If ID.Value <> "" Then
Set FindingIDatRG = WalletReportShopee.Range("TbRCSRelatorioGeral[Código]").Find(ID.Value, LookIn:=xlValues, MatchCase:=True)

                If Not FindingIDatRG Is Nothing Then
                    FoundAddress(1) = FindingIDatRG.Address
                    Counter(1) = Counter(1) + 1

                    FindOneCode.Cells(ID.Row, Range("TbProtocolToInsert[Status]").Column).Value = "OK"

                    Do
                        If WalletReportShopee.Cells(FindingIDatRG.Row, Range("TbRCSRelatorioGeral[Sinalização]").Column).Value <> "" And ClearOrNot = vbNo Then
                            WalletReportShopee.Cells(FindingIDatRG.Row, Range("TbRCSRelatorioGeral[Sinalização]").Column).Value = _
                                WalletReportShopee.Cells(FindingIDatRG.Row, Range("TbRCSRelatorioGeral[Sinalização]").Column).Value & " | " & maxvalue

                        Else
                            WalletReportShopee.Cells(FindingIDatRG.Row, Range("TbRCSRelatorioGeral[Sinalização]").Column).Value = maxvalue

                        End If

                    Counter(2) = Counter(2) + 1
                    Set FindingIDatRG = WalletReportShopee.Range("TbRCSRelatorioGeral[Código]").FindNext(FindingIDatRG)

                    Loop While FoundAddress(1) <> FindingIDatRG.Address
                Else
                    Counter(3) = Counter(3) + 1

                    FindOneCode.Cells(ID.Row, Range("TbProtocolToInsert[Status]").Column).Value = "Não encontrado"

                End If
            Else
                FindOneCode.Cells(ID.Row, Range("TbProtocolToInsert[Status]").Column).Value = "Vazio"

            End If
        Next

        MsgBox "Foram atualizados um total de " & Counter(1) & " de " & FindOneCode.Range("TbProtocolToInsert[ID]").Count & " IDs com " & Counter(2) & " elementos." & Chr(10) & _
            Counter(3) & " Não foram encontrados" & Chr(10) & Chr(10) & _
            "O número da sinalização é: " & maxvalue

    Else
        MsgBox "Operação cancelada"

    End If

'Setting excel back
    Application.Calculation = xlCalculationAutomatic
    Application.ScreenUpdating = True
    Application.EnableEvents = True

End Sub


Sub ClearGroupOfProtocolNumberAtA1C()
'
' This code will clear the table 'TbProtocolToInsert' at A1C
'

'

' Setting excel up
Application.EnableEvents = False
Application.ScreenUpdating = False

    If MsgBox("Realmente deseja limpar os dados?", vbYesNo, "ESTA OPERAÇÃO NÃO TEM VOLTA!") = vbYes Then
        FindOneCode.Range("TbProtocolToInsert").ClearContents
        FindOneCode.ListObjects("TbProtocolToInsert").Resize Intersect(Range("TbProtocolToInsert[#all]"), Range(Range("TbProtocolToInsert").Row & ":" & Range("TbProtocolToInsert").Row - 1))

    Else
        MsgBox "Operação cancelada"

    End If

'Setting excel back
Application.ScreenUpdating = True
Application.EnableEvents = True

End Sub

```

## CrossModules

```visual-basic
Global rcsRGColumnNumber(1 To 10) As Integer
Global roOrColumnNumber(1) As Integer
Global raQFRColumnNumber(1) As Integer

Global rcsRGStructure(1) As Boolean

Sub UpdatingColumnNumber(Optional ByVal rcsRG As Boolean, Optional ByVal roOR As Boolean, Optional ByVal raQFR As Boolean)
'
' Se the column values as asked by each code - so it doesn't over run for each module
'

'

    If rcsRG Then
        rcsRGColumnNumber(1) = WalletReportShopee.Range("TbRCSRelatorioGeral[ErroVBA]").Column
        rcsRGColumnNumber(2) = WalletReportShopee.Range("TbRCSRelatorioGeral[ObservaçãoVBA]").Column
        rcsRGColumnNumber(3) = WalletReportShopee.Range("TbRCSRelatorioGeral[Pagamento]").Column
        rcsRGColumnNumber(4) = WalletReportShopee.Range("TbRCSRelatorioGeral[PagoVBA]").Column
        rcsRGColumnNumber(5) = WalletReportShopee.Range("TbRCSRelatorioGeral[Código]").Column
        rcsRGColumnNumber(6) = WalletReportShopee.Range("TbRCSRelatorioGeral[RetratadoVBA]").Column
        rcsRGColumnNumber(7) = WalletReportShopee.Range("TbRCSRelatorioGeral[Retratado?]").Column
        rcsRGColumnNumber(8) = WalletReportShopee.Range("TbRCSRelatorioGeral[N° Protocolo]").Column
        rcsRGColumnNumber(9) = WalletReportShopee.Range("TbRCSRelatorioGeral[Último N° Protocolo]").Column
        rcsRGColumnNumber(10) = WalletReportShopee.Range("TbRCSRelatorioGeral[Observação]").Column

    End If

    If roOR Then
        roOrColumnNumber(1) = OrderReport.Range("QrOrdemReport[Valor a receber Real]").Column

    End If

    If raQFR Then
        raQFRColumnNumber(1) = QuickFoundReport.Range("QrAntecipaReport[Valor antecipado]").Column

    End If

End Sub

Sub CheckGeneralStructure(Optional ByVal rcsRG As Boolean)
'
' Check the structure of the choose data
'

'

    If rcsRG Then
        If WorksheetFunction.sum(Range("sTbRCSrg_erros")) = 0 Then
            rcsRGStructure(1) = True

        End If

    End If

End Sub

Sub SetErrorAndDescription(ByVal IDAddress As Range, ByVal ErrorVBA As String, ByVal Description As String)
'
'  This code will set ErrorVBA as byval and Descrition as byval. And do all the checks need. It will also check if the Description is already set for no duplicates
'

'

    If Cells(IDAddress.Row, rcsRGColumnNumber(2)).Value = "" Then
        WalletReportShopee.Cells(IDAddress.Row, rcsRGColumnNumber(1)).Value = ErrorVBA
        WalletReportShopee.Cells(IDAddress.Row, rcsRGColumnNumber(2)).Value = Description


    Else
        On Error Resume Next

Dim DescriptionLocation As Integer
        DescriptionLocation = WorksheetFunction.Find(Description, WalletReportShopee.Cells(IDAddress.Row, rcsRGColumnNumber(2)).Value, 1)

        If Err.number = 1004 Then
            WalletReportShopee.Cells(IDAddress.Row, rcsRGColumnNumber(2)).Value = WalletReportShopee.Cells(IDAddress.Row, rcsRGColumnNumber(2)).Value & "; " & Description

            Err.clear

        ElseIf Err.number = 0 Then 'Code build for future updates, for now, there's no use for this.

        End If

        On Error GoTo 0

    End If
End Sub

Sub CleanSpecificError(ByVal IDAddress As Range, ByVal Description As String, ByVal FullDescription As String)
'
' This code will get the error provide and take it out of the description + set Error as Null IF there is no other error
'

'

    On Error Resume Next

Dim DescriptionLocation(1 To 2) As Integer '1: ; + Description | 2: only Description

    DescriptionLocation(1) = WorksheetFunction.Find("; " & Description, FullDescription, 1)

    If Err.number = 1004 Then 'if description wasn't find in the middle (with ";")
        Err.clear
        DescriptionLocation(1) = 0

        DescriptionLocation(2) = WorksheetFunction.Find(Description, FullDescription, 1)

        If Err.number = 1004 Then 'if description wasn't find alone either
            Err.clear
            DescriptionLocation(2) = 0

        End If

    End If

    On Error GoTo 0

    If DescriptionLocation(1) <> 0 Then
        WalletReportShopee.Cells(IDAddress.Row, rcsRGColumnNumber(2)).Value = _
            Mid(FullDescription, 1, DescriptionLocation(1) - 1) & Mid(FullDescription, DescriptionLocation(1) + Len(Description) + 2, Len(FullDescription))

    ElseIf DescriptionLocation(2) <> 0 Then
        WalletReportShopee.Cells(IDAddress.Row, rcsRGColumnNumber(2)).Value = _
            Mid(FullDescription, Len(Description) + 3, Len(FullDescription))

    End If

    If WalletReportShopee.Cells(IDAddress.Row, rcsRGColumnNumber(2)).Value = "" Then 'ObservaçãoVBA
        WalletReportShopee.Cells(IDAddress.Row, rcsRGColumnNumber(1)).Value = "" 'ErroVBA

    End If

End Sub
Sub SetSpecificStatusNull(ByVal bvIDRow As Integer)
'
' This will set the status in the RG, so we don't need to repeat the code all the time
'

'
    If (WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(4)).Value = "Fpaid" Or WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(4)).Value = "Npaid") And _
        (WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(6)).Value = "Y" Or WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(7)).Value <> "N") _
        Then

            WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(1)).Value = "Y2"
            WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(4)).Value = "Null"

            WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(6)).Value = ""
            WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(7)).Value = "CleanedByVBA: " & WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(7)).Value

        ElseIf (WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(6)).Value = "Y" Or WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(7)).Value <> "N") And _
            WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(4)).Value = "Null" _
            Then

            'Nothing to be done, the ID has been fixed and the error is the same

        Else
            WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(1)).Value = "Y"
            WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(4)).Value = "Null"

    End If
End Sub

Sub SetSpecificStatusNpaid(ByVal bvIDRow As Integer)
'
' This will set the status in the RG, so we don't need to repeat the code all the time
'

'
    If (WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(4)).Value = "Fpaid" Or WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(4)).Value = "Null") And _
        (WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(6)).Value = "Y" Or WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(7)).Value <> "N") _
        Then

            WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(1)).Value = "Y2"
            WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(4)).Value = "Npaid"

            WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(6)).Value = ""
            WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(7)).Value = "CleanedByVBA: " & WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(7)).Value

        ElseIf (WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(6)).Value = "Y" Or WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(7)).Value <> "N") And _
            WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(4)).Value = "Npaid" _
            Then

            'Nothing to be done, the ID has been fixed, and the error is the same

        Else
            WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(1)).Value = "Y"
            WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(4)).Value = "Npaid"

    End If
End Sub
Sub SetSpecificStatusFpaid(ByVal bvIDRow As Integer, ByVal bvIDAddress As Range)
'
' This will set the status in the RG, so we don't need to repeat the code all the time
'

'

    If WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(4)).Value <> "Fpaid" And _
        WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(4)).Value <> "" _
        Then 'This check if the current ID has been Portrayed

        WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(6)).Value = "Y"

    End If

    WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(4)).Value = "Fpaid"

    WalletReportShopee.Cells(bvIDRow, rcsRGColumnNumber(1)).Value = "" 'Cleaning the status of error

    CleanSpecificError IDAddress:=bvIDAddress, Description:="STR", FullDescription:=Cells(bvIDRow, rcsRGColumnNumber(2)).Value 'Cleaning the description of error


End Sub
Sub ClearFilters(ByVal bvTableName As String, ByVal bvSheetName As String)
'
' This will clear filters of some table
'

'


Set tbl = Sheets(bvSheetName).ListObjects(bvTableName)
    'sorting table so equation will work
    tbl.AutoFilter.ShowAllData

    With tbl.Sort
        .SortFields.clear
        .Apply

    End With

End Sub
Sub sdjasjlkdas()
ClearFilters bvTableName:="TbRCSRelatorioGeral", bvSheetName:=WalletReportShopee.Name
End Sub
Sub ReorderTable(ByVal bvType As Integer)
'
' This code will sort the table on 'WalletReportShopee' depending on the type wanted
'

'

If bvType = 1 Then
    WalletReportShopee.ListObjects("TbRCSRelatorioGeral").Range.AutoFilter Field:=15, Criteria1:="<>"
    WalletReportShopee.ListObjects("TbRCSRelatorioGeral").Range.AutoFilter Field:=13, Criteria1:="="
    WalletReportShopee.ListObjects("TbRCSRelatorioGeral").Range.AutoFilter Field:=10, Criteria1:="="
End If

End Sub

```

## Database_InBook

```visual-basic
Global QrAntecipaReport As ADODB.Recordset
Global QrOrdemReport As ADODB.Recordset

Global WBConnection As ADODB.Connection

Sub GetTablesToRecordset(Optional ByVal bvQrAntecipaReport As Boolean, Optional ByVal bvQrOrdemReport As Boolean)
'
' This code will get the tables in this workbook and put that in a record set
'

'
Dim SourcePath As String
    'SourcePath = Range("RefAddress[Data]").Value & "\Relatório Financeiro Shopee.xlsm" '"\Relatório Financeiro Shopee.xlsm"
    'Setting and starting the database
    Set WBConnection = New ADODB.Connection

    WBConnection.Open "Provider=Microsoft.ACE.OLEDB.12.0;Data Source=" & _
        "##########################\Relatório Financeiro Shopee.xlsm" & _
        ";Extended Properties=""Excel 12.0 Xml;HDR=YES"";"

    If bvQrAntecipaReport Then
        Set QrAntecipaReport = New ADODB.Recordset

        QrAntecipaReport.Open "SELECT * FROM [" & QuickFoundReport.Name & "$]", WBConnection, adOpenStatic, adLockBatchOptimistic

    End If

    If bvQrOrdemReport Then
        Set QrOrdemReport = New ADODB.Recordset

        QrOrdemReport.Open "SELECT * FROM [" & OrderReport.Name & "$]", WBConnection, adOpenStatic, adLockBatchOptimistic

    End If

End Sub
Sub WBConnectionDesconect()
'
' This will close the Connectionection with the database
'

'
    If Not WBConnection Is Nothing Then 'check if the Connectionection is open, and if it is, it is close and the memory cleaned
        WBConnection.Close
        Set WBConnection = Nothing
    End If


End Sub



```

## InSheetEvents

```visual-basic
Public Function CopyToClipboard(ByVal ClipboardText As String)
'
' This will save a given value to the clipboard
'

'

Dim dataObj As New MSForms.DataObject
    dataObj.SetText ClipboardText
    dataObj.PutInClipboard

End Function

```

