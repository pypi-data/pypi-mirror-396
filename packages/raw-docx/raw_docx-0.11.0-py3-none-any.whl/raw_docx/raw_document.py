from .raw_section import RawSection


class RawDocument:
    def __init__(self):
        self.sections = []
        self._levels = [0, 0, 0, 0, 0, 0]
        self._section_number_mapping = {}
        self._section_title_mapping = {}
        section = RawSection(None, None, 1)
        self.add(section, False)  # No section number increment

    def add(self, section: RawSection, increment=True):
        if increment:
            self._inc_section_number(section.level)
            section.number = self._get_section_number(section.level)
        self._section_number_mapping[section.number] = section
        self._section_title_mapping[section.title] = section
        self.sections.append(section)

    def current_section(self) -> RawSection:
        return self.sections[-1]

    def section_by_ordinal(self, ordinal: int) -> RawSection:
        if 1 <= ordinal <= len(self.sections):
            return self.sections[ordinal - 1]
        else:
            return None

    def section_by_number(self, section_number: str) -> RawSection:
        if section_number in self._section_number_mapping:
            return self._section_number_mapping[section_number]
        else:
            return None

    def section_by_title(self, section_title: str) -> RawSection:
        if section_title in self._section_title_mapping:
            return self._section_title_mapping[section_title]
        else:
            return None

    def _inc_section_number(self, level: int) -> None:
        self._levels[level] += 1
        for index in range(level + 1, len(self._levels)):
            self._levels[index] = 0

    def _get_section_number(self, level: int) -> str:
        return ".".join(str(x) for x in self._levels[1 : level + 1])

    def to_dict(self) -> dict:
        """Convert the document to a dictionary representation"""
        return {
            "type": "document",
            "sections": [section.to_dict() for section in self.sections],
            "levels": self._levels,
            "section_number_mapping": {
                num: section.to_dict()
                for num, section in self._section_number_mapping.items()
            },
            "section_title_mapping": {
                title: section.to_dict()
                for title, section in self._section_title_mapping.items()
            },
        }

    def to_html(self) -> str:
        sections = [section.to_html() for section in self.sections]
        return ("").join(sections)
