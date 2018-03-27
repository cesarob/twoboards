
from terminaltables import AsciiTable
from .color import yellow, cyan, colorize_row


def print_table(title, header, rows):
    title = yellow(title)
    header = colorize_row(header, cyan)
    table_rows = [header]
    for row in rows:
        table_rows.append(row)

    table = AsciiTable(table_rows, title=title)
    print(table.table)
    print()
