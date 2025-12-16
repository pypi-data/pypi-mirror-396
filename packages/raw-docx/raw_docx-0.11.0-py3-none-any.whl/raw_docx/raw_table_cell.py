from .raw_paragraph import RawParagraph
from .raw_list import RawList
from .raw_table import RawTable


class RawTableCell:
    def __init__(self, h_span: int = 1, v_span: int = 1, first: bool = True):
        self.h_span = h_span
        self.v_span = v_span
        self.h_merged = h_span > 1
        self.v_merged = v_span > 1
        self.merged = self.h_merged or self.v_merged
        self.first = first
        self.items = []

    def add(self, item: RawParagraph | RawList | RawTable) -> None:
        self.items.append(item)

    def is_text(self) -> bool:
        for item in self.items:
            if not isinstance(item, RawParagraph):
                return False
        return True

    def text(self) -> str:
        return ("\n").join([x.text for x in self.items])

    def is_in_list(self) -> bool:
        if self.items:
            if isinstance(self.items[-1], RawList):
                return True
        return False

    def current_list(self) -> RawList:
        if self.items:
            return self.items[-1] if isinstance(self.items[-1], RawList) else None
        else:
            return None

    def to_html(self):
        if not self.first:
            return ""
        lines = []
        colspan = f' colspan="{self.h_span}"' if self.h_merged else ""
        rowspan = f' rowspan="{self.v_span}"' if self.v_merged else ""
        lines.append(f"<td{colspan}{rowspan}>")
        for item in self.items:
            lines.append(item.to_html())
        lines.append("</td>")
        return ("\n").join(lines)

    def to_dict(self) -> dict:
        """Convert the table cell to a dictionary representation"""
        return {
            "type": "table_cell",
            "row_span": self.v_span,
            "col_span": self.h_span,
            "first": self.first,
            "content": [
                item.to_dict() if hasattr(item, "to_dict") else str(item)
                for item in self.items
            ],
        }
