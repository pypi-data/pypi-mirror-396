# Note: Bookmark is a target, the desination of any link
class RawBookmarkStart:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    @property
    def text(self) -> str:
        return ""

    def to_html(self) -> str:
        return f'<span id="{self.name}"></span>'

    def to_dict(self) -> dict:
        """Convert the paragraph to a dictionary representation"""
        return {
            "type": "bookmark_start",
            "id": self.id,
            "name": self.name,
        }
