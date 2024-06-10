Option Explicit

Sub ParseSQL()
    Dim sql As String
    Dim selectClause As String
    Dim fromClause As String
    Dim columns As Variant
    Dim column As Variant
    Dim tables As Variant
    Dim table As Variant
    Dim result As String
    Dim i As Integer

    ' Example SQL query
    sql = "SELECT a.col1 AS alias1, b.col2 AS alias2, c.col3 AS alias3 FROM db1.table1 a JOIN db2.table2 b ON a.id = b.id JOIN db3.table3 c ON b.id = c.id"

    ' Extract SELECT and FROM clauses
    selectClause = Trim(Mid(sql, InStr(1, sql, "SELECT ") + 7, InStr(1, sql, "FROM") - InStr(1, sql, "SELECT ") - 7))
    fromClause = Trim(Mid(sql, InStr(1, sql, "FROM ") + 5))

    ' Split columns by comma
    columns = Split(selectClause, ",")

    ' Split tables by JOIN
    tables = Split(fromClause, "JOIN")

    ' Print columns and their aliases
    Debug.Print "Columns and Aliases:"
    For i = LBound(columns) To UBound(columns)
        column = Trim(columns(i))
        If InStr(column, " AS ") > 0 Then
            Debug.Print Mid(column, 1, InStr(column, " AS ") - 1) & " -> " & Mid(column, InStr(column, " AS ") + 4)
        Else
            Debug.Print column
        End If
    Next i

    ' Print tables and their aliases
    Debug.Print vbCrLf & "Tables and Aliases:"
    For i = LBound(tables) To UBound(tables)
        table = Trim(tables(i))
        If InStr(table, " ") > 0 Then
            Debug.Print Mid(table, 1, InStr(table, " ") - 1) & " -> " & Mid(table, InStr(table, " ") + 1)
        Else
            Debug.Print table
        End If
    Next i
End Sub