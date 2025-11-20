def format_currency(value: float) -> str:
    return f"${value:,.2f}"


def print_table(rows, headers):
    """
    Prints a clean aligned table.
    
    rows: list of lists (data)
    headers: list of column titles
    """

    # Determine column widths
    col_widths = []
    for col_index in range(len(headers)):
        header_width = len(headers[col_index])
        column_items = [len(str(row[col_index])) for row in rows]
        max_width = max([header_width] + column_items)
        col_widths.append(max_width)

    # Build horizontal line
    line = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

    # Print header
    print(line)
    header_row = "| " + " | ".join(
        headers[i].ljust(col_widths[i])
        for i in range(len(headers))
    ) + " |"
    print(header_row)
    print(line)

    # Print rows
    for row in rows:
        row_str = "| " + " | ".join(
            str(row[i]).ljust(col_widths[i])
            for i in range(len(row))
        ) + " |"
        print(row_str)

    print(line)
