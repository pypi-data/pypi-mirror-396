from raw_docx.raw_table import RawTable


def text_within(this_text: str, in_text: str) -> bool:
    return this_text.upper() in in_text.upper()


def table_get_row(table: RawTable, key: str) -> str:
    for row in table.rows:
        if row.cells[0].is_text():
            # if row.cells[0].text().upper().startswith(key.upper()):
            if text_within(key, row.cells[0].text()):
                cell = row.next_cell(0)
                result = cell.text() if cell else ""
                return result
    return ""


def table_get_row_html(table: RawTable, key: str) -> str:
    for row in table.rows:
        if row.cells[0].is_text():
            # if row.cells[0].text().upper().startswith(key.upper()):
            if text_within(key, row.cells[0].text()):
                cell = row.next_cell(0)
                return cell.to_html() if cell else ""
    return ""
