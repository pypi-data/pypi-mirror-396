import re
from docx.text.paragraph import Paragraph
from docx.styles.style import ParagraphStyle
from docx.text.run import Run
from simple_error_log import Errors
from simple_error_log.error_location import KlassMethodLocation
from raw_docx.raw_run import RawRun
from raw_docx.raw_simple_field import RawSimpleField
from raw_docx.raw_bookmark_start import RawBookmarkStart
from raw_docx.raw_bookmark_end import RawBookmarkEnd
from docx.oxml.text.run import CT_R
from lxml import etree


BOOKMARK_START = (
    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}bookmarkStart"
)
BOOKMARK_END = (
    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}bookmarkEnd"
)
FIELD_SIMPLE = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fldSimple"
FIELD_CHAR = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fldChar"
INSTRUCTION_TEXT = (
    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}instrText"
)

PARA_PROPERTIES = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}pPr"
HYPERLINK = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hyperlink"
PROOF_ERROR = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}proofErr"

ELEMENT_IGNORE_TAGS = [PARA_PROPERTIES, HYPERLINK, PROOF_ERROR]
SIMPLE_FIELD_IGNORE_TAGS = [BOOKMARK_START, BOOKMARK_END]

ID_ATTRIBUTE = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id"
NAME_ATTRIBUTE = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}name"
FIELD_CHAR_TYPE_ATTRIBUTE = (
    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}fldCharType"
)
INSTR_ATTRIBUTE = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}instr"

MODULE = "raw_docx.docx.docx_paragraph"


def install():
    setattr(Paragraph, "extract_content", extract_content)


def extract_content(
    paragraph: Paragraph, errors: Errors
) -> list[RawRun | RawBookmarkStart | RawBookmarkEnd | RawSimpleField]:
    return process_element(paragraph._element, paragraph, errors)


def process_element(
    element: etree._Element | CT_R, parent: Paragraph, errors: Errors
) -> list[RawRun | RawBookmarkStart | RawBookmarkEnd | RawSimpleField]:
    data = []
    bookmark = None
    bookmark_id = None
    for child in element:
        # print(
        #     f"XML: {child.xml if isinstance(child, CT_R) else etree.tostring(child, encoding='unicode', pretty_print=True)}, type{type(child)}"
        # )
        if isinstance(child, CT_R):
            run = build_run(child, parent, errors)
            data.append(run)
        elif child.tag == BOOKMARK_START:
            if bookmark:
                del data[bookmark]
            id = child.get(ID_ATTRIBUTE)
            name = child.get(NAME_ATTRIBUTE)
            data.append(RawBookmarkStart(id, name))
            bookmark_id = id
            bookmark = len(data) - 1
        elif child.tag == BOOKMARK_END:
            id = child.get(ID_ATTRIBUTE)
            if id == bookmark_id:
                name = child.get(NAME_ATTRIBUTE)
                data.append(RawBookmarkEnd(id, name))
                bookmark = None
                bookmark_id = None
        elif child.tag == FIELD_SIMPLE:
            bookmark_id = _extract_instruction_id(child.get(INSTR_ATTRIBUTE))
            items = process_simple_field(child, parent, errors)
            data.append(RawSimpleField(bookmark_id, create_runs(items, errors)))
        elif child.tag in ELEMENT_IGNORE_TAGS:
            pass
        else:
            errors.warning(
                f"Element other instance/tag detected:: '{child.tag}'",
                KlassMethodLocation(MODULE, "process_element"),
            )
    return create_runs(data, errors)


def process_simple_field(element, parent: Paragraph, errors: Errors) -> list[RawRun]:
    data = []
    for child in element:
        # print(F"CHILD: {child}, type{type(child)}")
        if isinstance(child, CT_R):
            run = build_run(child, parent, errors)
            data.append(run)
        elif child.tag in SIMPLE_FIELD_IGNORE_TAGS:
            pass
        else:
            errors.warning(
                f"Simple field other instance/tag detected: '{child.tag}'",
                KlassMethodLocation(MODULE, "process_element"),
            )
    return data


def _extract_instruction_id(text: str) -> str:
    pattern = r"_TN[A-F0-9]+"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(0) if match else ""


def create_runs(data: list[dict], errors: Errors) -> list[RawRun]:
    data = _tidy_runs(data, errors)
    results = []
    for x in data:
        if isinstance(x, dict):
            results.append(
                RawRun(
                    x["text"],
                    x["color"],
                    x["highlight"],
                    x["style"],
                    x["superscript"],
                    x["subscript"],
                    x["field_char_type"],
                    x["instruction"],
                )
            )
        else:
            results.append(x)
    return results


def build_run(element, paragraph: Paragraph, errors: Errors) -> RawRun:
    run = Run(element, paragraph)
    field_char_type = None
    instruction = None
    for child in element:
        if child.tag == FIELD_CHAR:
            field_char_type = child.get(FIELD_CHAR_TYPE_ATTRIBUTE)
        elif child.tag == INSTRUCTION_TEXT:
            instruction = _extract_instruction_id(child.text)
    return {
        "text": run.text,
        "color": _get_run_color(paragraph.style, run, errors),
        "highlight": _get_highlight_color(run, errors),
        "keep": True,
        "style": paragraph.style.name,
        "subscript": run.font.subscript,
        "superscript": run.font.superscript,
        "field_char_type": field_char_type,
        "instruction": instruction,
    }


def _tidy_runs(data: list, errors: Errors) -> list:
    more = False
    # print(f"TIDY IN: {data}")
    for index, run in enumerate(data):
        if index > 0 and isinstance(run, dict) and isinstance(data[index - 1], dict):
            # print(f"A={run}, B={data[index - 1]}")
            if _equal_with_ignore(run, data[index - 1], ["text", "keep"]):
                run["text"] = data[index - 1]["text"] + run["text"]
                data[index - 1]["keep"] = False
                more = True
    new_data = [
        x
        for x in data
        if (isinstance(x, dict) and x["keep"]) or (not isinstance(x, dict))
    ]
    if more:
        new_data = _tidy_runs(new_data, errors)
    # print(f"TIDY OUT: {new_data}")
    return new_data


def _equal_with_ignore(a: dict, b: dict, ignore_keys: list) -> bool:
    # print(f"A={a}, B={b}")
    return {k: v for k, v in a.items() if k not in ignore_keys} == {
        k: v for k, v in b.items() if k not in ignore_keys
    }


def _get_run_color(paragraph: Paragraph, run: Run, errors: Errors) -> str | None:
    paragraph_color = _get_font_colour(paragraph, errors)
    font_color = _get_font_colour(run, errors)
    style_color = _run_style_color(run, errors)
    if font_color:
        result = str(font_color)
    elif style_color:
        result = str(style_color)
    else:
        result = str(paragraph_color)
    return result


def _get_highlight_color(run: Run, errors: Errors) -> str | None:
    try:
        return str(run.font.highlight_color)
    except Exception as e:
        errors.exception("Failed to get run highlight color", e)
        return None


def _run_style_color(run: Run, errors: Errors) -> str | None:
    try:
        run_color = None
        run_style = run.style
        while run_style and not run_color:
            if run_style.font.color.rgb:
                run_color = run_style.font.color.rgb
            else:
                run_style = run_style.base_style
        return run_color
    except Exception as e:
        errors.exception("Failed to get run style color", e)
        return None


def _get_font_colour(item: Run | ParagraphStyle, errors: Errors) -> str | None:
    try:
        return item.font.color.rgb
    except Exception as e:
        errors.exception("Failed to get font color", e)
        return None
