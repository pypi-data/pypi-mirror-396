import re
from raw_docx.raw_table import RawTable
from raw_docx.raw_paragraph import RawParagraph
from raw_docx.raw_section import RawSection


@staticmethod
def text_within(this_text: str, in_text: str) -> bool:
    clean_text = re.sub(
        "\s+", " ", in_text
    )  # Remove any end of line chars and tabs etc
    return this_text.upper() in clean_text.upper()


@staticmethod
def table_get_row(table: RawTable, key: str) -> str:
    # print(f"\n\nTABLE FIND: {key}")
    for row in table.rows:
        if row.cells[0].is_text():
            # print(f"CELL 0: {row.cells[0].text()}")
            if text_within(key, row.cells[0].text()):
                # print(f"FOUND: {key}")
                cell = row.next_cell(0)
                result = cell.text() if cell else ""
                return result.strip()
    return ""


@staticmethod
def section_get_para(section: RawSection, in_text: str) -> str:
    para: RawParagraph
    for para in section.paragraphs():
        if text_within(in_text, para.text):
            parts = para.text.split(":")
            return (":").join(parts[1:]).strip() if len(parts) >= 2 else ""
    return ""


@staticmethod
def table_get_row_html(table: RawTable, key: str) -> str:
    for row in table.rows:
        if row.cells[0].is_text():
            if text_within(key, row.cells[0].text()):
                cell = row.next_cell(0)
                return cell.to_html() if cell else ""
    return ""
