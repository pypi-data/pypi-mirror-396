class RawRun:
    def __init__(
        self,
        text: str,
        color: str | None,
        highlight: str | None,
        style: str,
        superscript: bool,
        subscript: bool,
        field_char_type: str,
        instruction: str,
    ):
        self._text = text
        self.color = color
        self.highlight = highlight
        self.style = style
        self.subscript = subscript
        self.superscript = superscript
        self.field_char_type = field_char_type
        self.instruction = instruction

    @property
    def text(self) -> str:
        return "" if self.subscript or self.superscript else self._text

    def to_text(self) -> str:
        return self.text

    def to_html(self) -> str:
        # Note: no support for colours as yet
        if self.field_char_type:
            return ""
        elif self.subscript:
            return f"<sub>{self.text}</sub>" if self.text else ""
        elif self.superscript:
            return f"<sup>{self.text}</sup>" if self.text else ""
        else:
            return f"{self.text}"

    def to_dict(self) -> dict:
        """Convert the instace to a dictionary representation"""
        return {
            "type": "run",
            "text": self.text,
            "color": self.color,
            "highlight": self.highlight,
            "style": self.style,
            "superscript": self.superscript,
            "subscript": self.subscript,
            "field_char_type": self.field_char_type,
            "instruction": self.instruction,
        }
