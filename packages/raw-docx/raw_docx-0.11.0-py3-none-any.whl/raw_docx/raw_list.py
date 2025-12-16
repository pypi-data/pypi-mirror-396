from .raw_list_item import RawListItem
from simple_error_log import Errors


class RawList:
    def __init__(self, errors: Errors, level=0):
        self.errors = errors
        self.items = []  # List to store RawListItems and nested RawLists
        self.level = level

    def add(self, item: RawListItem) -> None:
        if item.level == self.level:
            self.items.append(item)
        elif item.level > self.level:
            list = self.items[-1] if self.items else None
            if not isinstance(list, RawList):
                list = RawList(self.errors, item.level)
                self.items.append(list)
            list.add(item)
            if item.level > self.level + 1:
                self.errors.warning(
                    f"Adding list item '{item}' to item but level jump greater than 1"
                )
        else:
            self.errors.error(
                f"Failed to add list item '{item}' to list '{self}', levels are in error"
            )

    @property
    def text(self):
        return self.to_text()

    def to_text(self) -> str:
        lines = []
        for item in self.items:
            lines.append(f"{item.to_text()}")
        return ("\n").join(lines)

    def all_items(self) -> list[RawListItem]:
        result = []
        for item in self.items:
            if isinstance(item, RawListItem):
                result.append(item)
            elif isinstance(item, RawList):
                result += item.all_items()
        return result

    def to_html(self) -> str:
        lines = []
        lines.append("<ul>")
        for item in self.items:
            lines.append(f"<li>{item.to_html()}</li>")
        lines.append("</ul>")
        return ("\n").join(lines)

    def to_dict(self) -> dict:
        return {
            "type": "list",
            "level": self.level,
            "items": [
                item.to_dict() if hasattr(item, "to_dict") else str(item)
                for item in self.items
            ],
        }

    def __str__(self) -> str:
        """Return a string representation of the list showing its level and item count.

        Returns:
            str: String representation of the list
        """
        return f"[level='{self.level}', item_count='{len(self.items)}']"
