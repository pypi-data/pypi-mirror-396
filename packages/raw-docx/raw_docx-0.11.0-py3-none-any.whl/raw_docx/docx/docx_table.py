from simple_error_log import Errors
from simple_error_log.error_location import KlassMethodLocation
from raw_docx.raw_table import RawTable
from docx.table import _Cell


class TableCell:
    def __init__(
        self,
        row: int,
        col: int,
        bottom: int,
        right: int,
        cell: _Cell,
        h_merge: bool,
        v_merge: bool,
    ):
        self.cell = cell
        self.top = row
        self.bottom = bottom
        self.left = col
        self.right = right
        self.v_merge = v_merge
        self.h_merge = h_merge

    def __str__(self):
        text = ""
        for paragraph in self.cell.paragraphs:
            text += paragraph.text
        return f"[{self.top}, {self.left}] --> [{self.bottom}, {self.right}] (H: {self.h_merge}, V: {self.v_merge}) {text}"


class TableRow:
    def __init__(self, row: int):
        self._row = row
        self._data = []

    def cell(self, col: int) -> TableCell:
        return self._data[col]

    def add(self, col: int, cell: TableCell):
        try:
            self._data[col] = cell
        except IndexError:
            if col >= 0:
                self._data.extend(((col + 1) - len(self._data)) * [None])
                self._data[col] = cell

    def pad(self, width: int):
        if len(self._data) < width:
            self._data.extend((width - len(self._data)) * [None])

    def __iter__(self):
        return iter(self._data)


class TableMatrix:
    MODULE = "raw_docx.docx.docx_table.TableMatrix"

    class LogicError(Exception):
        pass

    def __init__(self, table: RawTable, errors: Errors):
        try:
            self._errors = errors
            self._table = table
            self._height = 0
            self._width = 0
            self._matrix: list[list[TableCell]] = []
            for cell in self._iter_cells():
                self._add(cell)
                self._width = cell.left if cell.left > self._width else self._width
                self._height = cell.top
            self._height += 1  # Set length not index
            self._width += 1  # Set length not index
            self._pad()
        except Exception as e:
            self._errors.exception(
                "Exception raised building table matrix",
                e,
                KlassMethodLocation(self.MODULE, "__init__"),
            )

    def _pad(self):
        row: TableRow
        for row in self._matrix:
            row.pad(self._width)

    def _add(self, cell: TableCell):
        row = cell.top
        col = cell.left
        if row >= 0 and row < len(self._matrix):
            row_data: TableRow = self._matrix[row]
            row_data.add(col, cell)
        elif row >= 0:
            self._matrix.extend(((row + 1) - len(self._matrix)) * [None])
            row_data = TableRow(row)
            self._matrix[row] = row_data
            row_data.add(col, cell)
        else:
            pass  # negative row!

    def _iter_cells(self):
        table = self._table
        for r, row in enumerate(table.rows):
            for c, cell in enumerate(row.cells):
                right = c
                bottom = r
                v_merge = False
                h_merge = False
                # Check if the cell equals the previous cell either horizontally or vertically
                #   so it can be ignored (part of a merge)
                if (
                    r > 0
                    and c < len(table.rows[r - 1].cells)
                    and cell._tc is table.rows[r - 1].cells[c]._tc
                ) or (c > 0 and cell._tc is row.cells[c - 1]._tc):
                    continue
                # Verical merge check
                if (
                    r >= 0
                    and r + 1 < len(table.rows)
                    and c < len(table.rows[r + 1].cells)
                    and cell._tc is table.rows[r + 1].cells[c]._tc
                ):
                    v_merge = True
                    bottom = self._v_extent(r, c) - 1
                # Horizontal merge check
                if (
                    c >= 0
                    and c + 1 < len(table.rows[r].cells)
                    and cell._tc is row.cells[c + 1]._tc
                ):
                    h_merge = True
                    right = self._h_extent(r, c) - 1
                yield TableCell(r, c, bottom, right, cell, h_merge, v_merge)

    def _v_extent(self, row: int, col: int) -> int:
        table = self._table
        next_row = row + 1
        height = len(table.rows)
        while next_row < height:
            if (
                next_row >= 0
                and col < len(table.rows[next_row].cells)
                and table.rows[row].cells[col]._tc
                is not table.rows[next_row].cells[col]._tc
            ):
                return next_row
            else:
                next_row += 1
        return height

    def _h_extent(self, row: int, col: int) -> int:
        table = self._table
        next_col = col + 1
        width = len(table.rows[row].cells)
        while next_col < width:
            if (
                next_col >= 0
                and table.rows[row].cells[col]._tc
                is not table.rows[row].cells[next_col]._tc
            ):
                return next_col
            else:
                next_col += 1
        return width

    def __iter__(self):
        return iter(self._matrix)
