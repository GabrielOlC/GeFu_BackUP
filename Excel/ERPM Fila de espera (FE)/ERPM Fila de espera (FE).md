# File objective

> This app should assist the individual responsible for packing the products in understanding the details of each purchase and ensuring items are dispatched correctly. It minimizes errors related to product quantity, color, or type by utilizing visual and auditory Poka Yoke techniques. 
> Given that the packer also determines the prices, the app provides insights into profit and expenses, as well as records of the product's maximum weight, batch profit, and customizable profit indicators in color ranges. 
> Additionally, it automatically generates a report summarizing the packed and dispatched items to be sent to partners and suppliers.

### Observations

- [x] Query snippets have been left out. Check the files directly.

- [x] Excel functions have been left out. Check the files directly.

## Update notes

### Dashboard Dedicado

- [ ] Quando um item for processado como 'cadastrado', apagar o item marcado anteriormente.
- [x] Se nenhum item for importado, exibir a mensagem: "Não há itens a serem cadastrados."
- [x] Ao importar um item a cadastrar, trocar o status para "enviar", mas avisar que já era um item bipado.
- [ ] Permitir dois cliques na quantidade de compras de um usuário para mostrar todos os itens comprados por ele.

### Integração

- [ ] Ao bipar um produto que não está em estoque, cadastrar automaticamente como compra ou solicitação de compra e lançar um aviso para verificação manual dos estoques
- [x] Ao rodar o código:
  - Fazer verificações de início e fim.
  - Se tudo der certo, deletar o backup.
  - Caso contrário, abrir o backup e solicitar verificação manual.
  - Incluir verificação de integridade das tabelas (remover textos abaixo).
- [ ] Caso não exista preço cadastrado no "peso bruto" do banco de dados, solicitar o peso e cadastrar o produto (aqui mesmo no dashboard na beepagem - opcional).
- [ ] Criar um novo dashboard com filtro para SKU, mostrando todos os IDs na horizontal e as unidades (do SKU) na vertical.
- [x] Ao vender, permitir que valores sejam tanto estáticos quanto dinâmicos.
- [ ] Ao selecionar manualmente produtos, limpar o código de rastreio no dashboard.
- [x] Adicionar opção de incluir notas no pedido, além das que já vêm da Shopee.
- [ ] Ao bipar, verificar se o produto precisa de validação de saída (dimensão, peso, etc.) para atualizar o banco de dados.
- [x] Criar um dashboard com o volume de vendas por mês.
- [x] Permitir alterar o status atual para qualquer outro status no painel de status.
- [ ] Melhorar o mecanismo de cores do dashboard para itens que são kits com mais de uma cor.
- [ ] Quando bipar e não encontrar um produto:
  - Liberar a opção para cadastrá-lo, mesmo que esteja bipado no azul.
  - Remover o produto que foi bipado por último.
- [ ] Salvar os valores de exportação de um lote.
- [ ] Permitir adicionar notas no sistema:
  - De forma individual ou em grupo.
  - Considerar tirar as notas da tabela auxiliar e colocá-las na tabela principal (inclusive as notas da Shopee).
- [ ] Lista de bipagem:
  - Melhorar caixas de mensagens para copiar para o clipboard (exibir mensagem antes de copiar e permitir múltiplas cópias parciais com opções de selecionar novamente).
  - Aplicar a mesma funcionalidade de "item diferente" também para "item já beepado."
- [x] No dashboard dedicado:
  - Adicionar célula para verificar se o valor da Shopee é igual ao valor calculado.
  - Automatizar a equação usada para este cálculo (o sistema deve pegar os valores de unidade atualizados).

---

# ⚙️VBA

## APP - Import Data

```visual-basic
'Importar os dados da planilha OrderToShip exportada pela shopee
'Coletar os dados já não processados (que não tem código de rastreio) e importar para "Waiting Line"
'Retornar os CPF para emitir nota no ERP Bling
' - Cuidar para não repetir CPF's. Caso tenha algum problema, e algum CPF não pode ser emitido, ele vai ficar na lista de espera
'   A nova lista para importar também vai trazer o mesmo CPF, esse CPF não pode entrar na lista de envio sem alerta

Sub GetDatafromOrderToShip()
'
' This gets the ids that doesn't have tracking codes, import and set as "revisar" those each were already import early
'

'
    Application.ScreenUpdating = False 'Allow the user to use other programs while this run (the screen doesn't change while the code runs)
    Application.Calculation = xlCalculationManual 'Stop updating the cells values that has calculations - so the macro runs faster

'Update the table columns numb
SetTableColumnsCurrentNumb

Dim PathToOrderToShip As FileDialog
    'Setting the filedialong
    Set PathToOrderToShip = Application.FileDialog(msoFileDialogFilePicker)
    With PathToOrderToShip
        .InitialFileName = "Desktop" 'Update to get anyone’s desktop
        .AllowMultiSelect = False
        .Filters.Add "Arquivos compativeis", "*.xlsx", 1
        .Title = "Escolha o arquivo OrderToShipe >> Da Shopee <<"
    End With

Dim WorkBooksNames(1 To 2) As Workbook 'will save workbook names to switch between them while check data. It will be defined right before switch
    Set WorkBooksNames(1) = ActiveWorkbook 'saving workbook

        'Getting the path if not empty
        If PathToOrderToShip.Show = -1 Then
        'WorkingOnData
            'Sorting the data
            Workbooks.Open (PathToOrderToShip.SelectedItems(1))
    Set WorkBooksNames(2) = ActiveWorkbook 'saving workbook
            'Checking the data
            If OrderToShip(Range("A1:BD1")) And _
                WorksheetFunction.CountA(Rows(1)) = 56 _
                Then

Dim StoringTable As Range
    Set StoringTable = Range("A1").CurrentRegion

    With ActiveWorkbook.Sheets(1).Sort
        .SortFields.Clear
        .SortFields.Add StoringTable.Columns(4), xlSortOnValues, xlAscending
        .SetRange StoringTable
        .Header = xlYes
        .Apply
    End With

                'Getting the column address

Dim AddressToEmptyValues As Integer

                If Range("D" & Range("A1").CurrentRegion.Rows.Count).Value = "" Then 'check if the column is not fully empty so the next loop will not be infinite
                    AddressToEmptyValues = Range("A1").CurrentRegion.Rows.Count

                    GoTo NextStep

                Else

                    Range("D2").Select

                    'do not update this, the "" cells ARE NOT empty! cannot use the empty function >v
                    If ActiveCell.Value = "" Then 'Check if there is any code to update
                        While ActiveCell.Value = ""
                            If ActiveCell.Offset(1).Value = "" Then
                                ActiveCell.Offset(1, 0).Select

                            Else
                                AddressToEmptyValues = ActiveCell.Row

                                GoTo NextStep

                            End If
                        Wend
                    Else
                        MsgBox "Não há nenhum código à ser importado" & Chr(10) & Chr(10) & _
                            "Note que os produtos não podem ser emitidos ANTES de serem exportados. Faça a beepagem dos produtos e os importe com a função:" & Chr(10) & Chr(10) & _
                            "Cadastrar ""ID do pedido"" através do ""Número de rastreamento"" ", vbCritical, "Importação cancelada"

                            WorkBooksNames(1).Activate
                            WorkBooksNames(2).Close SaveChanges:=False
                            CleanSettings

                        Exit Sub

                    End If
                End If

            Else
                Beep
                MsgBox "A arquitetura do documento não corresponde a arquitetura da programação!", Title:="Erro de arquitetura"

            End If

        'if empty AND agreed to try select file again
        ElseIf MsgBox("Nenhum arquivo foi escolhido, deseja voltar a seleção?", vbYesNo, "NENHUM arquivo selecionado") = 6 Then
            GetDatafromOrderToShip

        Else
            CleanSettings
            Exit Sub

        End If

'For some reason when u don't select a file and then select a file, the code runs good but jump out the if and run "NextSetp"
'To make sure "NextStep" will not run at all unless it is called, exit sub was also added here
CleanSettings
Exit Sub
NextStep:

Dim FindingDuplicates As Range 'save true or false for having or not a duplicate
Dim G2(1 To 2) As Integer 'Counter for marker 1
Dim RlTableEmptyrow As Integer 'tells the numb of the cell each is empty on the TbCpMainData
Dim G3(1 To 3) As Integer 'Counter for marker 2 - count data
    G3(1) = 0
    G3(2) = 0
    G3(3) = 0


    'Checking for duplicates and importing
    With WorkBooksNames(1).Sheets("Fila de espera").Range("TbFEMainData[ID do pedido]")

        For G1 = 2 To AddressToEmptyValues
            WorkBooksNames(2).Activate

Set FindingDuplicates = .Find(Range("A" & G1).Value, LookIn:=xlValues, MatchCase:=True, matchbyte:=True)

            If Not FindingDuplicates Is Nothing Then 'if there as duplicate
                If WorkBooksNames(1).Sheets("Fila de espera").Cells(FindingDuplicates.Row, TbFEMainDataColumnsNumb(10)).Value = "" Then

                    WorkBooksNames(1).Sheets("Fila de espera").Cells(FindingDuplicates.Row, TbFEMainDataColumnsNumb(10)).Value = "Revisar"
'Marker 2
                    G3(1) = G3(1) + 1 'Num of data repeated

                    Application.StatusBar = "Pedidos importados: " & G3(2) & " Itens importados: " & G3(2) + G3(3) & " Itens a revisar: " & G3(1)

                End If

            Else

'Marker 1
                If _
                    IsEmpty(WorkBooksNames(1).Sheets("Fila de espera").Range("TbFEMainData[ID do pedido]")) And _
                    IsEmpty(WorkBooksNames(1).Sheets("Fila de espera").Range("TbFEMainData[Número de rastreamento]")) _
                    Then

                    G2(1) = 8

                Else
                    G2(1) = WorkBooksNames(1).Sheets("Fila de espera").Range("TbFEMainData[ID do pedido]").Rows.Count + 8 'free cell at table TbFEMainData
                End If


'Marker 1
                G2(2) = WorksheetFunction.CountA(WorkBooksNames(1).Sheets("Fila de espera").Range("TbCP_MainData[FK_ID Do pedido]")) + 8 'free cell at table TbCP_MainData

            'Main table
                ' ID do pedido
                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(2)).Value = _
                WorkBooksNames(2).Sheets(1).Range("A" & G1).Value

                'Hora do pagamento do pedido
                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(3)).Value = _
                WorkBooksNames(2).Sheets(1).Range("J" & G1).Value

                'Hora de criação do pedido
                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(18)).Value = _
                WorkBooksNames(2).Sheets(1).Range("I" & G1).Value

                'Peso bruto do pedido
                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(4)).Value = _
                WorkBooksNames(2).Sheets(1).Range("V" & G1).Value

                'Valor total
                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(5)).Value = _
                WorkBooksNames(2).Sheets(1).Range("AH" & G1).Value

                'Total global
                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(6)).Value = _
                WorkBooksNames(2).Sheets(1).Range("AO" & G1).Value

                'Frete estimado
                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(7)).Value = _
                WorkBooksNames(2).Sheets(1).Range("AP" & G1).Value

                'CPF do comprador
                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(8)).Value = _
                WorkBooksNames(2).Sheets(1).Range("AT" & G1).Value

                'CEP
                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(9)).Value = _
                WorkBooksNames(2).Sheets(1).Range("BA" & G1).Value

                'Comissão
                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(12)).Value = _
                WorkBooksNames(2).Sheets(1).Range("AM" & G1).Value

                'Frete Pago
                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(13)).Value = _
                WorkBooksNames(2).Sheets(1).Range("AI" & G1).Value

                'Taxa de serviço
                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(15)).Value = _
                WorkBooksNames(2).Sheets(1).Range("AN" & G1).Value

                'Cupons
                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(17)).Value = _
                WorkBooksNames(2).Sheets(1).Range("Z" & G1).Value

            'Cp table
                ' ID do pedido foreing key
                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(1)).Value = _
                WorkBooksNames(2).Sheets(1).Range("A" & G1).Value

                'SKU
                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(2)).Value = _
                WorkBooksNames(2).Sheets(1).Range("M" & G1).Value

                'Preço original
                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(3)).Value = _
                WorkBooksNames(2).Sheets(1).Range("O" & G1).Value

                'Preço acordado
                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(4)).Value = _
                WorkBooksNames(2).Sheets(1).Range("P" & G1).Value

                'Quantidade
                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(5)).Value = _
                WorkBooksNames(2).Sheets(1).Range("Q" & G1).Value

                'Observação do comprador
                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(6)).Value = _
                WorkBooksNames(2).Sheets(1).Range("BB" & G1).Value

                'Nota
                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(7)).Value = _
                WorkBooksNames(2).Sheets(1).Range("BD" & G1).Value


'Marker 2
                G3(2) = G3(2) + 1 'Num of times it past main values without repeat

                Application.StatusBar = "Pedidos importados: " & G3(2) & " Itens importados: " & G3(2) + G3(3) & " Itens a revisar: " & G3(1)

                If WorkBooksNames(2).Sheets(1).Range("A" & G1).Offset(1).Value = WorkBooksNames(2).Sheets(1).Range("A" & G1).Value Then
                    Do
                    G1 = G1 + 1
'Marker 1
                    G2(2) = WorksheetFunction.CountA(WorkBooksNames(1).Sheets("Fila de espera").Range("TbCP_MainData[FK_ID Do pedido]")) + 8 'Update the free cell at table TbCP_MainData

                        ' ID do pedido foreign key
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(1)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("A" & G1).Value

                        'SKU
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(2)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("M" & G1).Value

                        'Preço original
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(3)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("O" & G1).Value

                        'Preço acordado
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(4)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("P" & G1).Value

                        'Quantidade
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(5)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("Q" & G1).Value

                        'Observação do comprador
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(6)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("BB" & G1).Value

                        'Nota
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(7)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("BD" & G1).Value


'Marker 2
                    G3(3) = G3(3) + 1

                    Application.StatusBar = "Pedidos importados: " & G3(2) & " Itens importados: " & G3(2) + G3(3) & " Itens a revisar: " & G3(1)

                    Loop Until WorkBooksNames(2).Sheets(1).Range("A" & G1).Offset(1).Value <> WorkBooksNames(2).Sheets(1).Range("A" & G1).Value

                End If
            End If

        Next
    End With
    WorkBooksNames(1).Activate
    WorkBooksNames(2).Close SaveChanges:=False
    Application.ScreenUpdating = True

    Application.Calculation = xlCalculationAutomatic

    Application.StatusBar = ""

    MsgBox "Foram importados com sucesso " & G3(2) & " Pedidos, num total de " & G3(2) + G3(3) & " Itens com " & G3(1) & " Pedidos a revisar!"

    SetClipBoardWithOrderID 'This will get the ID's to send the NF
End Sub

Sub GetDataFromPackingList()
'
' This imports the tracking code after we import the order to ship list
'

'
    Application.ScreenUpdating = False

'Update the table columns numb
SetTableColumnsCurrentNumb

Dim PathToPackingList As FileDialog
        'Setting the filedialong
Set PathToPackingList = Application.FileDialog(msoFileDialogFilePicker)
    With PathToPackingList
        .InitialFileName = "desktop" 'Update to get anyones desktop
        .AllowMultiSelect = False
        .Filters.Add "Arquivos compativeis", "*.xlsx", 1
        .Title = "Escolha o arquivo Lista de empacotamento >> Da Shopee <<"
    End With

Dim WorkBooksNames(1 To 2) As Workbook 'will save workbook names to switch between them while check data. It will be defined right before switch
Set WorkBooksNames(1) = ActiveWorkbook 'saving workbook

        'Getting the path if not empty
        If PathToPackingList.Show = -1 Then
            Workbooks.Open (PathToPackingList.SelectedItems(1))
Set WorkBooksNames(2) = ActiveWorkbook 'saving workbook
            If PackingList(Range("A1:E1")) And _
                WorksheetFunction.CountA(Rows(1)) = 5 _
                Then

Dim FindingMatching As Range
Dim G2(1 To 3) As Integer 'Marker 1
    G2(1) = WorkBooksNames(1).Sheets("Fila de espera").Range("TbFEMainData[ID do pedido]").Count 'Counts how many data I have to import
    G2(2) = 0 'Count how many products will be shipping with correios

                With WorkBooksNames(2).Sheets(1).Range("A1").CurrentRegion.Columns(2)

'Marker 1
                    For G1 = 8 To G2(1) + 7
Set FindingMatching = .Find(WorkBooksNames(1).Sheets("Fila de espera").Cells(G1, TbFEMainDataColumnsNumb(2)).Value, LookIn:=xlValues, MatchCase:=True, matchbyte:=True)

                        If Not FindingMatching Is Nothing Then 'if there is a matching
                            WorkBooksNames(1).Sheets("Fila de espera").Cells(G1, TbFEMainDataColumnsNumb(1)).Value = _
                            WorkBooksNames(2).Sheets(1).Range("A" & FindingMatching.Row).Value

                            If WorkBooksNames(1).Sheets("Fila de espera").Cells(G1, TbFEMainDataColumnsNumb(10)).Value = "" Then
                                WorkBooksNames(1).Sheets("Fila de espera").Cells(G1, TbFEMainDataColumnsNumb(10)).Value = "Impresso"

                            ElseIf WorkBooksNames(1).Sheets("Fila de espera").Cells(G1, TbFEMainDataColumnsNumb(10)).Value = "Revisar" Then

                                G2(3) = G2(3) + 1
                            End If

                            'Already set the carrier
                            Select Case Len(WorkBooksNames(2).Sheets(1).Range("A" & FindingMatching.Row).Value)
                                Case 13 And Mid(WorkBooksNames(2).Sheets(1).Range("A" & FindingMatching.Row).Value, 12, 13) = "BR"

                                    WorkBooksNames(1).Sheets("Fila de espera").Cells(G1, TbFEMainDataColumnsNumb(11)).Value = "Correios"
'Marker 1
                                    G2(2) = G2(2) + 1
                                Case _
                                    25 And Mid(WorkBooksNames(2).Sheets(1).Range("A" & FindingMatching.Row).Value, 16, 5) = "SPXLM", _
                                    26 And Mid(WorkBooksNames(2).Sheets(1).Range("A" & FindingMatching.Row).Value, 16, 5) = "SPXLM"

                                    WorkBooksNames(1).Sheets("Fila de espera").Cells(G1, TbFEMainDataColumnsNumb(11)).Value = "Shopee Xpress"
                                Case Else

                                    WorkBooksNames(1).Sheets("Fila de espera").Cells(G1, TbFEMainDataColumnsNumb(11)).Value = "Desconhecido"
                            End Select
                        End If

                    Next

                End With
                WorkBooksNames(1).Activate
                WorkBooksNames(2).Close SaveChanges:=False
                Application.ScreenUpdating = True

                If G2(2) <> 0 Or G2(3) <> 0 Then
                        Beep
                        MsgBox G2(2) & " Pedidos especiais" & Chr(10) & G2(3) & " Pedidos a revisar atualizados"

                Else
                        Beep
                        MsgBox "Nenhum pedido especial"
                End If
            Else
                Beep
                MsgBox "A arquitetura do documento não corresponde a arquitetura da programação!", Title:="Erro de arquitetura"

            End If

         ElseIf MsgBox("Nenhum arquivo foi escolhido, deseja voltar a seleção?", vbYesNo, "NENHUM arquivo selecionado") = 6 Then
            GetDataFromPackingList
         Else
            Exit Sub
         End If

End Sub
Sub GetDataFromOtherToShipBR()
'
' This code does the same as order to ship but, for those products that haven’t been imported early for any reason.
' This one import the data based on the tracking code, while order to ship do it based on the ID
'

'
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual

'Update the table columns numb
SetTableColumnsCurrentNumb

Dim PathToOrderToShip As FileDialog
    'Setting the filedialong
    Set PathToOrderToShip = Application.FileDialog(msoFileDialogFilePicker)
    With PathToOrderToShip
        .InitialFileName = "A:\gabri\Desktop\Baixados" 'Update to get anyone’s desktop
        .AllowMultiSelect = False
        .Filters.Add "Arquivos compativeis", "*.xlsx", 1
        .Title = "Escolha o arquivo OrderToShipe >> Da Shopee <<"
    End With

Dim WorkBooksNames(1 To 2) As Workbook 'will save workbook names to switch between them while check data. It will be defined right before switch
    Set WorkBooksNames(1) = ActiveWorkbook 'saving workbook

        'getting the path if not empty
        If PathToOrderToShip.Show = -1 Then
        'WorkingOnData
            'Sorting the data
            Workbooks.Open (PathToOrderToShip.SelectedItems(1))
    Set WorkBooksNames(2) = ActiveWorkbook 'saving workbook
            'Checking the data
            If OrderToShip(Range("A1:BD1")) And _
                WorksheetFunction.CountA(Rows(1)) = 56 _
                Then

Dim StoringTable As Range
    Set StoringTable = Range("A1").CurrentRegion

    With ActiveWorkbook.Sheets(1).Sort
        .SortFields.Clear
        .SortFields.Add StoringTable.Columns(4), xlSortOnValues, xlDescending
        .SetRange StoringTable
        .Header = xlYes
        .Apply
    End With

                'getting the collumn address

Dim AddressToEmptyValues As Integer

                If Range("D" & Range("A1").CurrentRegion.Rows.Count).Value <> "" Then 'check if the collumn is not full empty so the next loop will not be infinit
                    AddressToEmptyValues = Range("A1").CurrentRegion.Rows.Count

                    GoTo NextStep

                Else

                    Range("D2").Select

                    'do not update this, the "" cells ARE NOT really empty! cannot use the empty function >v
                    While ActiveCell.Value <> ""
                        If ActiveCell.Offset(1).Value <> "" Then
                            ActiveCell.Offset(1, 0).Select

                        Else
                            AddressToEmptyValues = ActiveCell.Row

                            GoTo NextStep

                        End If
                    Wend
                End If

            Else
                Beep
                MsgBox "A arquitetura do documento não corresponde a arquitetura da programação!", Title:="Erro de arquitetura"

            End If

        'if empty AND agreed to try select file again
        ElseIf MsgBox("Nenhum arquivo foi escolhido, deseja voltar à seleção?", vbYesNo, "NENHUM arquivo selecionado") = 6 Then
            GetDataFromOtherToShipBR
        Else
            Exit Sub
        End If

'For some reason when u don't select a file and then select a file, the code runs well but jump out the if and run "NextSetp"
'To make sure "NextStep" will not run at all unless it is called, exit sub was also added here
Exit Sub
NextStep:

Dim FindingDuplicates As Range 'save true or false for having or not a duplicate
Dim G2(1 To 2) As Integer 'Counter for marker 1
Dim RlTableEmptyrow As Integer 'tells the numb of the cell each is empty on the TbCpMainData
Dim G3(2 To 3) As Integer 'Counter for marker 2 - count data
    G3(2) = 0
    G3(3) = 0

    'Checking for duplicates and importing
    With WorkBooksNames(1).Sheets("Fila de espera").Range("TbFEMainData[Número de rastreamento]")

        For G1 = 2 To AddressToEmptyValues
            WorkBooksNames(2).Activate

Set FindingDuplicates = .Find(Mid(Range("D" & G1).Value, 1, 15), LookIn:=xlValues, MatchCase:=True, matchbyte:=True)

            If Not FindingDuplicates Is Nothing Then 'if there as duplicate
                If Not WorkBooksNames(1).Sheets("Fila de espera").Cells(FindingDuplicates.Row, TbFEMainDataColumnsNumb(2)).Value <> "" Then

'Marker 1
                    G2(1) = FindingDuplicates.Row 'Cell where found the value
                    G2(2) = WorksheetFunction.CountA(WorkBooksNames(1).Sheets("Fila de espera").Range("TbCP_MainData[FK_ID Do pedido]")) + 8 'free cell at table TbCP_MainData

                    'Main table
                        ' ID do pedido
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(2)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("A" & G1).Value

                        'Hora do pagamento do pedido
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(3)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("J" & G1).Value

                        'Hora de criação do pedido
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(18)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("I" & G1).Value

                        'Peso bruto do pedido
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(4)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("V" & G1).Value

                        'Valor total
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(5)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("AH" & G1).Value

                        'Total global
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(6)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("AO" & G1).Value

                        'Frete estimado
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(7)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("AP" & G1).Value

                        'CPF do comprador
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(8)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("AT" & G1).Value

                        'CEP
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(9)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("BA" & G1).Value

                        'Comissão
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(12)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("AM" & G1).Value

                        'Frete Pago
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(13)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("AI" & G1).Value

                        'Taxa de serviço
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(15)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("AN" & G1).Value

                        'Cupons
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(1), TbFEMainDataColumnsNumb(17)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("Z" & G1).Value


                    'Cp table
                        ' ID do pedido foreing key
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(1)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("A" & G1).Value

                        'SKU
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(2)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("M" & G1).Value

                        'Preço original
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(3)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("O" & G1).Value

                        'Preço acordado
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(4)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("P" & G1).Value

                        'Quantidade
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(5)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("Q" & G1).Value

                        'Observação do comprador
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(6)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("BB" & G1).Value

                        'Nota
                        WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(7)).Value = _
                        WorkBooksNames(2).Sheets(1).Range("BD" & G1).Value


'Marker 2
                    G3(2) = G3(2) + 1 'Num of times it past main values without repeat
                    Application.StatusBar = "Pedidos importados: " & G3(2) & " Itens importados: " & G3(2) + G3(3)

                        If WorkBooksNames(2).Sheets(1).Range("A" & G1).Offset(1).Value = WorkBooksNames(2).Sheets(1).Range("A" & G1).Value Then
                            Do
                            G1 = G1 + 1
'Marker 1
                            G2(2) = WorksheetFunction.CountA(WorkBooksNames(1).Sheets("Fila de espera").Range("TbCP_MainData[FK_ID Do pedido]")) + 8 'Update the free cell at table TbCP_MainData

                                ' ID do pedido foreing key
                                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(1)).Value = _
                                WorkBooksNames(2).Sheets(1).Range("A" & G1).Value

                                'SKU
                                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(2)).Value = _
                                WorkBooksNames(2).Sheets(1).Range("M" & G1).Value

                                'Preço original
                                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(3)).Value = _
                                WorkBooksNames(2).Sheets(1).Range("O" & G1).Value

                                'Preço acordado
                                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(4)).Value = _
                                WorkBooksNames(2).Sheets(1).Range("P" & G1).Value

                                'Quantidade
                                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(5)).Value = _
                                WorkBooksNames(2).Sheets(1).Range("Q" & G1).Value

                                'Observação do comprador
                                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(6)).Value = _
                                WorkBooksNames(2).Sheets(1).Range("BB" & G1).Value

                                'Nota
                                WorkBooksNames(1).Sheets("Fila de espera").Cells(G2(2), TbCP_MainDataColumnsNumb(7)).Value = _
                                WorkBooksNames(2).Sheets(1).Range("BD" & G1).Value


'Marker 2
                            G3(3) = G3(3) + 1

                            Application.StatusBar = "Pedidos importados: " & G3(2) & " Itens importados: " & G3(2) + G3(3)

                            Loop Until WorkBooksNames(2).Sheets(1).Range("A" & G1).Offset(1).Value <> WorkBooksNames(2).Sheets(1).Range("A" & G1).Value

                        End If
                End If

            End If

        Next
    End With
    WorkBooksNames(1).Activate
    WorkBooksNames(2).Close SaveChanges:=False

    Application.ScreenUpdating = True

    Application.Calculation = xlCalculationAutomatic

    Application.StatusBar = ""

    MsgBox "Foram importados com sucesso " & G3(2) & " Pedidos, num total de " & G3(2) + G3(3) & " Itens"

End Sub

```

## Buttons

```visual-basic
Sub ClearDataTables()
'
' Clean all the data in "lista de espera"
'

'

    If _
        MsgBox("Está operação não pode ser desfeita!" & Chr(13) & "Deseja continuar assim mesmo?", vbYesNo, "Proceda com cuidado!") = 6 _
        Then

        If _
        InputBox("Digite a senha para confirmar a ação", "Confirmação final") = "123456" _
            Then

'It gets the current columns each table is
SetTableColumnsCurrentNumb

            Range("TbFEMainData").ClearContents
            ActiveSheet.ListObjects("TbFEMainData").Resize Range(Cells(7, WorksheetFunction.Min(TbFEMainDataColumnsNumb)), Cells(8, WorksheetFunction.Max(TbFEMainDataColumnsNumb)))

            Range("TbCP_MainData").ClearContents
            ActiveSheet.ListObjects("TbCP_MainData").Resize Range(Cells(7, WorksheetFunction.Min(TbCP_MainDataColumnsNumb)), Cells(8, WorksheetFunction.Max(TbCP_MainDataColumnsNumb)))
        Else
            MsgBox "A operação foi cancelada"
        End If
    Else
        MsgBox "A operação foi cancelada"
    End If

End Sub

Sub SetAsSent()
'
' Set the Status column of TbFEMainData from "Enviar" to "Enviado"
'

'
    Application.ScreenUpdating = False

'It gets the current columns each table is
SetTableColumnsCurrentNumb

    If MsgBox("Esta operação irá configurar o status ""Enviar"" como ""Enviado""" & Chr(13) & "Deseja continuar assim mesmo?", vbYesNo, "Esta operação não é reversível") = 6 Then
        For Each Cell In Range(Cells(8, TbFEMainDataColumnsNumb(10)), Cells(Range("TbFEMainData").Rows.Count + 7, TbFEMainDataColumnsNumb(10)))
            If Cell.Value = "Enviar" Then
                Cell.Value = "Enviado"
            End If
        Next
    End If

    Application.ScreenUpdating = True
End Sub

Sub SetClipBoardWithOrderID()
'
' This gets the ID's from TbFEMainData where has no status (where has just being added) and copy it to the clipboard with at most 50 ID per turn
'

'
Application.ScreenUpdating = False

'It gets the current columns each table is
SetTableColumnsCurrentNumb

Dim ClipboardData As New MSForms.DataObject
Dim ClipboardPreData As String 'clipboard variable to set all the Id's before set the text to the ClipboardData data object

Dim G1 As Integer 'Counter - Marker 1
G1 = 0

    For Each Cell In Range(Cells(8, TbFEMainDataColumnsNumb(10)), Cells(Range("TbFEMainData").Rows.Count + 7, TbFEMainDataColumnsNumb(10)))
        If Cell.Value = "" Then

            ClipboardPreData = ClipboardPreData & Cells(Cell.Row, TbFEMainDataColumnsNumb(2)) & ";"
'Marker 1
            G1 = G1 + 1

            If G1 = 50 Then

               ClipboardData.SetText ClipboardPreData
               ClipboardData.PutInClipboard
               G1 = 0

               ClipboardPreData = ""
               Beep
               MsgBox "50 códigos foram copiados para o seu clipboard! Ainda tem mais vindo!", Title:="Operação pausada em 50"
            End If
        End If
    Next

If ClipboardPreData <> "" Then
   ' Dim byteArray As String
   ' byteArray = System.Text.Encoding.UTF8.GetString(byteArray)

    ClipboardData.SetText ClipboardPreData
    ClipboardData.PutInClipboard 'put the data in ClipboardData to the clipboard

        Beep
        MsgBox G1 & " códigos foram copiados para o seu clipboard!", Title:="Operação finalizada"

Else
    MsgBox "Não há dados para importar para o clipboard"
End If

Application.ScreenUpdating = True
End Sub

Sub DataValidationActionStart()
'
'
'

'

    DataValidation bvFEMainData:=True

End Sub

Sub sbLockItens()
'
' This button will set the table with the items inside the asking, so the system can check if the next is the same as the before
'

'
Application.EnableEvents = False
Application.Calculation = xlCalculationManual
DashBoardD_FE.Unprotect

    If Range("B11").Value Then
        Range("B11").Value = "FALSE"
        ActiveSheet.Shapes.Range(Array("LockUnlockItens")).TextFrame.Characters.Text = "Travar Itens"

    Else
        Range("B11").Value = "TRUE"
        ActiveSheet.Shapes.Range(Array("LockUnlockItens")).TextFrame.Characters.Text = "Destravar Itens"

        'Cleaning current data in the table
        DashBoardD_FE.Range("SupTbLongCacheSKU").ClearContents
        DashBoardD_FE.ListObjects("SupTbLongCacheSKU").Resize Intersect(Range("SupTbLongCacheSKU[#all]"), Range(Range("SupTbLongCacheSKU").Row & ":" & Range("SupTbLongCacheSKU").Row - 1))

Dim RowCount(1) As Integer
        RowCount(1) = Range("SupTbLongCacheSKU").Row

        For Each SKU In Range("DSBDProdutosID[SKU]")
            Cells(RowCount(1), Range("SupTbLongCacheSKU").Column).Value = SKU.Value & "-" & Cells(SKU.Row, Range("DSBDProdutosID[Quantidade]").Column).Value

            RowCount(1) = RowCount(1) + 1
        Next

    End If

Application.EnableEvents = True
Application.Calculation = xlCalculationAutomatic
DashBoardD_FE.Protect

End Sub
Sub ResetWhiteBeepCounter()
'
' This button will reset the counter on DashBoardD_FE for the cell "White" responsible to set code as "enviar" on the WaitingInLine
'

'
    DashBoardD_FE.Unprotect
    Application.EnableEvents = False
        DashBoardD_FE.Range("M10").Value = 0

    Application.EnableEvents = True
    DashBoardD_FE.Protect
End Sub


```

## CrossModules

```visual-basic
Global TbCP_MainDataColumnsNumb(1 To 7) As Integer 'Update and save for all modules use the table TbCP_MainData columns number
Global TbFEMainDataColumnsNumb(1 To 18) As Integer 'Update and save for all modules use the table TbFEMainData columns number
Global FEMainDataCounterERROS(1 To 6) As Integer

Sub CheckProductsOut()
'
' This will check the products. When we beep it at "Dashboard dedicado" it will set the status column at "Fila de espera" as "enviar"
'

'

Application.ScreenUpdating = False

'Update the tables columns numb
SetTableColumnsCurrentNumb

Dim FindingMatching As Range

        With Range("TbFEMainData[Número de rastreamento]")
Set FindingMatching = .Find(DashBoardD_FE.Range("F12").Value, LookIn:=xlValues, MatchCase:=True)

            If Not FindingMatching Is Nothing Then  'check if i have already scan the code
                If _
                    DashBoardD_FE.Range("E12").Value = "Enviar" And _
                    (WaitingInLine.Cells(FindingMatching.Row, TbFEMainDataColumnsNumb(10)).Value = "Enviar" Or _
                    WaitingInLine.Cells(FindingMatching.Row, TbFEMainDataColumnsNumb(10)) = "Cadastrar") _
                    Then

                    Beep
                    Application.Speech.Speak "It's already scanned"
                    'MsgBox "Você já escaneou esse código de barras para envio!", Title:="ERRO de Duplicata"

                    'Set the cell each find the products
                    DashBoardD_FE.Range("F13").Value = _
                    WaitingInLine.Cells(Range("TbFEMainData[Número de rastreamento]").Find(DashBoardD_FE.Range("F12").Value, LookIn:=xlValues, MatchCase:=True).Row, TbFEMainDataColumnsNumb(2)).Value

                    'Range("Y8").Value = Range("TbFEMainData[Número de rastreamento]").Find(Range("Y7").Value, LookIn:=xlValues, MatchCase:=True).Offset(, 1).Value
                Else
                    'In case we print an order that had been send already, the system will see it, and alert us
                    If WaitingInLine.Cells(FindingMatching.Row, TbFEMainDataColumnsNumb(10)).Value = "Enviado" And DashBoardD_FE.Range("E12").Value = "Enviar" Then

                        Beep
                        Application.Speech.Speak "Duplicated item"
                        MsgBox "Este item está configurado como ENVIADO - integridade do sistema comprometida. " & Chr(13) & Chr(13) & _
                        "É necessário identificar a fonte do erro", Title:="ERRO CRÍTICO de Duplicata"

                    ElseIf WaitingInLine.Cells(FindingMatching.Row, TbFEMainDataColumnsNumb(10)).Value = "Cancelado" Then

                        Beep
                        Application.Speech.Speak "Cancelled item"
                        MsgBox "Este item está configurado como CANCELADO. " & Chr(13) & Chr(13) & _
                        "Remova o item da pilha de envio", Title:="Item Cancelado"

                    ElseIf DashBoardD_FE.Range("E12").Value <> "Enviar" Then
                        WaitingInLine.Cells(FindingMatching.Row, TbFEMainDataColumnsNumb(10)).Value = DashBoardD_FE.Range("E12").Value

                        DashBoardD_FE.Range("M10").Value = DashBoardD_FE.Range("M10").Value + 1

                    Else

                        WaitingInLine.Cells(FindingMatching.Row, TbFEMainDataColumnsNumb(10)).Value = "Enviar"

                        DashBoardD_FE.Range("M10").Value = DashBoardD_FE.Range("M10").Value + 1
                        Beep
                        Beep
                    End If

                    'Set the cell each find the products
                        DashBoardD_FE.Range("F13").Value = _
                        WaitingInLine.Cells(Range("TbFEMainData[Número de rastreamento]").Find(DashBoardD_FE.Range("F12").Value, LookIn:=xlValues, MatchCase:=True).Row, TbFEMainDataColumnsNumb(2)).Value
                End If
            Else

Dim G1 As Integer

                'Find the free line to add the data
                If _
                    IsEmpty(WaitingInLine.Range("TbFEMainData[ID do pedido]")) And _
                    IsEmpty(WaitingInLine.Range("TbFEMainData[Número de rastreamento]")) _
                    Then

                    G1 = 8

                Else
                    G1 = WaitingInLine.Range("TbFEMainData[ID do pedido]").Rows.Count + 8 'free cell at table TbFEMainData
                End If

                If Mid(DashBoardD_FE.Range("F12").Value, 1, 2) = "BR" Or Mid(DashBoardD_FE.Range("F12"), 12, 13) = "BR" Then 'check if the code is or not correct

                    WaitingInLine.Cells(G1, TbFEMainDataColumnsNumb(1)).Value = DashBoardD_FE.Range("F12").Value
                    WaitingInLine.Cells(G1, TbFEMainDataColumnsNumb(10)).Value = "Cadastrar"

                    'Set the cell each find the products
                    DashBoardD_FE.Range("F13").Value = _
                    WaitingInLine.Cells(Range("TbFEMainData[Número de rastreamento]").Find(DashBoardD_FE.Range("F12").Value, LookIn:=xlValues, MatchCase:=True).Row, TbFEMainDataColumnsNumb(2)).Value

                Else
                    Beep
                    Application.Speech.Speak "Code not recognized"
                    MsgBox "Este código não é reconhecido como um número de rastreio", Title:="Arquitetura do código não é reconhecida"

                End If

            End If
        End With

        If Range("B11") Then 'This will trigger the Block item checking
            fnCheckingIfEqualItens bvMsgBox:=True

        End If


Application.ScreenUpdating = True
End Sub
Sub FindProductsInPack()
'
' Find the ID from the "Dashboard dedicado" into "Fila de espera" and bring up the info.
'

'
Application.ScreenUpdating = False
Application.EnableEvents = False
Application.Calculation = xlCalculationManual

DashBoardD_FE.Activate

'Update the tables columns numb
SetTableColumnsCurrentNumb

Dim FindingMatching As Range

    With Range("TbCP_MainData[FK_ID Do pedido]")
Set FindingMatching = .Find(DashBoardD_FE.Range("F13").Value, LookIn:=xlValues, MatchCase:=True)

        If Not FindingMatching Is Nothing Then

Dim G1(1 To 3) As Integer 'count for FindingMatching
    G1(1) = FindingMatching.Row 'Save the first finding
    G1(3) = 0 'how many time it ran

            'Clean the products that were there before
            DashBoardD_FE.Range("DSBDProdutosID").ClearContents
            DashBoardD_FE.ListObjects("DSBDProdutosID").Resize Range("$I$12:$L$13")

            'Sometimes that item has some observations or notes, this will check out for it and tells us about it
            If WaitingInLine.Cells(FindingMatching.Row, TbCP_MainDataColumnsNumb(6)).Value <> "" Then
                Application.Speech.Speak "Client note"
                MsgBox "Este item tem uma nota do comprador!" & Chr(13) & Chr(13) & ">> " & _
                WaitingInLine.Cells(FindingMatching.Row, TbCP_MainDataColumnsNumb(6)).Value, Title:="Nota do comprador"


            ElseIf WaitingInLine.Cells(FindingMatching.Row, TbCP_MainDataColumnsNumb(7)).Value <> "" Then
                MsgBox "Este item possui uma nota!" & Chr(13) & Chr(13) & ">> " & _
                WaitingInLine.Cells(FindingMatching.Row, TbCP_MainDataColumnsNumb(7)).Value, Title:="Nota"
                 Application.Speech.Speak "System note"

            End If


            Do
                DashBoardD_FE.Range("J" & 13 + G1(3)).Value = WaitingInLine.Cells(FindingMatching.Row, TbCP_MainDataColumnsNumb(2)).Value 'SKU
                DashBoardD_FE.Range("K" & 13 + G1(3)).Value = WaitingInLine.Cells(FindingMatching.Row, TbCP_MainDataColumnsNumb(5)).Value 'Valume

                DashBoardD_FE.Range("I10").Copy
                DashBoardD_FE.Range("I" & G1(3) + 13).PasteSpecial (xlPasteFormulas)
                Application.CutCopyMode = False

                DashBoardD_FE.Range("L10").Copy
                DashBoardD_FE.Range("L" & G1(3) + 13).PasteSpecial (xlPasteFormulas)
                Application.CutCopyMode = False

                G1(3) = G1(3) + 1

                Set FindingMatching = .FindNext(FindingMatching)

                G1(2) = FindingMatching.Row

            Loop While G1(2) <> G1(1)
        Beep
        Beep

        End If

    End With

Application.EnableEvents = True
Application.Calculation = xlCalculationAutomatic
Application.ScreenUpdating = True
End Sub
Sub SetTableColumnsCurrentNumb() 'Saving all the columns for the tables

'TbFEMainData
    'TbFEMainData
    TbFEMainDataColumnsNumb(1) = Range("TbFEMainData[Número de rastreamento]").Column
    TbFEMainDataColumnsNumb(2) = Range("TbFEMainData[ID do pedido]").Column
    TbFEMainDataColumnsNumb(3) = Range("TbFEMainData[Hora do pagamento do pedido]").Column
    TbFEMainDataColumnsNumb(4) = Range("TbFEMainData[Peso bruto do pedido]").Column
    TbFEMainDataColumnsNumb(5) = Range("TbFEMainData[Valor total]").Column
    TbFEMainDataColumnsNumb(6) = Range("TbFEMainData[Total global]").Column
    TbFEMainDataColumnsNumb(7) = Range("TbFEMainData[frete estimado]").Column
    TbFEMainDataColumnsNumb(8) = Range("TbFEMainData[CPF do comprador]").Column
    TbFEMainDataColumnsNumb(9) = Range("TbFEMainData[CEP]").Column
    TbFEMainDataColumnsNumb(10) = Range("TbFEMainData[Status]").Column
    TbFEMainDataColumnsNumb(11) = Range("TbFEMainData[Transportadora]").Column
    TbFEMainDataColumnsNumb(12) = Range("TbFEMainData[Comissão]").Column
    TbFEMainDataColumnsNumb(13) = Range("TbFEMainData[Frete Pago]").Column
    TbFEMainDataColumnsNumb(14) = Range("TbFEMainData[Sup_Beep]").Column
    TbFEMainDataColumnsNumb(15) = Range("TbFEMainData[Taxa de serviço]").Column
    TbFEMainDataColumnsNumb(16) = Range("TbFEMainData[Retorno do pedido]").Column
    TbFEMainDataColumnsNumb(17) = Range("TbFEMainData[Cupons]").Column
    TbFEMainDataColumnsNumb(18) = Range("TbFEMainData[Hora de Criação do Pedido (CP)]").Column

    'TbCP_MainData
    TbCP_MainDataColumnsNumb(1) = Range("TbCP_MainData[FK_ID Do pedido]").Column
    TbCP_MainDataColumnsNumb(2) = Range("TbCP_MainData[SKU]").Column
    TbCP_MainDataColumnsNumb(3) = Range("TbCP_MainData[Preço Original]").Column
    TbCP_MainDataColumnsNumb(4) = Range("TbCP_MainData[Preço Acordado]").Column
    TbCP_MainDataColumnsNumb(5) = Range("TbCP_MainData[Quantidade]").Column
    TbCP_MainDataColumnsNumb(6) = Range("TbCP_MainData[Observação do comprador]").Column
    TbCP_MainDataColumnsNumb(7) = Range("TbCP_MainData[Nota]").Column

End Sub
Sub DataValidation(ByVal bvFEMainData As Boolean, Optional ByVal bvMsgBox As Boolean = True)
'
' This app will check if the data we are about to send is valid
'

'
Application.ScreenUpdating = False
'D1 Errors on FEMainData
'D2 Errors on CPMainData
'DxDy Type of errors for each Dx

    If bvFEMainData Then ' <D1>
        If WorksheetFunction.Sum(Range("5:5")) <> 0 Then 'check the common mistakes <1>
            FEMainDataCounterERROS(1) = FEMainDataCounterERROS(1) + 1

        End If

DBConnect bvWaitingInLine:=True

Dim CheckingID As ADODB.Recordset

        For Each IDcell In Range("TbFEMainData[ID do pedido]") 'check if there's an duplicated ID <2>
            Set CheckingID = New ADODB.Recordset
            CheckingID.Open "SELECT ID_FEMainData FROM FEMainData WHERE ID_FEMainData = """ & IDcell.Value & """", DBConnectionToWaitingInLine

            If Not CheckingID.EOF Then
                FEMainDataCounterERROS(2) = FEMainDataCounterERROS(2) + 1

            End If

            Set CheckingID = Nothing
        Next

        For Each BRCell In Range("TbFEMainData[Número de rastreamento]")  'check if there's an duplicated mail code <3>
            Set CheckingID = New ADODB.Recordset
            CheckingID.Open "SELECT TrackerNumber_FEMainData FROM FEMainData WHERE TrackerNumber_FEMainData = """ & BRCell.Value & """", DBConnectionToWaitingInLine

            If Not CheckingID.EOF Then
                FEMainDataCounterERROS(3) = FEMainDataCounterERROS(3) + 1

            End If

            Set CheckingID = Nothing
        Next

        For Each StatusCell In Range("TbFEMainData[Status]")
            If StatusCell.Value = "Impresso" Then
                FEMainDataCounterERROS(4) = FEMainDataCounterERROS(4) + 1

            ElseIf StatusCell.Value = "Empacotar" Then
                FEMainDataCounterERROS(6) = FEMainDataCounterERROS(6) + 1

            ElseIf StatusCell.Value = "Enviar" Then
                FEMainDataCounterERROS(5) = FEMainDataCounterERROS(5) + 1

            End If
        Next

        If WorksheetFunction.Sum(FEMainDataCounterERROS()) <> 0 And bvMsgBox Then
            MsgBox "Foram identificado falhas na integridade do sistema" & Chr(10) & Chr(10) & _
                "R. Inputs gerais: " & FEMainDataCounterERROS(1) & Chr(10) & _
                "R. Duplicatas ID: " & FEMainDataCounterERROS(2) & Chr(10) & _
                "R. Duplicatas BR: " & FEMainDataCounterERROS(3) & Chr(10) & _
                "R. Status Impresso precisa ser atualizados: " & FEMainDataCounterERROS(4) & Chr(10) & _
                "R. Status Empacotar precis ser atualizado: " & FEMainDataCounterERROS(6) & Chr(10) & _
                "R. Status Enviar precisa ser atualizado: " & FEMainDataCounterERROS(5), vbCritical, "Relatório de integridade de dados"

        ElseIf bvMsgBox Then
            MsgBox "Não foram encontrados erros de integridade do sistema", Title:="Relatório de integridade de dados"

        End If

DBDisconnect bvWaitingInLine:=True

    End If

Application.ScreenUpdating = True
End Sub
Public Function PackingList(Titles As Range) As Boolean
'
' This function will check the PackingList structure and return true or false
'

'

'Columns name settings
Dim ColumnName(1 To 5) As String
    'ColumnName(1) = "Número de rastreamento"
    'ColumnName(2) = "ID do pedido"
    'ColumnName(3) = "Informações do produto"
    'ColumnName(4) = "Observação do comprador"
    'ColumnName(5) = "Nota"
    ColumnName(1) = "tracking_number"
    ColumnName(2) = "order_sn"
    ColumnName(3) = "product_info"
    ColumnName(4) = "remark_from_buyer"
    ColumnName(5) = "seller_note"

    PackingList = True

    For TitleNum = 1 To 5

        If Not Titles(TitleNum) = ColumnName(TitleNum) Then
            PackingList = False

        End If

    Next TitleNum

End Function
Public Function OrderToShip(Titles As Range) As Boolean
'
' This function will check the OrderToShip structure and return true or false
'

'

'Columns name settings
Dim ColumnName(1 To 56) As String
    ColumnName(1) = "ID do pedido"
    ColumnName(2) = "Status do pedido"
    ColumnName(3) = "Status da Devolução / Reembolso"
    ColumnName(4) = "Número de rastreamento"
    ColumnName(5) = "Opção de envio"
    ColumnName(6) = "Método de envio"
    ColumnName(7) = "Data prevista de envio"
    ColumnName(8) = "Tempo de Envio"
    ColumnName(9) = "Data de criação do pedido"
    ColumnName(10) = "Hora do pagamento do pedido"
    ColumnName(11) = "Nº de referência do SKU principal"
    ColumnName(12) = "Nome do Produto"
    ColumnName(13) = "Número de referência SKU"
    ColumnName(14) = "Nome da variação"
    ColumnName(15) = "Preço original"
    ColumnName(16) = "Preço acordado"
    ColumnName(17) = "Quantidade"
    ColumnName(18) = "Subtotal do produto"
    ColumnName(19) = "Desconto do vendedor"
    ColumnName(20) = "Desconto do vendedor"
    ColumnName(21) = "Reembolso Shopee"
    ColumnName(22) = "Peso total SKU"
    ColumnName(23) = "Número de produtos pedidos"
    ColumnName(24) = "Peso total do pedido"
    ColumnName(25) = "Código do Cupom"
    ColumnName(26) = "Cupom do vendedor"
    ColumnName(27) = "Seller Absorbed Coin Cashback"
    ColumnName(28) = "Cupom Shopee"
    ColumnName(29) = "Indicador da Leve Mais por Menos"
    ColumnName(30) = "Desconto Shopee da Leve Mais por Menos"
    ColumnName(31) = "Desconto da Leve Mais por Menos do vendedor"
    ColumnName(32) = "Compensar Moedas Shopee"
    ColumnName(33) = "Total descontado Cartão de Crédito"
    ColumnName(34) = "Valor Total"
    ColumnName(35) = "Taxa de envio pagas pelo comprador"
    ColumnName(36) = "Desconto de Frete Aproximado"
    ColumnName(37) = "Taxa de Envio Reversa"
    ColumnName(38) = "Taxa de transação"
    ColumnName(39) = "Taxa de comissão"
    ColumnName(40) = "Taxa de serviço"
    ColumnName(41) = "Total global"
    ColumnName(42) = "Valor estimado do frete"
    ColumnName(43) = "Nome de usuário (comprador)"
    ColumnName(44) = "Nome do destinatário"
    ColumnName(45) = "Telefone"
    ColumnName(46) = "CPF do Comprador"
    ColumnName(47) = "Endereço de entrega"
    ColumnName(48) = "Cidade"
    ColumnName(49) = "Bairro"
    ColumnName(50) = "Cidade"
    ColumnName(51) = "UF"
    ColumnName(52) = "País"
    ColumnName(53) = "CEP"
    ColumnName(54) = "Observação do comprador"
    ColumnName(55) = "Hora completa do pedido"
    ColumnName(56) = "Nota"


    OrderToShip = True

    For TitleNum = 1 To 56

        If Not Titles(TitleNum) = ColumnName(TitleNum) Then
            OrderToShip = False

        End If

    Next TitleNum

End Function

```

## DataBase - not finished

```visual-basic
Global DBConnectionToWaitingInLine As ADODB.Connection 'save the connection path

Sub DBConnect(ByVal bvWaitingInLine As Boolean)
'
' This will open a connection with the database
'

'
    If bvWaitingInLine Then

Set DBConnectionToWaitingInLine = New ADODB.Connection

Dim PathToDB_Alpha(1 To 2) As String  'save the path to the database, so we don't need repeat it
        'PathToDB_Alpha(1) = "#########################\Banco de dados\BD_WaitingInLine - Copy.accdb"
        PathToDB_Alpha(1) = "####################\BD_WaitingInLine - Copy.accdb"
        PathToDB_Alpha(2) = "Provider=Microsoft.ACE.OLEDB.12.0; Data Source =" & PathToDB_Alpha(1) & "; Persist Security Info=False" ';Jet Oledb:DataBase password=ff123"

        DBConnectionToWaitingInLine.Open PathToDB_Alpha(2) 'start our connection with the database
    End If

End Sub

Sub DBDisconnect(ByVal bvWaitingInLine As Boolean)
'
' This will close the connection with the database
'

'
    If bvWaitingInLine Then
        If Not DBConnectionToWaitingInLine Is Nothing Then 'check if the connection is open, and if it is, it is close and the memory cleaned
            DBConnectionToWaitingInLine.Close
            Set DBConnectionToWaitingInLine = Nothing

        End If
    End If

End Sub

Sub FEMainDataInsert()
'
' This app will get the data from the table and send it to the database
'

'
DBConnect bvWaitingInLine:=True

    DBConnectionToWaitingInLine.Execute "INSERT INTO FEMainData (TrackerNumber_FEMainData, IDAsking_FEMainData, AskingBuyingTime_FEMainData, GrosssWeight_FEMainData," & _
        "TotalPrice_FEMainData, GlobalPrice_FEMainData, Commission_FEMainData, ShippingCalculated_FEMainData, ShippingPaid_FEMainData, ClientID_FEMainData, CEP_FEMainData," * _
        "Status_FEMainData)" & _
        "VALUES(" & x & ")"

DBDisconnect bvWaitingInLine:=True

End Sub


```

## Functions

```visual-basic
Public Function CleanSettings()
'
' This function will clean all the classic settings we used in the functions
'

'
Application.ScreenUpdating = True
Application.Calculation = xlCalculationAutomatic
Application.StatusBar = ""


End Function

Publ Function fnCheckingIfEqualItens(Optional bvMsgBox As Boolean) As Boolean
'
' This Function will return true or false if the locking itens at SupTbLongCacheSKU are the same as the table DSBDProdutosID
'

'
Application.ScreenUpdating = False
fnCheckingIfEqualItens = True

    If WorksheetFunction.CountA(Range("SupTbLongCacheSKU[Long Cache SKU]")) <> WorksheetFunction.CountA(Range("DSBDProdutosID[SKU]")) Then
        GoTo SetasFalse

    Else

        Dim AllSKU As String
        Dim Position As Integer 'just cause we need save it to use .find

            'Getting all the SKU into a single Variable
            For Each SKU In Range("DSBDProdutosID[SKU]")
                AllSKU = AllSKU & SKU.Value & "-" & Cells(SKU.Row, Range("DSBDProdutosID[Quantidade]").Column).Value & "; "

            Next

            On Error GoTo SetasFalse

            For Each SavedSKU In Range("SupTbLongCacheSKU[Long Cache SKU]")
                Position = WorksheetFunction.Find(SavedSKU.Value, AllSKU, 1)

            Next

            On Error GoTo 0
    End If

Application.ScreenUpdating = True

Exit Function
SetasFalse:
    fnCheckingIfEqualItens = False

    Beep
    Application.Speech.Speak "different item"

    If bvMsgBox Then
        MsgBox "Item beepado não corresponde ao item travado", vbInformation, "Item Diferente!"

    End If

Application.ScreenUpdating = True

End Function



```

## In Sheet Events

### DashBoardD_FE

```visual-basic
Private Sub Worksheet_Change(ByVal Target As Range)
    If Target.Address = Range("F12").Address Then 'Check out products as "Enviados"
        If Target.Value <> "" Then

DashBoardD_FE.Unprotect
            DashBoardD_FE.Range("L11").Value = "" 'clean the beep cell

            CheckProductsOut

            'Get cell ready for next
            Target.Value = ""
            Range(Target.Address).Select


DashBoardD_FE.Protect
        End If

'
' new app
'

    ElseIf Target.Address = Range("F14").Address Then 'Just set and start FindProductsInPack

'Update the columns numb
SetTableColumnsCurrentNumb

DashBoardD_FE.Unprotect

Dim FindingMatching As Range
    Set FindingMatching = WaitingInLine.Range("TbFEMainData[Número de rastreamento]").Find(DashBoardD_FE.Range("F14").Value, LookIn:=xlValues, MatchCase:=True)

Application.ScreenUpdating = False
        If Not FindingMatching Is Nothing Then
            If WaitingInLine.Cells(FindingMatching.Row, TbFEMainDataColumnsNumb(14)).Value = 1 Then
                DashBoardD_FE.Range("L11").Value = "Beep"
                DashBoardD_FE.Range("N10").Value = DashBoardD_FE.Range("N10").Value - 1
            Else
                WaitingInLine.Cells(FindingMatching.Row, TbFEMainDataColumnsNumb(14)).Value = 1
                DashBoardD_FE.Range("L11").Value = ""
            End If

            DashBoardD_FE.Range("N10").Value = DashBoardD_FE.Range("N10").Value + 1
            DashBoardD_FE.Range("F13").Value = WaitingInLine.Cells(FindingMatching.Row, TbFEMainDataColumnsNumb(2)).Value

        Else
            DashBoardD_FE.Range("F13").Value = ""

            Beep
            Application.Speech.Speak "Not found"
            MsgBox "Este valor não está cadastrado no sistema", Title:="Código não encontrado"
        End If

        If Range("B11") Then 'This will trigger the block item check
            fnCheckingIfEqualItens

        End If

        DashBoardD_FE.Range("F14").Select

Application.ScreenUpdating = True

DashBoardD_FE.Protect


'
' new app
'
    ElseIf Target.Address = Range("F13").Address Then
DashBoardD_FE.Unprotect

        FindProductsInPack

DashBoardD_FE.Protect
    End If


End Sub


```

### WaitingInLine

```visual-basic
Private Sub Worksheet_BeforeDoubleClick(ByVal Target As Range, Cancel As Boolean)


    '
    ' This code must at a double click on an ID or a items status on TbFE main data, send to de dashboard to see details
    '

    If Not Intersect(Target, Range("TbFEMainData[ID do pedido]")) Is Nothing Or Not Intersect(Target, Range("TbFEMainData[Status]")) Is Nothing Then
        DashBoardD_FE.Unprotect

            'get the column number
            SetTableColumnsCurrentNumb

            'Activate the window
            DashBoardD_FE.Activate

            'Apply the value
            DashBoardD_FE.Range("F13").Value = WaitingInLine.Cells(Target.Row, TbFEMainDataColumnsNumb(2)).Value

        DashBoardD_FE.Protect
    End If

End Sub



```

## Try out of new version

```visual-basic
Sub GetDataFromOtherToShipBR2()
'
' This a try out module - testing efficiency with recordset instead old version
' p.s. better finish this after doing the other ERPM as it works fine

'
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual

'Update the table columns numb
SetTableColumnsCurrentNumb

Dim PathToOrderToShip As FileDialog
    'Setting the filedialong
    Set PathToOrderToShip = Application.FileDialog(msoFileDialogFilePicker)
    With PathToOrderToShip
        .InitialFileName = "A:\gabri\Desktop\Baixados" 'Update to get anyones desktop
        .AllowMultiSelect = False
        .Filters.Add "Arquivos compativeis", "*.xlsx", 1
        .Title = "Escolha o arquivo OrderToShipe >> Da Shopee <<"
    End With

Dim WorkBooksNames(1 To 2) As Workbook 'will save workbook names to switch between them while check data. It will be defined right before switch
    Set WorkBooksNames(1) = ActiveWorkbook 'saving workbook

        'getting the path if not empty
        If PathToOrderToShip.Show = -1 Then
        'WorkingOnData
            'Sorting the data
            Workbooks.Open (PathToOrderToShip.SelectedItems(1))
    Set WorkBooksNames(2) = ActiveWorkbook 'saving workbook
            'Checking the data
            'If OrderToShip(Range("A1:BD1")) And _
                WorksheetFunction.CountA(Rows(1)) = 56 _
                Then
            If 1 = 1 Then

                'Activing database
                GetTablesToRecordset Address:=WorkBooksNames(2).FullName

Dim StoringTable As Range
    Set StoringTable = Range("A1").CurrentRegion

    With ActiveWorkbook.Sheets(1).Sort
        .SortFields.Clear
        .SortFields.Add StoringTable.Columns(4), xlSortOnValues, xlDescending
        .SetRange StoringTable
        .Header = xlYes
        .Apply
    End With

                'getting the collumn address

Dim AddressToEmptyValues As Integer

                If Range("D" & Range("A1").CurrentRegion.Rows.Count).Value <> "" Then 'check if the collumn is not full empty so the next loop will not be infinit
                    AddressToEmptyValues = Range("A1").CurrentRegion.Rows.Count

                    GoTo NextStep

                Else

                    Range("D2").Select

                    'do not update this, the "" cells ARE NOT empty! cannot use the empty function
                    While ActiveCell.Value <> ""
                        If ActiveCell.Offset(1).Value <> "" Then
                            ActiveCell.Offset(1, 0).Select

                        Else
                            AddressToEmptyValues = ActiveCell.Row

                            GoTo NextStep

                        End If
                    Wend
                End If

            Else
                Beep
                MsgBox "A arquitetura do documento não corresponde a arquitetura da programação!", Title:="Erro de arquitetura"

            End If

        'if empty AND agreed to try select file again
        ElseIf MsgBox("Nenhum arquivo foi escolhido, deseja voltar a seleção?", vbYesNo, "NENHUM arquivo selecionado") = 6 Then
            GetDataFromOtherToShipBR
        Else
            Exit Sub
        End If

'For some reason when u don't select a file and then select a file, the code runs well but jump out the if and run "NextSetp"
'To make sure "NextStep" will not run at all unless it is called, exit sub was also added here
Exit Sub
NextStep:
'
' The next step is a demo version, needs to be adapted for each needed case! Do not run it without checking rules
' OBS: The values we want to repeat for each found ID, if it hasn’t, would be need an accumulation

'
Dim StatusBarCounter(1 To 2) As Integer

    With WaitingInLine
        Application.Wait (Now() + TimeValue("00:00:15"))
        WorkBooksNames(1).Activate
        StatusBarCounter(2) = .Range("TbFEMainData[ID do pedido]").Count

        For Each ID In .Range("TbFEMainData[ID do pedido]")

        QrOrdemReport.Filter = "[ID do pedido] = " & ID.Value & ""

            If QrOrdemReport.RecordCount > 0 Then
                QrOrdemReport.MoveFirst

                'Taxa de serviço
                .Cells(ID.Row, TbFEMainDataColumnsNumb(15)).Value = QrOrdemReport.Fields("Taxa de serviço").Value

                'Cupons
                .Cells(ID.Row, TbFEMainDataColumnsNumb(17)).Value = QrOrdemReport.Fields("Cupom do vendedor").Value
            End If

        StatusBarCounter(1) = StatusBarCounter(1) + 1
        Application.StatusBar = StatusBarCounter(1) & " of " & StatusBarCounter(2)
        Next

    End With

    WorkBooksNames(2).Close SaveChanges:=False

    Application.ScreenUpdating = True



    Application.Calculation = xlCalculationAutomatic

    Application.StatusBar = ""

    WBConnectionDesconect
End Sub


```



```visual-basic
Global QrAntecipaReport As ADODB.Recordset
Global QrOrdemReport As ADODB.Recordset

Global WBConnection As ADODB.Connection

Sub GetTablesToRecordset(Address As String)
'
' This code will get the tables in this workbook and put that in a record set
'

'
    'Setting and starting the database
    Set WBConnection = New ADODB.Connection

    WBConnection.Open "Provider=Microsoft.ACE.OLEDB.12.0;Data Source=" & _
        Address & _
        ";Extended Properties=""Excel 12.0 Xml;HDR=YES"";"

        Set QrOrdemReport = New ADODB.Recordset

        QrOrdemReport.Open "SELECT * FROM [" & "Relatório de ordem" & "$]", WBConnection, adOpenStatic, adLockBatchOptimistic


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



```visual-basic
Global QrAntecipaReport As ADODB.Recordset
Global QrOrdemReport As ADODB.Recordset

Global WBConnection As ADODB.Connection

Sub GetTablesToRecordset(Address As String)
'
' This code will get the tables in this workbook and put that in a record set
'

'
    'Setting and starting the database
    Set WBConnection = New ADODB.Connection

    WBConnection.Open "Provider=Microsoft.ACE.OLEDB.12.0;Data Source=" & _
        Address & _
        ";Extended Properties=""Excel 12.0 Xml;HDR=YES"";"

        Set QrOrdemReport = New ADODB.Recordset

        QrOrdemReport.Open "SELECT * FROM [" & "Relatório de ordem" & "$]", WBConnection, adOpenStatic, adLockBatchOptimistic


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

