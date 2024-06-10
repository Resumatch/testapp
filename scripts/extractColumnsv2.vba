Option Explicit

Sub ParseSQL()
    Dim sql As String
    Dim selectClause As String
    Dim fromClause As String
    Dim columns As Variant
    Dim column As Variant
    Dim tables As Variant
    Dim table As Variant
    Dim i As Integer
    Dim rowIndex As Integer

    ' Example SQL query
    sql = "SELECT a.col1 AS alias1, b.col2 AS alias2, c.col3 AS alias3 FROM db1.table1 a JOIN db2.table2 b ON a.id = b.id JOIN db3.table3 c ON b.id = c.id"

    ' Extract SELECT and FROM clauses
    selectClause = Trim(Mid(sql, InStr(1, sql, "SELECT ") + 7, InStr(1, sql, "FROM") - InStr(1, sql, "SELECT ") - 7))
    fromClause = Trim(Mid(sql, InStr(1, sql, "FROM ") + 5))

    ' Split columns by comma
    columns = Split(selectClause, ",")

    ' Split tables by JOIN
    tables = Split(fromClause, "JOIN")

    ' Output to the active worksheet
    rowIndex = 1
    With ActiveSheet
        .Cells(rowIndex, 1).Value = "Columns and Aliases:"
        rowIndex = rowIndex + 1
        For i = LBound(columns) To UBound(columns)
            column = Trim(columns(i))
            If InStr(column, " AS ") > 0 Then
                .Cells(rowIndex, 1).Value = Mid(column, 1, InStr(column, " AS ") - 1)
                .Cells(rowIndex, 2).Value = Mid(column, InStr(column, " AS ") + 4)
            Else
                .Cells(rowIndex, 1).Value = column
            End If
            rowIndex = rowIndex + 1
        Next i

        rowIndex = rowIndex + 1
        .Cells(rowIndex, 1).Value = "Tables and Aliases:"
        rowIndex = rowIndex + 1
        For i = LBound(tables) To UBound(tables)
            table = Trim(tables(i))
            If InStr(table, " ") > 0 Then
                .Cells(rowIndex, 1).Value = Mid(table, 1, InStr(table, " ") - 1)
                .Cells(rowIndex, 2).Value = Mid(table, InStr(table, " ") + 1)
            Else
                .Cells(rowIndex, 1).Value = table
            End If
            rowIndex = rowIndex + 1
        Next i
    End With
End Sub