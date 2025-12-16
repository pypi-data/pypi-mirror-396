import os
import re
import docx
import zipfile
from pathlib import Path
from raw_docx.raw_document import RawDocument
from raw_docx.raw_section import RawSection
from raw_docx.raw_paragraph import RawParagraph
from raw_docx.raw_image import RawImage
from raw_docx.raw_table import RawTable
from raw_docx.raw_table_row import RawTableRow
from raw_docx.raw_table_cell import RawTableCell
from raw_docx.raw_list import RawList
from raw_docx.raw_list_item import RawListItem
from raw_docx.docx.docx_paragraph import install
from raw_docx.docx.docx_table import TableMatrix
from docx import Document as DocXProcessor
from docx.document import Document
from docx.oxml.table import CT_Tbl, CT_TcPr
from docx.oxml.text.paragraph import CT_P
from docx.table import Table, _Cell
from docx.text.paragraph import Paragraph
from lxml import etree
from simple_error_log import Errors
from simple_error_log.error_location import KlassMethodLocation


class RawDocx:
    MODULE = "raw_docx.raw_docx.RawDocx"

    class LogicError(Exception):
        pass

    def __init__(self, full_path: str):
        install()
        self._errors = Errors()
        path = Path(full_path)
        self.full_path = full_path
        self.dir = path.parent
        self.filename = path.name
        self.image_path = os.path.join(self.dir, "images")
        self._errors.debug(
            f"RawDocx initialisation: full_path='{self.full_path}', dir='{self.dir}', image_path0'{self.image_path}', filename='{self.filename}",
            KlassMethodLocation(self.MODULE, "__init__"),
        )
        self.image_rels = {}
        self._organise_dir()
        self.source_document = DocXProcessor(self.full_path)
        self.target_document = RawDocument()
        self._process()

    @property
    def errors(self) -> Errors:
        return self._errors

    def _organise_dir(self):
        try:
            os.mkdir(self.image_path)
        except FileExistsError:
            pass
        except Exception as e:
            self._errors.exception(
                "Failed to create image directory",
                e,
                KlassMethodLocation(self.MODULE, "_organise_dir"),
            )

    def _process(self):
        try:
            self._process_images()
            for block_item in self._iter_block_items(self.source_document):
                target_section = self.target_document.current_section()
                if isinstance(block_item, Paragraph):
                    self._process_paragraph(block_item, target_section, self.image_rels)
                elif isinstance(block_item, Table):
                    self._process_table(block_item, target_section)
                else:
                    self._errors.warning(
                        f"Ignoring element {block_item}",
                        KlassMethodLocation(self.MODULE, "_process"),
                    )
                    raise ValueError
        except Exception as e:
            self._errors.exception(
                "Exception raised processing document",
                e,
                KlassMethodLocation(self.MODULE, "_process"),
            )

    def _process_images(self):
        # Extract images to image dir
        self._extract_images()
        for r in self.source_document.part.rels.values():
            if isinstance(r._target, docx.parts.image.ImagePart):
                self.image_rels[r.rId] = os.path.join(
                    self.image_path, os.path.basename(r._target.partname)
                )

    def _iter_block_items(self, parent):
        """
        Yield each paragraph and table child within *parent*, in document
        order. Each returned value is an instance of either Table or
        Paragraph. *parent* would most commonly be a reference to a main
        Document object, but also works for a _Cell object, which itself can
        contain paragraphs and tables.
        """
        if isinstance(parent, Document):
            parent_elm = parent.element.body
        elif isinstance(parent, _Cell):
            parent_elm = parent._tc
        else:
            raise ValueError("something's not right with the parent")

        for child in parent_elm.iterchildren():
            if isinstance(child, str):
                self._errors.warning(
                    f"Ignoring eTree element {child}",
                    KlassMethodLocation(self.MODULE, "_iter_block_items"),
                )
            elif isinstance(child, CT_P):
                yield Paragraph(child, parent)
            elif isinstance(child, CT_Tbl):
                yield Table(child, parent)
            elif isinstance(child, etree._Element):
                if (
                    child.tag
                    == "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tcPr"
                ):
                    pass
                elif (
                    child.tag
                    == "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sdt"
                ):
                    pass
                else:
                    self._errors.warning(
                        f"Ignoring eTree element '{child.tag}'",
                        KlassMethodLocation(self.MODULE, "_iter_block_items"),
                    )

            else:
                raise ValueError(f"something's not right with a child {type(child)}")

    def _process_table(self, table, target: RawSection | RawTableCell):
        target_table = RawTable()
        target.add(target_table)
        matrix = TableMatrix(table, self._errors)
        for r_index, row in enumerate(matrix):
            target_row = RawTableRow()
            target_table.add(target_row)
            for c_index, row_cell in enumerate(row):
                if row_cell:
                    h_span = row_cell.right - row_cell.left + 1
                    v_span = row_cell.bottom - row_cell.top + 1
                    first = r_index == row_cell.top and c_index == row_cell.left
                    target_cell = RawTableCell(h_span, v_span, first)
                    target_row.add(target_cell)
                    for block_item in self._iter_block_items(row_cell.cell):
                        if isinstance(block_item, Paragraph):
                            self._process_cell(block_item, target_cell)
                        elif isinstance(block_item, Table):
                            raise self.LogicError("Table within table detected")
                        elif isinstance(block_item, etree._Element):
                            if block_item.tag == CT_TcPr:
                                pass
                            else:
                                self._errors.warning(
                                    f"Ignoring eTree element '{block_item.tag}'",
                                    KlassMethodLocation(self.MODULE, "_process_table"),
                                )
                        else:
                            raise self.LogicError(
                                f"Something's not right with a child {type(block_item)}"
                            )

    def _process_cell(self, paragraph, target_cell: RawTableCell):
        if self._is_list(paragraph):
            list_level = self.get_list_level(paragraph)
            item = RawListItem(paragraph.extract_content(self._errors), list_level)
            if target_cell.is_in_list():
                list = target_cell.current_list()
            else:
                list = RawList(self._errors)
                target_cell.add(list)
            list.add(item)
        else:
            target_paragraph = RawParagraph(paragraph.extract_content(self._errors))
            target_cell.add(target_paragraph)

    def _process_paragraph(
        self, paragraph, target_section: RawSection, image_rels: dict
    ):
        is_heading, level = self._is_heading(paragraph.style.name)
        if is_heading:
            target_section = RawSection(paragraph.text, paragraph.text, level)
            self.target_document.add(target_section)
        elif self._is_list(paragraph):
            list_level = self.get_list_level(paragraph)
            item = RawListItem(paragraph.extract_content(self._errors), list_level)
            if target_section.is_in_list():
                list = target_section.current_list()
            else:
                list = RawList(self._errors)
                target_section.add(list)
            list.add(item)
        elif "Graphic" in paragraph._p.xml:
            for rId in image_rels:
                if rId in paragraph._p.xml:
                    target_image = RawImage(image_rels[rId], self._errors)
                    target_section.add(target_image)
        else:
            # print("===== Raw Para =====")
            target_paragraph = RawParagraph(paragraph.extract_content(self._errors))
            target_section.add(target_paragraph)

    def get_list_level(self, paragraph):
        list_level = paragraph._p.xpath("./w:pPr/w:numPr/w:ilvl/@w:val")
        return int(str(list_level[0])) if list_level else 0

    def _is_heading(self, text) -> tuple[bool, int]:
        """
        Extract heading level from text containing "Heading <N>" pattern.

        Args:
            text: Text to analyze for heading pattern

        Returns:
            tuple[bool, int]: (success, level) where success indicates if heading
            pattern was found and level is the extracted integer value
        """
        if not text:
            return False, 0

        # Look for "Heading <N>" pattern where <N> is one or more digits
        match = re.search(r"Heading\s+(\d+)", text, re.IGNORECASE)
        if match:
            try:
                level = int(match.group(1))
                return True, level
            except (ValueError, IndexError):
                return True, 0
        return False, 0

    def _is_list(self, paragraph):
        level = paragraph._p.xpath("./w:pPr/w:numPr/w:ilvl/@w:val")
        if level:
            return True
        if paragraph.style.name in ["CPT_List Bullet", "List Bullet"]:
            return True
        if paragraph.text:
            if hex(ord(paragraph.text[0])) == "0x2022":
                return True
        return False

    def _extract_images(self):
        archive = zipfile.ZipFile(self.full_path)
        for file in archive.filelist:
            if file.filename.startswith("word/media/"):
                # Extract the image file name from the path
                image_name = Path(file.filename).name
                # Create the target path for the image
                target_path = os.path.join(self.image_path, image_name)
                # Extract the file to the target path
                with archive.open(file) as source, open(target_path, "wb") as target:
                    target.write(source.read())

    def to_dict(self) -> dict:
        """Convert the RawDocx instance to a dictionary representation"""
        if hasattr(self, "target_document"):
            return {
                "type": "raw_docx",
                "document": self.target_document.to_dict()
                if hasattr(self.target_document, "to_dict")
                else None,
            }
        return {"type": "raw_docx", "document": None}
