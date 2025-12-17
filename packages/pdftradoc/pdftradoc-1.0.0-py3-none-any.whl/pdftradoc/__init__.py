"""
pdftradoc - PDF Translation Document Library

A Python library for translating PDF documents while preserving the original layout.

Main functions:
    - extract(pdf_path, json_path) - Extract text segments from PDF to JSON
    - translate(json_path, source_lang, target_lang) - Auto-translate segments
    - apply_overlay(pdf_path, json_path, output_path) - Generate translated PDF

Example:
    >>> from pdftradoc import extract, translate, apply_overlay
    >>> extract("document.pdf", "segments.json")
    >>> translate("segments.json", source_lang="it", target_lang="en")
    >>> apply_overlay("document.pdf", "segments.json", "translated.pdf")
"""

from .extractor import (
    extract,
    translate,
    apply_overlay,
    apply,
    show,
    stats,
    translate_pdf,
)

__version__ = "1.0.0"
__author__ = "PdfTradoc"
__all__ = [
    "extract",
    "translate",
    "apply_overlay",
    "apply",
    "show",
    "stats",
    "translate_pdf",
]
