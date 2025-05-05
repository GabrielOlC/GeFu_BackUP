# File objective

> This file estimates the purchase price of any type of plastic bag and calculates the difference between the estimated and actual units/weight in a pack. It proposes a selling price based on predefined rules and offers unlimited columns for storing personalized prices. Additionally, it includes functions to easily switch calculations to any of those prices, compare competitor prices, and analyze profits for each selected column. The file also generates simple outputs that can be shared with clients in either list or table format. 

### Observations

- [x] Query snippets have been left out. Check the files directly.

- [x] Some Excel functions have been left out. Check the files directly.

## Update notes

- [x] Fazer a tabela aceitar outros nomes de sacos (ao invés de números apenas) **(Facilidade: 5 | Benefício: 5 | GU: 25)**

- [ ] Fazer a tabela comparar automaticamente o preço dos concorrentes **(Facilidade: 1 | Benefício: 5 | GU: 5)**
  
  - [ ] Identificar quais preços cada concorrente teria e qual preço faríamos para cobrir
    - [x] Básico realizado (trazer o valor do concorrente)
    - [ ] Falta adicionar balanços já que nem todos os concorrentes têm pacotes com a mesma quantidade de unidades ou espessura
      - [x] Adicionar balance para unidades
      - [ ] Adicionar balance para peso
      - [ ] Adicionar balance para espessura
  - [ ] Não permitir lucros abaixo da regra e sempre considerar o maior valor
  - [ ] Identificar quais clientes têm quais sacos e fornecedor
  - [x] Gerar uma tabela de preço de venda automática considerando todos esses elementos
    - [ ] PS. quando terminar os outros itens só adicionar a condicional

- [x] Adicionar cálculo de custo dinâmico para cada tipo de saco (cada saco vai ter uma categoria de custo) **(Facilidade: 3 | Benefício: 2 | GU: 6)**

- [ ] Adicionar modelo de cálculo de preço para R$ / unidade de venda **(Facilidade: 2 | Benefício: 3 | GU: 6)**

- [x] Revisar cálculo de unidades (tem alguns que são 20 unidades reais—por que não está como 20?) **(Facilidade: 1 | Benefício: 1 | GU: 1)**
  O fabricante realiza muitos arredondamentos nós cálculos... o que não é um problema já que todos eles estão dentro de uma variação aceitável na espessura e a compra de pacotes de 'und' sempre entrega as unidades prometidas.

- [ ] Melhorar cálculo nas colunas roxas (promoção de lote com valor de compra mínima) **(Facilidade: 3 | Benefício: 1 | GU: 3)**
  
  - [x] Adicionar opção para inserir custos do lote além do frete
  - [ ] Criar uma tabela matriz para escolher o custo a partir de uma matriz padrão

---

# ⚙️VBA

## Buttons

```visual-basic
Sub bt_ChangeTaxValue()
'
' This button will set the tax at a specific value A or B in case A already there
'

'
    Dim vShp As Shape
        Set vShp = ActiveSheet.Shapes(Application.Caller)
    Dim vValueToSet(1 To 2)
        vValueToSet(1) = 0.08
        vValueToSet(2) = 0

    If Range("cnSTotalCustoPct").Value = vValueToSet(1) Then
        vShp.TextFrame2.TextRange.Text = "Tax at " & vValueToSet(2) * 100 & "%"
        Range("cnSTotalCustoPct").Value = vValueToSet(2)
    Else
        vShp.TextFrame2.TextRange.Text = "Tax at " & vValueToSet(1) * 100 & "%"
        Range("cnSTotalCustoPct").Value = vValueToSet(1)
    End If

End Sub

```

## CrossModules

```visual-basic
Function vfHexToRGB(HexColor As String) As Long
'
' This will convert the Hex codes to RGB, Easy picking on color selector with hex
'

'
    Dim r As Long, g As Long, b As Long

    ' Remove the "#" if it's there
    If Left(HexColor, 1) = "#" Then HexColor = Mid(HexColor, 2)

    ' Convert the hex strings to RGB values
    r = Val("&H" & Mid(HexColor, 1, 2))
    g = Val("&H" & Mid(HexColor, 3, 2))
    b = Val("&H" & Mid(HexColor, 5, 2))

    vfHexToRGB = RGB(r, g, b)
End Function
Function vfGetUnion(arr() As Range) As Range
'
' This will merge and return the provided ranges as ranges
'

'
    Dim vRng As Range
        Set vRng = arr(1)

    For i = LBound(arr) + IIf(LBound(arr) = 0, 2, 1) To UBound(arr) 'if checks if we started the arr at 0 to x or 1 to x and apply the correction — we are supossing we leaving 0 to add some special range union or something. So if we have a special range we got 0 to x, if not 1 to x
        Set vRng = Union(vRng, arr(i))

    Next i

    Set vfGetUnion = vRng
End Function

```

## ErrorHandler

```visual-basic
Function vfNamedRangeExists(ByVal bvCellName As String) As Boolean
'
' This checks if the provided cell name exists
'

'
    vfNamedRangeExists = True
    On Error GoTo SetFunction

    Dim vTester As String

    vTester = Range(bvCellName).Value

Exit Function
SetFunction:
    vfNamedRangeExists = False
    MsgBox "The provided range (" & bvCellName & ") doesn't exist, the operation was canceled", vbCritical

End Function

```

## WorksheetFunctions

```visual-basic
Sub vsSetSelectedPrice(ByVal bvCellName As String, ByVal bvValueToSet As Integer, ByVal bvRangeToColor As Range, Optional ByVal bvCellToColor As Range)
    '
    ' This will set the provided cell with the provided value and the column header's color as dark green, _
    If it is already that value, it will set as 0 and column header's color as light green
    '

    '
    If vfNamedRangeExists(bvCellName) Then
        If Range(bvCellName).Value = bvValueToSet Then
            Range(bvCellName).Value = 0
            bvRangeToColor.Interior.Color = vfHexToRGB("#00B050") 'light green

        Else
            Range(bvCellName).Value = bvValueToSet

            If Not bvCellToColor Is Nothing Then
                'Set the headers as light green before setting the dark
                bvRangeToColor.Interior.Color = vfHexToRGB("#00B050") 'light green

                bvCellToColor.Interior.Color = vfHexToRGB("#007A37") 'Dark green

            End If

        End If
    End If

End Sub
```

## In Sheet Events

```visual-basic
Private Sub Worksheet_BeforeDoubleClick(ByVal Target As Range, Cancel As Boolean)

'
' These triggers check a double click on the respective headers and change the settings accordingly (Change the cnSelectPrice to the respective header, some headers change the cnSCompraMinima too)
'

'
    Dim vRng(1 To 8) As Range
        Set vRng(1) = Range("tbPCCalculator[[#Headers],[PV Client Final]]") 'first column, highest price
        Set vRng(2) = Range("tbPCCalculator[[#Headers],[PV Venda em volume]]") 'third column
        Set vRng(3) = Range("tbPCCalculator[[#Headers],[PV Sem compromisso]]") 'second column
        Set vRng(4) = Range("tbPCCalculator[[#Headers],[PV Abatendo concorrentes]]") 'fourth column
        Set vRng(5) = Range("tbPCCalculator[[#Headers],[PV Abatendo concorrentes (sem imposto)]]") 'fifth column, lowest price
        Set vRng(6) = Range("tbPCCalculator[[#Headers],[Pv 10 R$ p/Kg]]")
        Set vRng(7) = Range("tbPCCalculator[[#Headers],[Pv 9.5 R$  p/Kg]]")
        Set vRng(8) = Range("tbPCCalculator[[#Headers],[Pv 9 R$ p/kg]]")

         For i = LBound(vRng) To UBound(vRng)
            If Target.Address = vRng(i).Address Then
                vsSetSelectedPrice _
                    bvCellName:="cnSelectPrice", _
                    bvValueToSet:=i, _
                    bvCellToColor:=Target, _
                    bvRangeToColor:=vfGetUnion(vRng)

                Select Case i
                    Case 2
                        vbSettings.Range("cnSCompraMinima").Value = 500
                    Case 4, 5
                        vbSettings.Range("cnSCompraMinima").Value = 1000
                End Select

                Cancel = True

                Exit For
            End If

        Next i

' ----

End Sub


```

# 🧮Excel Functions

## Automatic Price List

```excel-formula
=LET(
  vConditions,
         ($G8 = tbPCCalculator[Litragem]) *
         (IF($B$5, $C$5, $D$5) = tbPCCalculator[Espessura]) *
         (tbPCCalculator[Und] = 100) *
         ($B$3 = tbPCCalculator[Material]) *
         (tbPCCalculator[Status] = "Ativo"),
  vCountValidConditions, SUMPRODUCT(vConditions),
  vOrigIndex, $B$2 + 1 + N("Set indext to start at 1 as ours starts at 0"),
  vFallBackIndices, IF(vOrigIndex>=2, SEQUENCE(vOrigIndex-1, 1, vOrigIndex, -1),IF(vOrigIndex=1,{1},{0})),
  vCandidateArray,
    MAP(vFallBackIndices,
      LAMBDA(lmIndex,
        IF(lmIndex=0, 0,
           SUMPRODUCT(vConditions, CHOOSE(lmIndex,
             tbPCCalculator[Preço de venda Recomendado],
             tbPCCalculator[PV Client Final],
             tbPCCalculator[PV Sem compromisso],
             tbPCCalculator[PV Venda em volume],
             tbPCCalculator[PV Abatendo concorrentes]
           ))
        )
      )
    ),
  vFirstCandidateEmpty,IF(INDEX(vCandidateArray,1)=0,TRUE,FALSE),
  vValidCandidates, FILTER(vCandidateArray, vCandidateArray<>0,0),
  vResultCandidate, IF(AND(ROWS(vValidCandidates)=1,INDEX(vValidCandidates,1)=0), 0, INDEX(vValidCandidates, 1)),
  IF(vCountValidConditions >= 2, "Err. Unexpected duplicate",
    IF(vCountValidConditions = 0, "",
      IF(vFirstCandidateEmpty,vResultCandidate*-1,vResultCandidate
      )
    )
  )
)
```

## Calculadora de preço

```excel-formula
/* Xlookup a value crossing the calling column and a header option - alternative to use one single datasheet for user fast use.

Needs a integer sup_row as column and sup_column as #totals. Both based on the first column (or the calling column):
    =ROW([@Litragem])-MIN(ROW([Litragem]))+2 (result should represent the rows sequence inside the table)
    =COLUMN()-COLUMN(tbSDimentionBags[[#Headers],[Litragem]])+1 (result should represent the column sequence inside the table)
*/

=INDEX(
  tbSDimentionBags[#All],
  XLOOKUP([@Litragem],tbSDimentionBags[Litragem],tbSDimentionBags[Sup_Row]),
  XLOOKUP([@Material],tbSDimentionBags[#Headers],tbSDimentionBags[#Totals])
)
```



```excel-formula
/* Calculate weight
*/
=IF(lmdCheckEmptyOrZero([@[Peso real]]),
     [@[Peso real]],

     IF(lmdCheckEmptyOrZero([@Und])*lmdCheckEmptyOrZero([@[Peso Tabela]]),
        [@Und]*[@[Peso Tabela]]/1000,

        IF(lmdCheckEmptyOrZero([@Und]),
           ([@Altura]*[@Largura]*[@Espessura]/10000*[@Und])+cnSAcrementoPeso,

           "Err: This scenario wasn't foreseen"
          )
       )
    )
```



```excel-formula
/* Calculate units
*/
=IF(lmdCheckEmptyOrZero([@Und]),
    [@Und],

    IF(lmdCheckEmptyOrZero([@[Peso real]])*lmdCheckEmptyOrZero([@[Peso Tabela]]),
       [@Peso]*1000/[@[Peso Tabela]],

        IF(lmdCheckEmptyOrZero([@[Peso real]]),
           ROUNDDOWN((10*([@Peso]-cnSAcrementoPeso)*1000)/([@Altura]*[@Largura]*[@Espessura]),0),

           "Err: This scenario wasn't foreseen"
          )
      )
    )
```



```excel-formula
/* Bring the competitors selling price. It also balance the prices according to weight and units (yet building)
*/
=IF(NOT(lmdCheckEmptyOrZero([@EAN])),"",
  LET(
    vCompetitor,XLOOKUP(cnSelectCompetitor,tbCDetails[Competitor name],tbCDetails[ID]),
    vCompetitorUnits, SUMPRODUCT(([@EAN]=tbCPrices[FK_ID_tbPCCalculator-EAN])*(vCompetitor=tbCPrices[FK_ID_tbCDetails]),tbCPrices[Units]),
    vCompetitorPrice, SUMPRODUCT(([@EAN]=tbCPrices[FK_ID_tbPCCalculator-EAN])*(vCompetitor=tbCPrices[FK_ID_tbCDetails]),tbCPrices[Value]),
    IF(vCompetitorPrice<>0,
      vCompetitorPrice*[@Unds]/IF(AND(vCompetitorUnits<>0,cnBalanceCompetitorUnits),vCompetitorUnits,[@Unds]),

      LET(
        REM_1,"We have updated above with the 'cnBalanceCompetitorUnits' but we did not here... need do, and also the part of balance weight which is not above either",
        vFKID_tbCPrices,XLOOKUP([@EAN],tbCSimilarPrice[FK_ID_tbPCCalculator-EAN],tbCSimilarPrice[FK_ID_tbCPrices],""),
        vSimilarPrice,SUMPRODUCT((vFKID_tbCPrices=tbCPrices[ID])*(vCompetitor=tbCPrices[FK_ID_tbCDetails]),tbCPrices[Value]),
        IF(vSimilarPrice<>0,vSimilarPrice*-1,"")
      )
    )
  )
)
```

## Name manager

```excel-formula
/* Return true if the value is not empty or 0
*/

name: lmdNotEmptyOrZero -> lmdNEZ
=LAMBDA(Cell,IF(AND(Cell<>0,Cell<>""),TRUE,FALSE))
```

