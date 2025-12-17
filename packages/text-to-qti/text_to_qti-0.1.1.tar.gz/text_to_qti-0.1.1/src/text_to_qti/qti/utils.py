"""XML utilities for QTI generation."""

from typing import Dict, Optional

from lxml import etree

# QTI 1.2 namespaces
QTI_NAMESPACE = "http://www.imsglobal.org/xsd/ims_qtiasiv1p2"
IMS_MD_NAMESPACE = "http://www.imsglobal.org/xsd/imsmd_v1p2"
XSI_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"

# Namespace map for cleaner code
NSMAP = {
    None: QTI_NAMESPACE,
    "imsmd": IMS_MD_NAMESPACE,
    "xsi": XSI_NAMESPACE,
}


def create_element(
    tag: str, text: Optional[str] = None, nsmap: Optional[Dict] = None, **attribs
) -> etree._Element:
    """Create an XML element with namespace support.

    Args:
        tag: Element tag name
        text: Optional text content
        nsmap: Optional namespace map
        **attribs: Element attributes

    Returns:
        Created element
    """
    elem = etree.Element(tag, nsmap=nsmap or {}, **attribs)
    if text:
        elem.text = text
    return elem


def add_child(
    parent: etree._Element, tag: str, text: Optional[str] = None, **attribs
) -> etree._Element:
    """Add a child element to a parent.

    Args:
        parent: Parent element
        tag: Child tag name
        text: Optional text content
        **attribs: Element attributes

    Returns:
        Created child element
    """
    child = etree.SubElement(parent, tag, **attribs)
    if text:
        child.text = text
    return child


def element_to_string(
    elem: etree._Element, pretty_print: bool = True, with_declaration: bool = False
) -> str:
    """Convert element to string.

    Args:
        elem: Element to convert
        pretty_print: Whether to pretty print
        with_declaration: Whether to include XML declaration

    Returns:
        XML string
    """
    result = str(
        etree.tostring(
            elem,
            encoding="unicode",
            pretty_print=pretty_print,
            xml_declaration=False,
        )
    )
    if with_declaration:
        result = '<?xml version="1.0" encoding="UTF-8"?>\n' + result
    return result


def escape_xml(text: str) -> str:
    """Escape XML special characters.

    Args:
        text: Text to escape

    Returns:
        Escaped text
    """
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )
