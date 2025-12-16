from .raw_run import RawRun


class RawSimpleField:
    def __init__(self, id: str, items: list[RawRun]):
        self.id = id
        self.items = items
        self.text = self._item_text()

    def to_html(self) -> str:
        start_tag = f'<a class="raw-docx-cross-ref" href="#{self.id}">'
        end_tag = "</a>"
        return f"{start_tag}{''.join([item.to_html() for item in self.items])}{end_tag}"

    def to_dict(self) -> dict:
        return {
            "type": "simple_field",
            "id": self.id,
            "text": self.text,
            "items": [item.to_dict() for item in self.items],
        }

    def _item_text(self) -> str:
        return "".join([x.text for x in self.items])
