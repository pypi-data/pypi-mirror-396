from .raw_table_cell import RawTableCell


class RawTableRow:
    def __init__(self):
        self.cells: list[RawTableCell] = []

    def add(self, cell: RawTableCell):
        self.cells.append(cell)

    def find_cell(self, text: str) -> RawTableCell:
        for cell in self.cells:
            if cell.is_text():
                if text.upper() in cell.text().upper():
                    return cell
        return None

    def find_cell_next_to(self, text: str) -> RawTableCell:
        for index, cell in enumerate(self.cells):
            if cell.is_text():
                if text.upper() in cell.text().upper():
                    return self.next_cell(index)
        return None

    def to_html(self):
        lines = []
        lines.append("<tr>")
        for item in self.cells:
            lines.append(item.to_html())
        lines.append("</tr>")
        return ("\n").join(lines)

    def next_cell(self, start_index: int) -> RawTableCell:
        for index, cell in enumerate(self.cells):
            if index > start_index and cell.first:
                return cell
        return None

    def to_dict(self) -> dict:
        """Convert the table row to a dictionary representation"""
        return {"type": "table_row", "cells": [cell.to_dict() for cell in self.cells]}
