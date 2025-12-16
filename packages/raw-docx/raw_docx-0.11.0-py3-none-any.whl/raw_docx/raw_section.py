from .raw_paragraph import RawParagraph
from .raw_list import RawList
from .raw_table import RawTable
from .raw_image import RawImage


class RawSection:
    def __init__(self, title: str | None, number: str | None, level: int):
        self.title = title.strip() if title else title
        self.number = number.strip() if number else number
        self.level = level
        self.items = []

    def add(self, item: RawParagraph | RawList | RawTable | RawImage) -> None:
        self.items.append(item)

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

    def to_dict(self) -> dict:
        """Convert the section to a dictionary representation"""
        return {
            "type": "section",
            "title": self.title,
            "number": self.number,
            "level": self.level,
            "items": [
                item.to_dict() if hasattr(item, "to_dict") else str(item)
                for item in self.items
            ],
        }

    def to_html(self):
        text = []
        for item in self.items:
            result = item.to_html()
            text.append(result)
        return ("\n").join(text)

    def to_html_between(self, start, end):
        text = []
        for index, item in enumerate(self.items):
            if index >= start and index < end:
                result = item.to_html()
                text.append(result)
        return ("\n").join(text)

    def paragraphs(self) -> list[RawParagraph]:
        return [x for x in self.items if isinstance(x, RawParagraph)]

    def tables(self) -> list[RawTable]:
        return [x for x in self.items if isinstance(x, RawTable)]

    def lists(self) -> list[RawList]:
        return [x for x in self.items if isinstance(x, RawList)]

    def items_between(self, start_index, end_index):
        return self.items[start_index:end_index]

    def find(self, text) -> list[RawParagraph]:
        return [x for x in self.items if isinstance(x, RawParagraph) and x.find(text)]

    def find_at_start(self, text) -> list[RawParagraph]:
        return [
            x
            for x in self.items
            if isinstance(x, RawParagraph) and x.find_at_start(text)
        ]

    def find_first_at_start(self, text) -> tuple[RawParagraph, int]:
        for index, item in enumerate(self.items):
            if isinstance(item, RawParagraph) and item.find_at_start(text):
                return item, index
        return None, -1

    def has_lists(self) -> bool:
        return len(self.lists()) > 0

    def has_content(self) -> bool:
        return not self.is_empty()

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def next(self, index: int):
        return self.items[index + 1] if (index + 1) < len(self.items) else None

    def index(self, item: RawParagraph | RawList | RawTable | RawImage) -> int | None:
        return next((i for i, x in enumerate(self.items) if x is item), None)

    def next_paragraph(self, start_index: int) -> RawParagraph:
        for index, item in enumerate(self.items):
            if index >= start_index:
                if isinstance(self.items[index], RawParagraph):
                    return item
        return None

    def next_table(self, start_index: int) -> RawTable:
        for index, item in enumerate(self.items):
            if index >= start_index:
                if isinstance(self.items[index], RawTable):
                    return item
        return None

    def _format_heading(self):
        if self.number and self.title:
            return f"<h{self.level}>{self.number} {self.title}</h{self.level}>"
        elif self.number:
            return f"<h{self.level}>{self.number}</h{self.level}>"
        elif self.title:
            return f"<h{self.level}>{self.title}</h{self.level}>"
        else:
            return ""
