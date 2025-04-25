# File objective

> This app updates the database by inserting new products and variations, as well as suggesting SKU names, weight range, etc. 

## Observations

- [x] Excel functions have been left out. Check the files directly.

## Update notes

- [ ] Converter os tipos de dado -> CNPJ para string, para o excel n converter em ns

### Funções

- [x] Função para copiar produto (tirando as informações que vão mudar, como peso e etc)
- [x] Quando inserir/atualizar o fornecedor, a tabela deve inserir o fornecedor (já faz) e atualizar novamente a tabela de fornecedor

### Integração

- [ ] Adicionar opção do tamanho unitário (opcional para cadastro, definindo: tamanho unitário líquido, tamanho do pacote líquido, tamanho bruto do pacote)
- [ ] Adicionar um campo para unidades com sinalização para kit
- [ ] Mudar a arquitetura do banco de dados para suportar kits de diferentes produtos e fornecedor primário e original
- [ ] Integrar a calculadora de caixa para estimar a caixa a partir do tamanho do produto
- [ ] Histórico para os SKU's
- [ ] Possibilitar uma única categoria ter mais de um NCM e CEST
- [x] Remover conectores do texto que formam o SKU automático ("DE", "COM" etc.)

---

# ⚙️VBA

## Buttons

```visual-basic
Sub ListProducts()
'
' This code will get the information in the database and bring it in the table "TbCPDadProduct"
'

'
Application.EnableEvents = False
Application.ScreenUpdating = False
Application.Calculation = xlCalculationManual

DBConnect 'get connect with the database
SetTableColumnsCurrentNumb 'Set the columns address for the tables


Dim DadProduct As ADODB.Recordset 'save the values of the database's sheet "BD_DadProduct"
    Set DadProduct = New ADODB.Recordset

Dim Variations As ADODB.Recordset ' save the values of the database's sheet "BD_Variations"
    Set Variations = New ADODB.Recordset

    DadProduct.Open "SELECT * FROM BD_DadProduct ORDER BY ID_DadProduct", DBConnection

'Clear end set all data

    ProductRegister.Range("TbCPDadProduct").ClearContents
    ProductRegister.ListObjects("TbCPDadProduct").Resize Intersect(Range("TbCPDadProduct[#all]"), Range("12:13"))

    ProductRegister.Range("TbCPVariations").ClearContents
    ProductRegister.ListObjects("TbCPVariations").Resize Intersect(Range("TbCPVariations[#all]"), Range("22:23"))

    Range("Q13:R13,R15,R17:R19,S14:U14,S17:T17,T18,V14:W16,Q17,R20").ClearContents

    Range("AE12:AE17").ClearContents

    Range("R9,AE9").Value = "Nenhuma"

Dim i As Integer 'Counter for the free lines
    i = 13

    'Do not update to past all, it is cute see all loading and fast enough :v
    Do While DadProduct.EOF = False
        ProductRegister.Cells(i, TbCPDadProductColumnsNumb(1)).Value = DadProduct!ProductName_DadProduct
        ProductRegister.Cells(i, TbCPDadProductColumnsNumb(2)).Value = DadProduct!NCM_DadProduct
        ProductRegister.Cells(i, TbCPDadProductColumnsNumb(3)).Value = DadProduct!CEST_DadProduct
        ProductRegister.Cells(i, TbCPDadProductColumnsNumb(4)).Value = DadProduct!ID_DadProduct
        ProductRegister.Cells(i, TbCPDadProductColumnsNumb(5)).Value = "Nenhuma"
        ProductRegister.Cells(i, TbCPDadProductColumnsNumb(6)).Value = DadProduct!UpdateDate_DadProduct

    i = i + 1
    DadProduct.MoveNext
    Loop

    If Not DadProduct Is Nothing Then  'Close record set and clean memory
        DadProduct.Close
        Set DadProduct = Nothing

    End If

Application.EnableEvents = True
Application.ScreenUpdating = True
Application.Calculation = xlCalculationAutomatic

DBDisconnect

'Check the datatype
DataValidation True

End Sub
Sub DadProductActionStart()
'
'
' This App will send the information so the database can be started

'
Dim counter(1 To 4) As Integer

    If MsgBox("Prosseguir com a atualização?", vbYesNo, "Atenção!") = vbYes Then
SetTableColumnsCurrentNumb

        For Each ActionCell In Range("TbCPDadProduct[Ação]")
            If ActionCell.Value = "Deletar" Then
                DBDadProductDelete Cells(ActionCell.Row, TbCPDadProductColumnsNumb(4)).Value

                counter(2) = counter(2) + 1
            ElseIf ActionCell.Value <> "Nenhuma" Then
                counter(4) = counter(4) + 1

            End If
        Next

DataValidation True, bvMsgBox:=False

        If ValidationErros(1) > 0 And counter(4) <> 0 Then

            MsgBox counter(4) & " Itens foram deletados com sucesso", Title:="Atualização realizada com sucesso"

            DataValidation True

            Exit Sub

        ElseIf ValidationErros(1) > 0 Then
            DataValidation True

            Exit Sub

        End If

        For Each ActionCell In Range("TbCPDadProduct[Ação]")
            If ActionCell.Value = "Atualizar" Then
                DBDadProductUpdate Cells(ActionCell.Row, TbCPDadProductColumnsNumb(1)).Value, Cells(ActionCell.Row, TbCPDadProductColumnsNumb(2)).Value, _
                    Cells(ActionCell.Row, TbCPDadProductColumnsNumb(3)).Value, Cells(ActionCell.Row, TbCPDadProductColumnsNumb(4)).Value

                counter(1) = counter(1) + 1

            ElseIf ActionCell.Value = "Inserir novo" Then
                DBDadPRoductInsert Cells(ActionCell.Row, TbCPDadProductColumnsNumb(1)).Value, Cells(ActionCell.Row, TbCPDadProductColumnsNumb(2)).Value, _
                    Cells(ActionCell.Row, TbCPDadProductColumnsNumb(3)).Value

                counter(3) = counter(3) + 1
            End If
        Next

        MsgBox "Foram Atualizados: " & counter(1) & " Itens" & Chr(10) & Chr(10) & _
            "Foram Inseridos: " & counter(3) & " Itens" & Chr(10) & Chr(10) & _
            "Foram Deletados: " & counter(2) & " Itens", Title:="Atualização realizada com sucesso"
ListProducts
    End If
End Sub
Sub VariationsDetailsActionStart()
'
' This app will start the database update, delete or insert action
'

'

Dim counter(1 To 3) As Integer

    If MsgBox("Prosseguir com a atualização?", vbYesNo, "Atenção!") = vbYes Then
SetTableColumnsCurrentNumb

'It checks if a DadProduct was select so the code can run
    If Range("TbCPDadProduct[Nome do produto]").Count <> 1 Then
        MsgBox "Você precisa selecionar um produto para fazer alterações em detalhes da variação", vbCritical, "Produto não selecionado"

        Exit Sub
    End If

        If ProductRegister.Range("R9").Value = "Deletar" Then

            DBVariationsDelete Range("T18").Value
            Range("AE12:AE17").ClearContents

            counter(2) = counter(2) + 1

            MsgBox counter(2) & " Itens foram deletados com sucesso", Title:="Atualização realizada com sucesso"
        Else
DataValidation VariationsDetail:=True

            If ValidationErros(1) > 0 Then

                Exit Sub

            End If
        End If

        If ProductRegister.Range("R9").Value = "Atualizar" Then
            If ProductRegister.Range("T18").Value = "" Or ProductRegister.Range("T18").Value < 1 Or Not IsNumeric(ProductRegister.Range("AE16").Value) Then
                MsgBox "O item que você está tentando atualizar não está com o ID sincronizado!" & Chr(10) & Chr(10) & _
                    "Sincronize o ID para continuar", vbCritical, "ID não sincronizado"

                Exit Sub

            Else
                With ProductRegister
                    DBVariationsUpdate .Range("Q13").Value, .Range("AE16").Value, .Range("R17").Value, .Range("S17").Value, .Range("T18").Value, .Range("T17").Value _
                        , .Range("S14").Value, .Range("T14").Value, .Range("U14").Value, .Range("V14").Value, .Range("V15").Value, .Range("V16").Value _
                        , .Range("W14").Value, .Range("W15").Value, .Range("W16").Value, .Range("R15").Value, .Range("Q17").Value _
                        , .Range("R20").Value, .Range("R19").Value

                End With

                counter(1) = counter(1) + 1

                BDC_VariationsFill ProductRegister.Range("TbCPVariations[ID]").Find(ProductRegister.Range("T18").Value) 'reload variations details
                DataValidation VariationsDetail:=True

            End If
        ElseIf ProductRegister.Range("R9").Value = "Inserir novo" Then

DBConnect
Dim Variations As ADODB.Recordset ' save the values of the database's sheet "BD_Variations"
    Set Variations = New ADODB.Recordset

    Variations.Open "SELECT * FROM BD_Variations WHERE SKU_Variations=""" & ProductRegister.Range("Q13").Value & """", DBConnection

            If Not Variations.BOF Then
                DBDisconnect

                MsgBox "O SKU informando já esta cadastrado dentro do banco de dados" & Chr(10) & Chr(10) & _
                    "Altere o SKU para prosseguir", vbCritical, "SKU duplicado"

                Exit Sub

            End If

            With ProductRegister
                DBVariationsInsert .Range("Q13").Value, .Range("AE16").Value, .Range("R17").Value, .Range("S17").Value, Range("TbCPDadProduct[ID]").Value _
                    , .Range("T17").Value, .Range("S14").Value, .Range("T14").Value, .Range("U14").Value, .Range("V14").Value, .Range("V15").Value _
                    , .Range("V16").Value, .Range("W14").Value, .Range("W15").Value, .Range("W16").Value, .Range("R15").Value, .Range("Q17").Value _
                    , .Range("R20").Value, .Range("R19").Value

            End With

            Range("Q13:R13,R15,R17:R19,S14:U14,S17:T17,T18,V14:W16,Q17,R20").ClearContents 'Clear variations
            Range("AE12:AE17").ClearContents 'clear supplier

            counter(3) = counter(3) + 1

        End If

        MsgBox "Foram Atualizados: " & counter(1) & " Itens" & Chr(10) & Chr(10) & _
                "Foram Inseridos: " & counter(3) & " Itens" & Chr(10) & Chr(10) & _
                "Foram Deletados: " & counter(2) & " Itens", Title:="Atualização realizada com sucesso"

        ProductRegister.Range("R9").Value = "Nenhuma"
        BDC_DadProductSelect ProductRegister.Range("TbCPDadProduct[ID]")

DBDisconnect

    End If
End Sub
Sub SupplierActionStart()
'
' This app will manage the update of the table supplier
'

'
Dim counter(1 To 3) As Integer

    If MsgBox("Prosseguir com a atualização?", vbYesNo, "Atenção!") = vbYes Then



        If ProductRegister.Range("AE9").Value = "Deletar" Then

            DBSupplierDelete bvID:=ProductRegister.Range("AE16").Value

            counter(2) = counter(2) + 1
        Else

DataValidation bvSupplier:=True
            If ValidationErros(1) > 0 Then


                Exit Sub

            End If
        End If

        Select Case Range("AE9").Value

            Case Is = "Atualizar"
                If ProductRegister.Range("AE16").Value = "" Or ProductRegister.Range("AE16").Value < 1 Or Not IsNumeric(ProductRegister.Range("AE16").Value) Then
                    MsgBox "O item que você está tentando atualizar não está com o ID sincronizado!" & Chr(10) & Chr(10) & _
                        "Sincronize o ID para continuar", vbCritical, "ID não sincronizado"

                    Exit Sub

                Else

                    With ProductRegister
                        DBSupplierUpdate bvName:=.Range("AE12").Value, bvCompanyName:=.Range("AE13").Value, bvCNPJ:=.Range("AE14").Value, bvType:=.Range("AE15").Value _
                            , bvID:=.Range("AE16").Value, bvNote:=.Range("AE17").Value

                    End With

                    ActiveWorkbook.Connections("Query - BD_Supplier").Refresh
                    ProductRegister.Range("AE9").Value = "Nenhuma"
                    counter(1) = counter(1) + 1

                End If

            Case Is = "Inserir novo"
DBConnect
Dim Supplier(1 To 2) As ADODB.Recordset ' save the values of the database's sheet "BD_Variations"
    Set Supplier(1) = New ADODB.Recordset
    Set Supplier(2) = New ADODB.Recordset

    Supplier(1).Open "SELECT * FROM BD_Supplier WHERE CompanyName_Supplier=""" & ProductRegister.Range("AE13").Value & """", DBConnection
    Supplier(2).Open "SELECT * FROM BD_Supplier WHERE CNPJ_Supplier=" & ProductRegister.Range("AE14").Value, DBConnection

            If Not Supplier(1).BOF Then
                MsgBox "Nome fantasia já está cadastrado!" & Chr(10) & Chr(10) & "Atualize o nome", vbCritical, "Duplicata do nome fantasia"

                Exit Sub

            ElseIf Not Supplier(2).BOF Then
                MsgBox "CNPJ já está cadastrado em outro fornecedor!" & Chr(10) & Chr(10) & "Atualize o CNPJ", vbCritical, "Duplicata do CNPJ"

                Exit Sub

            End If

                With ProductRegister
                    DBSupplierInsert bvName:=.Range("AE12").Value, bvCompanyName:=.Range("AE13").Value, bvCNPJ:=.Range("AE14").Value, bvType:=.Range("AE15").Value _
                        , bvNote:=.Range("AE17").Value

                End With

                ActiveWorkbook.Connections("Query - BD_Supplier").Refresh
                ProductRegister.Range("AE9").Value = "Nenhuma"
                Range("R13").Value = Range("AE13").Value

                counter(3) = counter(3) + 1
DBDisconnect
        End Select

        MsgBox "Foram Atualizados: " & counter(1) & " Itens" & Chr(10) & Chr(10) & _
                "Foram Inseridos: " & counter(3) & " Itens" & Chr(10) & Chr(10) & _
                "Foram Deletados: " & counter(2) & " Itens", Title:="Atualização realizada com sucesso"


    End If
End Sub

Sub DataValidationDadProductActionStart()
    DataValidation DadProduct:=True

End Sub
Sub DataValidationVariationsActionStart()
    DataValidation VariationsDetail:=True

End Sub
Sub DataValidationSuppliersActionStart()
    DataValidation bvSupplier:=True

End Sub


```

## CrossModules

```visual-basic
Global TbCPDadProductColumnsNumb(1 To 6) As Integer
Global TbCPVariationsColumnsNumb(1 To 7) As Integer
Global ValidationErros(1) As Integer

Sub SetTableColumnsCurrentNumb()

    On Error GoTo ErroMsg

    TbCPDadProductColumnsNumb(1) = Range("TbCPDadProduct[Nome do produto]").Column
    TbCPDadProductColumnsNumb(2) = Range("TbCPDadProduct[NCM]").Column
    TbCPDadProductColumnsNumb(3) = Range("TbCPDadProduct[CEST]").Column
    TbCPDadProductColumnsNumb(4) = Range("TbCPDadProduct[ID]").Column
    TbCPDadProductColumnsNumb(5) = Range("TbCPDadProduct[Ação]").Column
    TbCPDadProductColumnsNumb(6) = Range("TbCPDadProduct[Última atualização]").Column

    TbCPVariationsColumnsNumb(1) = Range("TbCPVariations[SKU]").Column
    TbCPVariationsColumnsNumb(2) = Range("TbCPVariations[Fornecedor]").Column
    TbCPVariationsColumnsNumb(3) = Range("TbCPVariations[Tamanho]").Column
    TbCPVariationsColumnsNumb(4) = Range("TbCPVariations[Cor]").Column
    TbCPVariationsColumnsNumb(5) = Range("TbCPVariations[Corpo]").Column
    TbCPVariationsColumnsNumb(6) = Range("TbCPVariations[EAN]").Column
    TbCPVariationsColumnsNumb(7) = Range("TbCPVariations[ID]").Column

Exit Sub
ErroMsg:
    MsgBox "Um erro foi identificado na nomenclatura de uma das tabelas." & Chr(10) & Chr(10) & _
    "Verifique o nome das colunas das tabelas", vbCritical, "Erro no título da tabela"

End Sub
Sub SupplierFill(ByVal bvIDSupplier As Long, ByVal ConnectToDatabase As Boolean)
Application.EnableEvents = False
ProductRegister.Range("AE9").Value = "Nenhuma"

If ConnectToDatabase Then
   DBConnect
End If

Dim Supplier As ADODB.Recordset 'Getting data from Supplier where ID_Supplier = target
    Set Supplier = New ADODB.Recordset

    Supplier.Open "SELECT * FROM BD_Supplier WHERE ID_Supplier=" & bvIDSupplier, DBConnection

    ProductRegister.Range("AE12").Value = Supplier!Name_Supplier
    ProductRegister.Range("AE13").Value = Supplier!CompanyName_Supplier
    ProductRegister.Range("AE14").Value = Supplier!CNPJ_Supplier
    ProductRegister.Range("AE15").Value = Supplier!Type_Supplier
    ProductRegister.Range("AE16").Value = Supplier!ID_Supplier
    ProductRegister.Range("AE17").Value = Supplier!Note_Supplier

If ConnectToDatabase Then
    DBDisconnect
End If
Application.EnableEvents = True
End Sub
Sub DataValidation(Optional ByVal DadProduct As Boolean, Optional ByVal VariationsDetail As Boolean, Optional ByVal bvMsgBox As Boolean = True, Optional ByVal bvSupplier As Boolean)
'
' This App will check if all the data is correct to send to the database
'

'
Application.ScreenUpdating = False

Dim counter(1 To 2) As Integer 'Marker 1
'
'Check Dad Product table
'
    If DadProduct Then
SetTableColumnsCurrentNumb

        For Each ProductNameCell In Range("TbCPDadProduct[Nome do produto]") 'Check the product name's len is > 10
            If Not Len(Cells(ProductNameCell.Row, TbCPDadProductColumnsNumb(1)).Value) > 10 Then
                With ProductNameCell.Interior
                    .ThemeColor = xlThemeColorDark1
                End With
                ProductNameCell.Font.ThemeColor = xlThemeColorLight1
'Marker 1
                counter(1) = counter(1) + 1
            Else
                With ProductNameCell.Interior
                    .ThemeColor = xlThemeColorDark2
                    .TintAndShade = -0.749992370372631
                End With
                ProductNameCell.Font.ThemeColor = xlThemeColorDark1

            End If
        Next

        For Each NCMNameCell In Range("TbCPDadProduct[NCM]") 'check if the ncm is number and have a len of 8
            If Len(NCMNameCell.Value) <> 8 Or Not IsNumeric(NCMNameCell) Then
                With NCMNameCell.Interior
                    .ThemeColor = xlThemeColorDark1
                End With
                NCMNameCell.Font.ThemeColor = xlThemeColorLight1
'Marker 1
                counter(1) = counter(1) + 1
            Else
                With NCMNameCell.Interior
                    .ThemeColor = xlThemeColorDark2
                    .TintAndShade = -0.749992370372631
                End With
                NCMNameCell.Font.ThemeColor = xlThemeColorDark1
            End If
        Next

        For Each CESTNameCell In Range("TbCPDadProduct[CEST]") 'check if the CEST have a len of 7
            If CESTNameCell < 100000 Or CESTNameCell > 9999999 Or Not IsNumeric(CESTNameCell) Then
                With CESTNameCell.Interior
                    .ThemeColor = xlThemeColorDark1
                End With
                CESTNameCell.Font.ThemeColor = xlThemeColorLight1
'Marker 1
                counter(1) = counter(1) + 1
            Else
                With CESTNameCell.Interior
                    .ThemeColor = xlThemeColorDark2
                    .TintAndShade = -0.749992370372631
                End With
                CESTNameCell.Font.ThemeColor = xlThemeColorDark1
            End If
        Next

    End If

'
'Check Variations detail table
'

    If VariationsDetail Then
        If Range("R10").Value <> 0 Or Range("Q13").Value = "" Then 'Check if SKU is not empty and don't have special characters
            Range("Q13").Offset(-1).Interior.ThemeColor = xlThemeColorDark1
            Range("Q13").Offset(-1).Font.ThemeColor = xlThemeColorLight1

            counter(1) = counter(1) + 1
        Else
            With Range("Q13").Offset(-1).Interior
                .ThemeColor = xlThemeColorDark2
                .TintAndShade = -0.749992370372631
            End With
            Range("Q13").Offset(-1).Font.ThemeColor = xlThemeColorDark1

        End If

        For Each VariationsNumbCell In Range("R17:T17,V14:W16") 'Check if the table numbers are numbers
            If Not IsNumeric(VariationsNumbCell.Value) And VariationsNumbCell.Value <> "" Then
                VariationsNumbCell.Interior.ThemeColor = xlThemeColorDark1
                VariationsNumbCell.Font.ThemeColor = xlThemeColorLight1

                counter(1) = counter(1) + 1

            Else
                With VariationsNumbCell.Interior
                    .ThemeColor = xlThemeColorDark2
                    .TintAndShade = -0.749992370372631
                End With
                VariationsNumbCell.Font.ThemeColor = xlThemeColorDark1

            End If
        Next

        For Each VariationsEmptyCell In Range("R17:S17,R13,T14") 'Check if the not optional values are not empty
            If VariationsEmptyCell.Value = "" Or VariationsEmptyCell.Value = 0 Then
                VariationsEmptyCell.Offset(-1).Interior.ThemeColor = xlThemeColorDark1
                VariationsEmptyCell.Offset(-1).Font.ThemeColor = xlThemeColorLight1

                counter(1) = counter(1) + 1

            Else
                With VariationsEmptyCell.Offset(-1).Interior
                    .ThemeColor = xlThemeColorDark2
                    .TintAndShade = -0.749992370372631

                End With
                VariationsEmptyCell.Offset(-1).Font.ThemeColor = xlThemeColorDark1

            End If
        Next

        For Each VariationsLogicCell In Range("W14:W17") 'check if the sizes are logical and set a optional counter
            If VariationsLogicCell.Offset(, -1).Value > VariationsLogicCell.Value And VariationsLogicCell.Value <> 0 And VariationsLogicCell.Value <> "" Then
                VariationsLogicCell.Offset(, 1).Interior.ThemeColor = xlThemeColorDark1
                VariationsLogicCell.Offset(, 1).Font.ThemeColor = xlThemeColorLight1

                counter(2) = counter(2) + 1

            Else
                With VariationsLogicCell.Offset(, 1).Interior
                    .ThemeColor = xlThemeColorDark2
                    .TintAndShade = -0.749992370372631

                End With
                VariationsLogicCell.Offset(, 1).Font.ThemeColor = xlThemeColorDark1
            End If
        Next

        'Check the sizes volume
        If Range("W17").Value < Range("V17").Value And Not Range("W17").Value <> "" Then
            counter(1) = counter(1) + 1
            counter(2) = 0
        End If

        For Each VariationsLogic2cell In Range("T17") ' check if the sizes are logical
            If VariationsLogic2cell.Offset(, -1).Value > VariationsLogic2cell.Value And VariationsLogic2cell.Value <> "" And VariationsLogic2cell.Value <> 0 Then
                VariationsLogic2cell.Offset(-1).Interior.ThemeColor = xlThemeColorDark1
                VariationsLogic2cell.Offset(-1).Font.ThemeColor = xlThemeColorLight1

                counter(1) = counter(1) + 1
            Else
                With VariationsLogic2cell.Offset(-1).Interior
                    .ThemeColor = xlThemeColorDark2
                    .TintAndShade = -0.749992370372631

                End With
                VariationsLogic2cell.Offset(-1).Font.ThemeColor = xlThemeColorDark1
            End If
        Next

        If Len(Range("Q17").Value) <> 13 And Range("Q17").Value <> "" Then 'check if the EAN len is 13
            Range("Q16").Interior.ThemeColor = xlThemeColorDark1
            Range("Q16").Font.ThemeColor = xlThemeColorLight1

            counter(1) = counter(1) + 1

        Else
            With Range("Q16").Interior
                .ThemeColor = xlThemeColorDark2
                .TintAndShade = -0.749992370372631
            End With
            Range("Q16").Font.ThemeColor = xlThemeColorDark1
        End If
    End If

'
' Check Supplier table
'

    If bvSupplier Then
        For Each NotEmptySupplier In Range("AE12:AE15") 'check if the values are not empty
            If NotEmptySupplier.Value = "" Then
                NotEmptySupplier.Offset(, -1).Interior.ThemeColor = xlThemeColorDark1
                NotEmptySupplier.Offset(, -1).Font.ThemeColor = xlThemeColorLight1

                counter(1) = counter(1) + 1
            Else
                With NotEmptySupplier.Offset(, -1).Interior
                    .ThemeColor = xlThemeColorDark2
                    .TintAndShade = -0.749992370372631

                End With
                NotEmptySupplier.Offset(, -1).Font.ThemeColor = xlThemeColorDark1
            End If
        Next

        If Len(Range("AE14").Value) > 14 Or Len(Range("AE14").Value) < 13 Or Not IsNumeric(Range("A14").Value) Then 'check it the CNPJ is number and it's len is 14
            Range("AE14").Offset(, -1).Interior.ThemeColor = xlThemeColorDark1
            Range("AE14").Offset(, -1).Font.ThemeColor = xlThemeColorLight1

            counter(1) = counter(1) + 1

        Else
            With Range("AE14").Offset(, -1).Interior
                .ThemeColor = xlThemeColorDark2
                .TintAndShade = -0.749992370372631

            End With
            Range("AE14").Offset(, -1).Font.ThemeColor = xlThemeColorDark1

        End If


        If Len(Range("AE12").Value) <= 10 Then 'check if the name has at least a len of 10
            Range("AE12").Offset(, -1).Interior.ThemeColor = xlThemeColorDark1
            Range("AE12").Offset(, -1).Font.ThemeColor = xlThemeColorLight1

            counter(1) = counter(1) + 1

        Else
            With Range("AE12").Offset(, -1).Interior
                .ThemeColor = xlThemeColorDark2
                .TintAndShade = -0.749992370372631

            End With
            Range("AE12").Offset(, -1).Font.ThemeColor = xlThemeColorDark1

        End If

    End If

Application.ScreenUpdating = True

'Marker 1
    If counter(1) > 0 And bvMsgBox Then

        MsgBox "Foram identificados " & counter(1) & " Inconformidades na planilha" & Chr(10) & Chr(10) & "Resolva as incoerências para realizar o envio para o banco de dados", vbCritical, "Inconformidade nos dados"
    ElseIf counter(2) > 0 Then
        If MsgBox("Foram identificados Inconformidades opcionais na planilha, deseja prosseguir de qualquer maneira?", vbYesNo, "Inconformidades opcionais") = vbNo Then
            counter(1) = 1

        End If
    End If
    ValidationErros(1) = counter(1)
End Sub

```

## DataBase

```visual-basic
Global DBConnection As ADODB.Connection 'save the connection path

Sub DBConnect()
'
' This will open a connection with the database
'

'

Set DBConnection = New ADODB.Connection

Dim PathToDB_Alpha(1 To 2) As String  'save the path to the database, so we don't need repeat it
    PathToDB_Alpha(1) = stSettings.Range("F12").Value & "\Banco de dados\BD_Alpha.accdb"
    PathToDB_Alpha(2) = "Provider=Microsoft.ACE.OLEDB.12.0; Data Source =" & PathToDB_Alpha(1) & "; Persist Security Info=False" ';Jet Oledb:DataBase password=ff123"

    DBConnection.Open PathToDB_Alpha(2) 'start our connection with the database

End Sub

Sub DBDisconnect()
'
' This will close the connection with the database
'

'
    If Not DBConnection Is Nothing Then 'check if the connection is open, and if it is, it is close and the memory cleaned
        DBConnection.Close
        Set DBConnection = Nothing
    End If
End Sub
Sub DBDadProductUpdate(ByVal bvDadProduct As String, ByVal bvNCM As Long, ByVal bvCEST As Long, ByVal bvID As Long)
'
' This App will update the database
'

'
DBConnect
    DBConnection.Execute "UPDATE BD_DadProduct SET ProductName_DadProduct =""" & bvDadProduct & """, NCM_DadProduct =" & bvNCM & _
        ", CEST_DadProduct =" & bvCEST & ", UpdateDate_DadProduct = """ & Date & """" & _
        " WHERE ID_DadProduct =" & bvID

DBDisconnect
End Sub
Sub DBDadProductDelete(ByVal bvID As Long)
'
' This app will delete data from the database with password
'

'

DBConnect
    DBConnection.Execute "DELETE FROM BD_DadProduct WHERE ID_DadProduct =" & bvID

DBDisconnect
End Sub
Sub DBDadPRoductInsert(ByVal bvDadProduct As String, ByVal bvNCM As Long, ByVal bvCEST As Long)
DBConnect

    DBConnection.Execute "INSERT INTO BD_DadProduct (ProductName_DadProduct, NCM_DadProduct, CEST_DadProduct)" & _
        "VALUES (""" & bvDadProduct & """," & bvNCM & "," & bvCEST & ")"

DBDisconnect
End Sub
Sub DBVariationsUpdate(ByVal bvSKU As String, ByVal bvSupplierID As Long, ByVal bvBuyingPrice As Double, ByVal bvNetWeight As Integer, ByVal bvID As Long, _
    Optional ByVal bvGrossWeight As Integer, Optional ByVal bvSize As String, Optional ByVal bvColor As String, Optional ByVal bvBody As String, _
    Optional ByVal bvPx As Integer, Optional ByVal bvPy As Integer, Optional ByVal bvPz As Integer, Optional ByVal bvBx As Integer, _
    Optional ByVal bvBy As Integer, Optional ByVal bvBz As Integer, Optional ByVal bvMaterial As String, Optional ByVal bvEAN As String, _
    Optional ByVal bvImage As String, Optional ByVal bvNote As String)

DBConnect

    DBConnection.Execute "UPDATE BD_Variations SET SKU_Variations=""" & bvSKU & """, Size_Variations=""" & bvSize & """,Color_Variations=""" & bvColor & _
        """,Body_Variations=""" & bvBody & """,Px_Variations=" & bvPx & ",Py_Variations=" & bvPy & ",Pz_Variations=" & bvPz & ",Bx_Variations=" & bvBx & _
        ",By_Variations=" & bvBy & ",Bz_Variations=" & bvBz & ",NetWeight_Variations=" & bvNetWeight & ",GrossWeight_Variations=" & bvGrossWeight & _
        ",BuyingPrice_Variations=" & Replace(bvBuyingPrice, ",", ".") & ",Supplier_Variations=" & bvSupplierID & ",EAN_Variations=""" & bvEAN & """,Image_Variations=""" & bvImage & _
        """,Note_Variations=""" & bvNote & """,Material_Variations=""" & bvMaterial & """,UpdateDate_Variations=""" & Date & _
        """ WHERE ID_Variations=" & bvID

DBDisconnect
End Sub
Sub DBVariationsDelete(ByVal bvID As Long)
DBConnect

    DBConnection.Execute "DELETE FROM BD_Variations WHERE ID_Variations =" & bvID

DBDisconnect
End Sub
Sub DBVariationsInsert(ByVal bvSKU As String, ByVal bvSupplierID As Long, ByVal bvBuyingPrice As String, ByVal bvNetWeight As Integer, ByVal bvFkID_DadProduct As Long, _
    Optional ByVal bvGrossWeight As Integer, Optional ByVal bvSize As String, Optional ByVal bvColor As String, Optional ByVal bvBody As String, _
    Optional ByVal bvPx As Integer, Optional ByVal bvPy As Integer, Optional ByVal bvPz As Integer, Optional ByVal bvBx As Integer, _
    Optional ByVal bvBy As Integer, Optional ByVal bvBz As Integer, Optional ByVal bvMaterial As String, Optional ByVal bvEAN As String, _
    Optional ByVal bvImage As String, Optional ByVal bvNote As String)

DBConnect

    DBConnection.Execute "INSERT INTO BD_Variations (SKU_Variations,Supplier_Variations,BuyingPrice_Variations,NetWeight_Variations,GrossWeight_Variations" & _
        ", Size_Variations, Color_Variations, Body_Variations, Px_Variations, Py_Variations, Pz_Variations, Bx_Variations, By_Variations, Bz_Variations" & _
        ", Material_Variations, EAN_Variations, Image_Variations, Note_Variations, FKID_DadProduct_Variations)" & _
    "VALUES (""" & bvSKU & """," & bvSupplierID & "," & CInt(bvBuyingPrice) & "," & bvNetWeight & "," & bvGrossWeight & ",""" & bvSize & """,""" & bvColor & _
        """,""" & bvBody & """," & bvPx & "," & bvPy & "," & bvPz & "," & bvBx & "," & bvBy & "," & bvBz & ",""" & bvMaterial & _
        """,""" & bvEAN & """,""" & bvImage & """,""" & bvNote & """," & bvFkID_DadProduct & ")"

DBDisconnect
End Sub
Sub DBSupplierUpdate(ByVal bvName As String, ByVal bvCompanyName As String, ByVal bvCNPJ As Double, ByVal bvType As String, ByVal bvID As Long, Optional ByVal bvNote As String)
DBConnect

    DBConnection.Execute "UPDATE BD_Supplier SET Name_Supplier =""" & bvName & """, CNPJ_Supplier=" & bvCNPJ & ", Note_Supplier=""" & bvNote & _
        """,Type_Supplier=""" & bvType & """,CompanyName_Supplier=""" & bvCompanyName & """ WHERE ID_Supplier=" & bvID


DBDisconnect
End Sub
Sub DBSupplierInsert(ByVal bvName As String, ByVal bvCompanyName As String, ByVal bvCNPJ As Double, ByVal bvType As String, Optional ByVal bvNote As String)
DBConnect

   DBConnection.Execute "INSERT INTO BD_Supplier (Name_Supplier,CNPJ_Supplier,Note_Supplier,Type_Supplier,CompanyName_Supplier)" & _
        "VALUES (""" & bvName & """," & bvCNPJ & ",""" & bvNote & """,""" & bvType & """,""" & bvCompanyName & """)"

DBDisconnect
End Sub
Sub DBSupplierDelete(ByVal bvID As Long)
DBConnect

   DBConnection.Execute "DELETE FROM BD_Supplier WHERE ID_Supplier =" & bvID

DBDisconnect

End Sub

```

## SheetEvents

```visual-basic
Sub BDC_VariationsFill(ByVal Target As Range)

SetTableColumnsCurrentNumb 'update the table address
Application.EnableEvents = False ' stop the events so this code don't over run
Application.Calculation = xlCalculationManual

DBConnect 'Open link with database

Dim Logical(1) As Boolean 'check if there's the info required to run the supplier database

Dim Variations As ADODB.Recordset 'Getting data from Variations where FKID_DadProdut = target
    Set Variations = New ADODB.Recordset

    Variations.Open "SELECT * FROM BD_Variations WHERE ID_Variations=" & Cells(Target.Row, TbCPVariationsColumnsNumb(7)).Value, DBConnection

'If in case the database have some data that has not a supplier, this will run the code without update supplier and asks the user to set a supplier
    If Cells(Target.Row, TbCPVariationsColumnsNumb(2)).Value = "" Or Cells(Target.Row, TbCPVariationsColumnsNumb(2)).Value < 1 _
        Or Not IsNumeric(Cells(Target.Row, TbCPVariationsColumnsNumb(2)).Value) Then

        Logical(1) = True

    Else

Dim Supplier As ADODB.Recordset 'Getting data from Supplier where ID_Supplier = target
    Set Supplier = New ADODB.Recordset

        Supplier.Open "SELECT * FROM BD_Supplier WHERE ID_Supplier=" & Variations!Supplier_Variations, DBConnection

    End If


    'Filling the Product description table

    Range("Q13:R13,R15,R17:R19,S14:U14,S17:T17,T18,V14:W16,Q17,R20").ClearContents 'clean table

    ProductRegister.Range("Q13").Value = Variations!SKU_Variations

    If Not Logical(1) Then 'if there's a Supplier ID
        ProductRegister.Range("R13").Value = Supplier!CompanyName_Supplier
    End If

    ProductRegister.Range("R15").Value = Variations!Material_Variations
    ProductRegister.Range("Q17").Value = Variations!EAN_Variations
    ProductRegister.Range("R17").Value = Variations!BuyingPrice_Variations
    ProductRegister.Range("R18").Value = Variations!UpdateDate_Variations
    ProductRegister.Range("R19").Value = Variations!Note_Variations
    ProductRegister.Range("S14").Value = Variations!Size_Variations
    ProductRegister.Range("T14").Value = Variations!Color_Variations
    ProductRegister.Range("U14").Value = Variations!Body_Variations
    ProductRegister.Range("S17").Value = Variations!NetWeight_Variations
    ProductRegister.Range("T17").Value = Variations!GrossWeight_Variations
    ProductRegister.Range("V14").Value = Variations!Px_Variations
    ProductRegister.Range("V15").Value = Variations!Py_Variations
    ProductRegister.Range("V16").Value = Variations!Pz_Variations
    ProductRegister.Range("W14").Value = Variations!Bx_Variations
    ProductRegister.Range("W15").Value = Variations!By_Variations
    ProductRegister.Range("W16").Value = Variations!Bz_Variations
    ProductRegister.Range("T18").Value = Variations!ID_Variations
    ProductRegister.Range("R20").Value = Variations!Image_Variations

'Gets the last ID on BD_Variations
Dim FindingMaxID As ADODB.Recordset
    Set FindingMaxID = New ADODB.Recordset

    FindingMaxID.Open "SELECT MAX(ID_Variations) FROM BD_Variations", DBConnection
    ProductRegister.Range("Q10").CopyFromRecordset FindingMaxID

    If Not Logical(1) Then 'if there's a Supplier ID
        'Filling the supplier table
        SupplierFill Variations!Supplier_Variations, False

    End If

    If Logical(1) Then 'If there's not a Supplier ID
        MsgBox "O item escolhido não possui Fornecedor!" & Chr(10) & Chr(10) & "Defina um fornecedor para o item!", vbInformation, "Fornecedor não cadastrado!"

    End If

DBDisconnect 'Close link with database
ProductRegister.Range("R9").Value = "Nenhuma"
Application.EnableEvents = True
Application.Calculation = xlCalculationAutomatic

End Sub
Sub BDC_DadProductSelect(ByVal Target As Range)

SetTableColumnsCurrentNumb 'update the table address
DBConnect 'get connect with the database
Application.EnableEvents = False

'Getting data from DadProduct where ID_DadProduct = target
Dim DadProduct As ADODB.Recordset
    Set DadProduct = New ADODB.Recordset

    DadProduct.Open "SELECT * FROM BD_DadProduct WHERE ID_DadProduct=" & Cells(Target.Row, TbCPDadProductColumnsNumb(4)).Value, DBConnection

    'Clean table
    ProductRegister.Range("TbCPDadProduct").ClearContents
    ProductRegister.ListObjects("TbCPDadProduct").Resize Intersect(Range("TbCPDadProduct[#all]"), Range("12:13"))

    'Fill table with target info
    ProductRegister.Cells(13, TbCPDadProductColumnsNumb(1)).Value = DadProduct!ProductName_DadProduct
    ProductRegister.Cells(13, TbCPDadProductColumnsNumb(2)).Value = DadProduct!NCM_DadProduct
    ProductRegister.Cells(13, TbCPDadProductColumnsNumb(3)).Value = DadProduct!CEST_DadProduct
    ProductRegister.Cells(13, TbCPDadProductColumnsNumb(4)).Value = DadProduct!ID_DadProduct
    ProductRegister.Cells(13, TbCPDadProductColumnsNumb(5)).Value = "Nenhuma"
    ProductRegister.Cells(13, TbCPDadProductColumnsNumb(6)).Value = DadProduct!UpdateDate_DadProduct


Dim Variations As ADODB.Recordset 'Getting data from Variations where FKID_DadProdut = target
    Set Variations = New ADODB.Recordset

    Variations.Open "SELECT * FROM BD_Variations WHERE FKID_DadProduct_Variations=" & Cells(13, TbCPDadProductColumnsNumb(4)).Value & _
    " ORDER BY ID_Variations", DBConnection

    ProductRegister.Range("TbCPVariations").ClearContents
    ProductRegister.ListObjects("TbCPVariations").Resize Intersect(Range("TbCPVariations[#all]"), Range("22:23"))

Dim i As Integer 'Counter for the free line
    i = 23

    Do While Variations.EOF = False
        ProductRegister.Cells(i, TbCPVariationsColumnsNumb(1)).Value = Variations!SKU_Variations
        ProductRegister.Cells(i, TbCPVariationsColumnsNumb(2)).Value = Variations!Supplier_Variations
        ProductRegister.Cells(i, TbCPVariationsColumnsNumb(3)).Value = Variations!Size_Variations
        ProductRegister.Cells(i, TbCPVariationsColumnsNumb(4)).Value = Variations!Color_Variations
        ProductRegister.Cells(i, TbCPVariationsColumnsNumb(5)).Value = Variations!Body_Variations
        ProductRegister.Cells(i, TbCPVariationsColumnsNumb(6)).Value = Variations!EAN_Variations
        ProductRegister.Cells(i, TbCPVariationsColumnsNumb(7)).Value = Variations!ID_Variations

    i = i + 1
    Variations.MoveNext
    Loop

Application.EnableEvents = True
DBDisconnect

End Sub
Sub C_DadProductStatus(ByVal Target As Range)

Application.EnableEvents = False
SetTableColumnsCurrentNumb 'Get the table collumns numb

    If Cells(Target.Row, TbCPDadProductColumnsNumb(5)).Value = "Nenhuma" And Target.Column <> TbCPDadProductColumnsNumb(5) Then

        Cells(Target.Row, TbCPDadProductColumnsNumb(5)).Value = "Atualizar"

    ElseIf Cells(Target.Row, TbCPDadProductColumnsNumb(5)).Value = "" Then

        Cells(Target.Row, TbCPDadProductColumnsNumb(5)).Value = "Inserir novo"

    End If

Application.EnableEvents = True

End Sub

Sub C_UpdateSupplier(ByVal SupplierName As String)

Dim TableAddress(1 To 2) As Range
    Set TableAddress(1) = Supplier.Range("BD_Supplier[ID_Supplier]")
    Set TableAddress(2) = Supplier.Range("BD_Supplier[CompanyName_Supplier]")

Dim FindingID 'Get the range of the cell that was found
    With TableAddress(2)
    Set FindingID = .Find(SupplierName, LookIn:=xlValues, MatchCase:=False, matchbyte:=True, SearchOrder:=xlByRows)

Dim FirstFindingID As String 'Save the first value that has been found
        If Not FindingID Is Nothing Then 'if there as duplicate
            FirstFindingID = FindingID.Address
    Set FindingID = .FindNext(FindingID)

            If FindingID.Address <> FirstFindingID Then
                MsgBox "Este item possui uma duplicata, revise a lista de fornecedores!", vbCritical, "Duplicatas"
                Range("R13").ClearContents

                Exit Sub

            Else
                SupplierFill Supplier.Cells(FindingID.Row, TableAddress(1).Column).Value, True

            End If
        End If
    End With
End Sub
Sub C_VariationsDetails(ByVal Target As Range)
Application.EnableEvents = False

    Range("R9").Value = "Atualizar"

Application.EnableEvents = True
End Sub

```

## In Sheet Events

### ProductRegister

```visual-basic
Private Sub Worksheet_BeforeDoubleClick(ByVal Target As Range, Cancel As Boolean)
'
'
' This app will check the double click on the variation table, get it ID and give all the info at the table above
' It also fill the Supplier table

'
    If Not Intersect(Range("TbCPVariations"), Target) Is Nothing Then
        BDC_VariationsFill Target

    End If

'
'
' This app after a double click, get the product ID from the target line and open the database getting that one data, what will be place as 1 line in
' Table. It also brings the variations from that one selected

'
    If Not Intersect(Range("TbCPDadProduct"), Target) Is Nothing Then
        BDC_DadProductSelect Target

    End If

'
' To make it easy to switch the value for "Inserir novo" we're adding this function
'

'
    If Not Intersect(Target, Range("R9,AE9")) Is Nothing Then
        Target.Value = "Inserir novo"

        If Target.Address = Range("R9").Address Then
              Range("Q17,R17,S17,T17,R15,T14,U14,S14,V14,V15,V16,W14,W16,W15,R13,Q13,R19,R20,T18").Value = ""

        End If
        If Target.Address = Range("AE9").Address Then
            Range("AE16").Value = ""

        End If

    End If

    If Target.Address = Range("Q13").Address Then
        Range("Q13").Value = Range("Q15").Value

        If Range("R10").Value <> 0 Then
            MsgBox "O formato automático deste SKU possuí caracteres inválidos" & Chr(10) & Chr(10) & _
                "Corrija as incoerências para enviar para o banco de dados", vbCritical, "Caracteres inválidos"
        End If
    End If

End Sub

Private Sub Worksheet_Change(ByVal Target As Range)
'
' So we don't need change the status all, this app will change the status for Update or Insert Into for us
'

'
    If Not Intersect(Range("TbCPDadProduct"), Target) Is Nothing Then
        C_DadProductStatus Target

    End If

'
' To update the supplier as I change the supplier cells automatically
'

'
    If Target.Address = Range("R13").Address Then
        C_UpdateSupplier Target.Value

    End If

'
' To clean the ID and SKU cells when adding a new product
'

'
    If Target.Address = Range("R9").Address Then
        If Target.Value = "Inserir novo" Then
            Range("T18").Value = ""
            Range("Q13").Value = ""
        End If

    End If


'
' To update the VariationsDetails as I change the VariationsDetails cells automatically
'

'
    If Not Intersect(Range("Q13:R13,R15,R17:R19,S14:U14,S17:T17,T18,V14:W16,Q17,R20"), Target) Is Nothing And Range("R9").Value = "Nenhuma" Then
        C_VariationsDetails Target    

    End If

'
' To update the status if we change the supplier table values automatically
'

'
    If Not Intersect(Range("AE12:AE17"), Target) Is Nothing And Range("AE9").Value = "Nenhuma" Then
        Range("AE9").Value = "Atualizar"

    End If
End Sub

```
