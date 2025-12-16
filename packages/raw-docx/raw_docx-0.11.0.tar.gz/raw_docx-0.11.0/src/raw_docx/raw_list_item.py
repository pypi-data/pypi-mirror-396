from .raw_paragraph import RawParagraph
from .raw_run import RawRun


class RawListItem(RawParagraph):
    def __init__(self, runs: list[RawRun], level: int):
        self.level = level
        super().__init__(runs)

    def to_text(self) -> str:
        return f"{'  ' * self.level}{self.text}"

    def to_html(self) -> str:
        return f"{self.text}"
        # return f"{escape(self.text)}"

    def to_dict(self) -> dict:
        return {"type": "list_item", "text": self.text, "level": self.level}

    def __str__(self) -> str:
        return f"[text='{self.text}', level='{self.level}']"
