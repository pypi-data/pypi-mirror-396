from .raw_run import RawRun
from .raw_bookmark_start import RawBookmarkStart
from .raw_bookmark_end import RawBookmarkEnd


class RawParagraph:
    def __init__(self, items: list[RawRun | RawBookmarkStart | RawBookmarkEnd]):
        self.items = items
        self.text = self._item_text()
        self.klasses = []

    def to_text(self):
        return self._item_text()

    def find(self, text: str) -> bool:
        return True if text in self.text else False

    def find_at_start(self, text: str) -> bool:
        return True if self.text.upper().startswith(text.upper()) else False

    def to_html(self) -> str:
        klass_list = " ".join(self.klasses)
        open_tag = f'<p class="{klass_list}">' if self.klasses else "<p>"
        close_tag = "</p>"
        body = ""
        in_anchor = False
        in_bookmark = False
        bookmark_id = None
        for index, item in enumerate(self.items):
            if isinstance(item, RawRun):
                if item.field_char_type == "begin":
                    if next_item := self._next_run_item(index):
                        if next_item.instruction:
                            body += f'<a class="raw-docx-cross-ref" href="#{next_item.instruction}">'
                            in_anchor = True
                elif item.field_char_type == "separate":
                    if next_item := self._next_run_item(index):
                        if next_item.instruction:
                            body += f'<a class="raw-docx-cross-ref" href="#{next_item.instruction}">'
                            in_anchor = True
                        elif in_bookmark:
                            body += (
                                f'<span class="raw-docx-bookmark" id="{bookmark_id}">'
                            )
                elif in_anchor and item.field_char_type == "end":
                    body += "</a>"
                    in_anchor = False
                elif in_bookmark and item.field_char_type == "end":
                    body += "</span>"
                    in_bookmark = False  # Will also be caught by BookmarkEnd
                    bookmark_id = None
                else:
                    body += item.to_html()
            elif isinstance(item, RawBookmarkStart):
                in_bookmark = True
                bookmark_id = item.name
            elif isinstance(item, RawBookmarkEnd):
                in_bookmark = False  # Will also be caught by field_char_type = "end"
                bookmark_id = None
            else:
                body += item.to_html()
        return f"{open_tag}{body}{close_tag}"

    def add_class(self, klass) -> None:
        self.klasses.append(klass)

    def to_dict(self) -> dict:
        """Convert the paragraph to a dictionary representation"""
        return {
            "type": "paragraph",
            "text": self.text,
            "items": [item.to_dict() for item in self.items],
            "classes": self.klasses,
        }

    def add_span(self, text: str, klass: str) -> None:
        new_str = f'<span class="{klass}">{text}</span>'
        self.text = new_str + self.text[len(text) :]

    def _next_run_item(self, start: int) -> RawRun | None:
        for index in range(start + 1, len(self.items)):
            if isinstance(self.items[index], RawRun):
                return self.items[index]
        return None

    def _item_text(self) -> str:
        text = ""
        in_separate = False
        for index, item in enumerate(self.items):
            if isinstance(item, RawRun):
                if item.field_char_type == "separate":
                    in_separate = True
                elif in_separate and item.field_char_type == "end":
                    in_separate = False
                elif not in_separate:
                    text += item.text
            else:
                text += item.text
        return text
