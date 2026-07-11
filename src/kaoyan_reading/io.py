import re
import zipfile
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree


def read_source(path: str) -> str:
    source = Path(path)
    suffix = source.suffix.lower()
    if suffix in {".txt", ".md"}:
        return source.read_text(encoding="utf-8")
    if suffix == ".docx":
        return _read_docx(source)
    if suffix == ".pdf":
        return _read_pdf(source)
    raise ValueError(f"Unsupported file type: {source.suffix}. Use .txt, .md, .docx, or .pdf.")


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(lines).strip()


def _read_docx(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml")
    root = ElementTree.fromstring(xml)
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs = []
    for paragraph in root.findall(".//w:p", namespace):
        texts = [node.text or "" for node in paragraph.findall(".//w:t", namespace)]
        joined = "".join(texts).strip()
        if joined:
            paragraphs.append(joined)
    return "\n\n".join(paragraphs)


def _read_pdf(path: Path) -> str:
    readers = (_read_pdf_with_pymupdf, _read_pdf_with_pypdf, _read_pdf_with_pdfplumber)
    errors = []
    for reader in readers:
        try:
            return reader(path)
        except ImportError as exc:
            errors.append(str(exc))
    joined = "; ".join(errors)
    raise RuntimeError(
        "PDF extraction needs one optional library installed: pymupdf, pypdf, or pdfplumber. "
        f"Tried all readers and got: {joined}"
    )


def _read_pdf_with_pymupdf(path: Path) -> str:
    import fitz  # type: ignore

    with fitz.open(path) as document:
        return "\n\n".join(page.get_text() for page in document)


def _read_pdf_with_pypdf(path: Path) -> str:
    from pypdf import PdfReader  # type: ignore

    reader = PdfReader(str(path))
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)


def _read_pdf_with_pdfplumber(path: Path) -> str:
    import pdfplumber  # type: ignore

    with pdfplumber.open(path) as pdf:
        return "\n\n".join(page.extract_text() or "" for page in pdf.pages)


def paragraphs(text: str) -> Iterable[str]:
    for block in re.split(r"\n\s*\n", normalize_text(text)):
        block = re.sub(r"\s*\n\s*", " ", block).strip()
        if block:
            yield block

