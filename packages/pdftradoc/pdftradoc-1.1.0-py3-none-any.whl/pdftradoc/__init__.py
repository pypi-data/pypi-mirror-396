"""
pdftradoc - PDF Translation Document Library

A Python library for translating PDF documents while preserving the original layout.

Main functions:
    - extract(pdf_path, json_path) - Extract text segments from PDF to JSON
    - translate(json_path, source_lang, target_lang) - Auto-translate segments
    - apply_overlay(pdf_path, json_path, output_path) - Generate translated PDF

Quality control functions:
    - analyze_segmentation(json_path) - Analyze extraction quality
    - merge_segments(json_path) - Merge fragmented segments
    - verify_with_ocr(pdf_path, json_path) - Verify with OCR
    - extract_with_ocr(pdf_path, json_path) - Extract using OCR

Example:
    >>> from pdftradoc import extract, translate, apply_overlay
    >>> # Basic extraction
    >>> extract("document.pdf", "segments.json")
    >>>
    >>> # With merge and OCR verification
    >>> extract("document.pdf", "segments.json", merge=True, verify_ocr=True)
    >>>
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
    # Quality control functions
    analyze_segmentation,
    merge_segments,
    verify_with_ocr,
    extract_with_ocr,
)

__version__ = "1.1.0"
__author__ = "PdfTradoc"
__all__ = [
    "extract",
    "translate",
    "apply_overlay",
    "apply",
    "show",
    "stats",
    "translate_pdf",
    # Quality control
    "analyze_segmentation",
    "merge_segments",
    "verify_with_ocr",
    "extract_with_ocr",
]
