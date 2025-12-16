class RawBookmarkEnd:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    @property
    def text(self) -> str:
        return ""

    def to_html(self) -> str:
        return ""

    def to_dict(self) -> dict:
        """Convert the paragraph to a dictionary representation"""
        return {
            "type": "bookmark_end",
            "id": self.id,
            "name": self.name,
        }
