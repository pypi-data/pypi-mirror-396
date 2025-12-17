"""
PDF Segment Extractor - Simple JSON-based workflow.

Three simple functions:
1. extract(pdf_path, json_path) - Extract segments from PDF to JSON
2. translate(json_path, source_lang, target_lang) - Auto-translate segments
3. apply(pdf_path, json_path, output_path) - Apply JSON translations to PDF

Or use the all-in-one function:
- translate_pdf(pdf_path, output_path, source_lang, target_lang) - Complete workflow
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List, Any, Optional
import fitz


def extract(pdf_path: str, json_path: str) -> dict:
    """
    Extract all text segments from a PDF and save to JSON.

    Args:
        pdf_path: Path to the PDF file
        json_path: Path where to save the JSON file

    Returns:
        Dictionary with extraction statistics

    Example:
        >>> from pdftradoc.extractor import extract, apply
        >>> extract("document.pdf", "segments.json")
        >>> # Edit segments.json to add translations
        >>> apply("document.pdf", "segments.json", "translated.pdf")
    """
    doc = fitz.open(pdf_path)

    output = {
        "source": pdf_path,
        "pages": len(doc),
        "segments": []
    }

    segment_id = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)

        for block_idx, block in enumerate(blocks.get("blocks", [])):
            if block.get("type") != 0:
                continue

            for line_idx, line in enumerate(block.get("lines", [])):
                # Get line direction for vertical text detection
                line_dir = line.get("dir", (1.0, 0.0))
                wmode = line.get("wmode", 0)

                # Calculate rotation angle from direction vector
                # dir (1,0) = 0°, (0,1) = 90°, (-1,0) = 180°, (0,-1) = 270°
                rotation = round(math.degrees(math.atan2(line_dir[1], line_dir[0])))

                # Combine all spans in the line
                text = ""
                bbox = None
                font_name = ""
                font_size = 11.0
                color = [0, 0, 0]
                flags = 0  # Text flags (bold, italic, etc.)
                origin = None

                for span in line.get("spans", []):
                    text += span.get("text", "")

                    if span.get("text", "").strip() and not font_name:
                        font_name = span.get("font", "Helvetica")
                        font_size = span.get("size", 11.0)
                        flags = span.get("flags", 0)
                        origin = span.get("origin")

                        c = span.get("color", 0)
                        color = [
                            ((c >> 16) & 0xFF) / 255,
                            ((c >> 8) & 0xFF) / 255,
                            (c & 0xFF) / 255,
                        ]

                    span_bbox = span.get("bbox")
                    if span_bbox:
                        if bbox is None:
                            bbox = list(span_bbox)
                        else:
                            bbox[0] = min(bbox[0], span_bbox[0])
                            bbox[1] = min(bbox[1], span_bbox[1])
                            bbox[2] = max(bbox[2], span_bbox[2])
                            bbox[3] = max(bbox[3], span_bbox[3])

                if not text.strip() or bbox is None:
                    continue

                # Detect bold/italic from flags
                is_bold = bool(flags & 16)  # fitz.TEXT_FONT_BOLD
                is_italic = bool(flags & 2)  # fitz.TEXT_FONT_ITALIC

                segment = {
                    "id": segment_id,
                    "page": page_num,
                    "text": text,
                    "translation": "",  # <-- To be filled
                    "bbox": bbox,
                    "font": font_name,
                    "size": round(font_size, 1),
                    "color": [round(c, 3) for c in color],
                    "bold": is_bold,
                    "italic": is_italic,
                    "rotation": rotation,  # 0 = horizontal, 90 = vertical, etc.
                    "origin": list(origin) if origin else [bbox[0], bbox[3]],
                }

                output["segments"].append(segment)
                segment_id += 1

    doc.close()

    # Save JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    return {
        "segments": len(output["segments"]),
        "pages": output["pages"],
        "json_path": json_path,
    }


def _get_base14_font(font_name: str, bold: bool = False, italic: bool = False) -> str:
    """
    Map font name to PDF Base14 font with bold/italic variants.

    Args:
        font_name: Original font name from PDF
        bold: Whether text is bold (can also be detected from font_name)
        italic: Whether text is italic (can also be detected from font_name)

    Returns:
        Base14 font name for PyMuPDF

    Base14 font abbreviations:
        Helvetica: helv, hebo (bold), heit (italic), hebi (bold italic)
        Courier: cour, cobo (bold), coit (italic), cobi (bold italic)
        Times: tiro, tibo (bold), tiit (italic), tibi (bold italic)
    """
    # Normalize font name
    name_lower = font_name.lower()

    # Detect bold/italic from font name if not explicitly provided
    # Common patterns: "Bold", "Bd", "Heavy", "Black" for bold
    # "Italic", "It", "Oblique", "Obl" for italic
    if not bold:
        bold = any(x in name_lower for x in ["bold", "-bd", "heavy", "black"])
    if not italic:
        italic = any(x in name_lower for x in ["italic", "-it", "oblique", "obl"])

    # Detect font family and select base + variants
    if "courier" in name_lower or "mono" in name_lower:
        # Courier family
        if bold and italic:
            return "cobi"
        elif bold:
            return "cobo"
        elif italic:
            return "coit"
        else:
            return "cour"
    elif "times" in name_lower or "serif" in name_lower:
        # Times family
        if bold and italic:
            return "tibi"
        elif bold:
            return "tibo"
        elif italic:
            return "tiit"
        else:
            return "tiro"
    else:
        # Helvetica (default for sans-serif and unknown fonts)
        if bold and italic:
            return "hebi"
        elif bold:
            return "hebo"
        elif italic:
            return "heit"
        else:
            return "helv"


def _calculate_font_and_bbox(
    text: str,
    fontname: str,
    bbox: List[float],
    original_size: float,
    min_size: float = 5.0,
) -> tuple:
    """
    Calculate font size and bbox to fit text.

    If text is too long, first try to reduce font size.
    If font would be too small, expand bbox instead.

    Args:
        text: Text to fit
        fontname: Font name (e.g., 'helv', 'hebo')
        bbox: Original bounding box [x0, y0, x1, y1]
        original_size: Original font size
        min_size: Minimum font size (below this, expand bbox)

    Returns:
        Tuple of (fontsize, new_bbox)
    """
    max_width = bbox[2] - bbox[0]

    # Calculate text width at original size
    text_width = fitz.get_text_length(text, fontname, original_size)

    # If text fits, return original values
    if text_width <= max_width:
        return original_size, bbox

    # Calculate scale factor needed
    scale = max_width / text_width
    new_size = original_size * scale

    # If new size is acceptable, use it
    if new_size >= min_size:
        return new_size, bbox

    # Font would be too small - expand bbox instead
    # Use minimum font size and calculate required width
    required_width = fitz.get_text_length(text, fontname, min_size)

    # Expand bbox to the right
    new_bbox = [
        bbox[0],
        bbox[1],
        bbox[0] + required_width + 2,  # +2 for small margin
        bbox[3],
    ]

    return min_size, new_bbox


def _extract_embedded_fonts(doc: fitz.Document) -> Dict[str, fitz.Font]:
    """
    Extract embedded fonts from PDF document for reuse.

    Returns a dict mapping font names to fitz.Font objects.
    """
    fonts = {}

    # Collect all font xrefs from all pages
    font_xrefs = {}
    for page_num in range(len(doc)):
        for font_info in doc.get_page_fonts(page_num):
            xref, ext, ftype, name, ref_name, enc = font_info
            if ext == 'ttf' and xref not in font_xrefs:
                font_xrefs[xref] = name

    # Extract each font
    for xref, name in font_xrefs.items():
        try:
            font_data = doc.extract_font(xref)
            if font_data and len(font_data) >= 4:
                fname, fext, fsubtype, fbuffer = font_data
                if fbuffer:
                    fonts[name] = fitz.Font(fontbuffer=fbuffer)
        except Exception:
            pass

    return fonts


def _get_font_for_segment(
    seg: dict,
    embedded_fonts: Dict[str, fitz.Font],
) -> tuple:
    """
    Get the best font for a segment, preferring embedded fonts.

    Returns (font, fontname_for_base14)
    """
    font_name = seg.get("font", "Helvetica")
    is_bold = seg.get("bold", False)
    is_italic = seg.get("italic", False)

    # Try to find matching embedded font
    font_name_lower = font_name.lower()

    for name, font in embedded_fonts.items():
        name_lower = name.lower()

        # Check if font name matches
        if font_name_lower in name_lower or name_lower in font_name_lower:
            # Check bold/italic match
            name_has_bold = "bold" in name_lower
            name_has_italic = "italic" in name_lower

            if name_has_bold == is_bold and name_has_italic == is_italic:
                return font, None

    # Fall back to Base14 font
    fontname = _get_base14_font(font_name, is_bold, is_italic)
    return fitz.Font(fontname), fontname


def apply(pdf_path: str, json_path: str, output_path: str) -> dict:
    """
    Apply translations from JSON file to PDF.

    Preserves original font, style (bold/italic), color and position.
    Uses embedded fonts from the original PDF when available.
    Automatically adjusts font size if translation is longer than original.

    Args:
        pdf_path: Path to the original PDF
        json_path: Path to JSON file with translations
        output_path: Path for the output PDF

    Returns:
        Dictionary with application statistics

    Example:
        >>> apply("document.pdf", "segments.json", "translated.pdf")
    """
    # Load JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    doc = fitz.open(pdf_path)

    # Extract embedded fonts for reuse
    embedded_fonts = _extract_embedded_fonts(doc)

    stats = {
        "total": len(data.get("segments", [])),
        "translated": 0,
        "applied": 0,
        "rotated": 0,
        "resized": 0,
        "errors": [],
    }

    # Group by page
    by_page: Dict[int, List[dict]] = {}
    for seg in data.get("segments", []):
        translation = seg.get("translation", "").strip()
        original = seg.get("text", "").strip()

        # Skip if no translation or same as original
        if not translation or translation == original:
            continue

        stats["translated"] += 1

        page_num = seg.get("page", 0)
        if page_num not in by_page:
            by_page[page_num] = []
        by_page[page_num].append(seg)

    # Apply translations page by page
    for page_num, segments in by_page.items():
        page = doc[page_num]

        # Collect all redaction annotations first
        for seg in segments:
            try:
                bbox = seg.get("bbox", [0, 0, 0, 0])
                rotation = seg.get("rotation", 0)

                # For rotated text, search and redact
                if rotation != 0:
                    original_text = seg.get("text", "")
                    search_results = page.search_for(original_text)
                    for search_rect in search_results:
                        expanded = fitz.Rect(
                            search_rect.x0 - 1,
                            search_rect.y0 - 1,
                            search_rect.x1 + 1,
                            search_rect.y1 + 1,
                        )
                        page.add_redact_annot(expanded, fill=(1, 1, 1))
                else:
                    # Normal text: redact the bbox area
                    rect = fitz.Rect(bbox)
                    page.add_redact_annot(rect, fill=(1, 1, 1))

            except Exception as e:
                stats["errors"].append(f"Redact {seg.get('id')}: {e}")

        # Apply all redactions at once
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

        # Now write translated text
        for seg in segments:
            try:
                bbox = seg.get("bbox", [0, 0, 0, 0])
                rotation = seg.get("rotation", 0)
                origin = seg.get("origin", [bbox[0], bbox[3]])
                original_size = seg.get("size", 11)
                color = tuple(seg.get("color", [0, 0, 0]))

                # Get font (prefer embedded)
                font, base14_name = _get_font_for_segment(seg, embedded_fonts)

                # Calculate font size to fit text
                # Use base14 name for width calculation if available
                calc_fontname = base14_name if base14_name else "helv"

                if rotation in (90, -90, 270, -270):
                    # Vertical: use height as available width
                    virtual_width = bbox[3] - bbox[1]
                    virtual_bbox = [bbox[0], bbox[1], bbox[0] + virtual_width, bbox[3]]
                else:
                    virtual_bbox = bbox

                fontsize, _ = _calculate_font_and_bbox(
                    seg["translation"], calc_fontname, virtual_bbox, original_size
                )

                if fontsize < original_size:
                    stats["resized"] += 1

                # Create text writer
                tw = fitz.TextWriter(page.rect)

                # Determine position
                if rotation == 90 or rotation == -270:
                    pos = fitz.Point(bbox[2], bbox[1])
                elif rotation == -90 or rotation == 270:
                    pos = fitz.Point(bbox[0], bbox[3])
                elif rotation == 180 or rotation == -180:
                    pos = fitz.Point(bbox[2], bbox[3])
                else:
                    # Use origin point for baseline positioning
                    pos = fitz.Point(origin[0], origin[1])

                # Add text
                tw.append(pos, seg["translation"], font=font, fontsize=fontsize)

                # Write with rotation if needed
                if rotation != 0:
                    pivot = pos
                    matrix = fitz.Matrix(rotation)
                    tw.write_text(page, color=color, morph=(pivot, matrix))
                    stats["rotated"] += 1
                else:
                    tw.write_text(page, color=color)

                stats["applied"] += 1

            except Exception as e:
                stats["errors"].append(f"Write {seg.get('id')}: {e}")

    # Save
    doc.save(output_path, garbage=4, deflate=True)
    doc.close()

    stats["output_path"] = output_path

    return stats


def show(json_path: str, max_segments: int = 20) -> None:
    """
    Display segments from a JSON file.

    Args:
        json_path: Path to JSON file
        max_segments: Maximum segments to show
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"\nSource: {data.get('source', 'N/A')}")
    print(f"Pages: {data.get('pages', 0)}")
    print(f"Total segments: {len(data.get('segments', []))}")

    translated = sum(1 for s in data.get("segments", [])
                    if s.get("translation", "").strip()
                    and s.get("translation") != s.get("text"))
    print(f"Translated: {translated}")

    print(f"\nSegments (first {max_segments}):")
    print("-" * 60)

    for seg in data.get("segments", [])[:max_segments]:
        seg_id = seg.get("id", "?")
        text = seg.get("text", "")[:50]
        trans = seg.get("translation", "")[:50]
        status = "✓" if trans and trans != seg.get("text", "") else " "

        print(f"[{seg_id:3}] {status} {text}...")
        if trans:
            print(f"       → {trans}...")
        print()


def stats(json_path: str) -> dict:
    """
    Get statistics from a JSON file.

    Args:
        json_path: Path to JSON file

    Returns:
        Statistics dictionary
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    segments = data.get("segments", [])
    total = len(segments)

    translated = sum(1 for s in segments
                    if s.get("translation", "").strip()
                    and s.get("translation") != s.get("text"))

    return {
        "source": data.get("source", ""),
        "pages": data.get("pages", 0),
        "total_segments": total,
        "translated": translated,
        "untranslated": total - translated,
        "percentage": round(translated / total * 100, 1) if total > 0 else 0,
    }


def translate(
    json_path: str,
    source_lang: str = "auto",
    target_lang: str = "en",
    batch_size: int = 50,
    skip_short: int = 2,
    preserve_numbers: bool = True,
) -> dict:
    """
    Auto-translate all segments in a JSON file.

    Uses Google Translate via deep-translator library.

    Args:
        json_path: Path to JSON file with segments
        source_lang: Source language code (e.g., 'it', 'de', 'auto')
        target_lang: Target language code (e.g., 'en', 'sq', 'it')
        batch_size: Number of segments to translate at once
        skip_short: Skip segments shorter than this (likely not text)
        preserve_numbers: Don't translate segments that are only numbers

    Returns:
        Statistics dictionary

    Language codes:
        'auto' - Auto-detect
        'it' - Italian
        'en' - English
        'de' - German
        'sq' - Albanian
        'fr' - French
        'es' - Spanish
        ... (see Google Translate for full list)

    Example:
        >>> from pdftradoc.extractor import extract, translate, apply
        >>> extract("document.pdf", "segments.json")
        >>> translate("segments.json", source_lang="it", target_lang="sq")
        >>> apply("document.pdf", "segments.json", "translated.pdf")
    """
    from deep_translator import GoogleTranslator
    import time

    # Load JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    segments = data.get("segments", [])

    stats = {
        "total": len(segments),
        "translated": 0,
        "skipped": 0,
        "errors": [],
    }

    # Create translator
    translator = GoogleTranslator(source=source_lang, target=target_lang)

    # Collect segments to translate
    to_translate = []
    indices = []

    for i, seg in enumerate(segments):
        text = seg.get("text", "").strip()

        # Skip empty
        if not text:
            stats["skipped"] += 1
            continue

        # Skip very short
        if len(text) < skip_short:
            stats["skipped"] += 1
            continue

        # Skip numbers only
        if preserve_numbers and text.replace(".", "").replace(",", "").replace(" ", "").replace("-", "").replace("/", "").isdigit():
            stats["skipped"] += 1
            continue

        # Skip watermarks and common PDF generator signatures
        watermarks = [
            "powered by", "tcpdf", "fpdf", "pdflib", "itext", "reportlab",
            "generated by", "created with", "made with", "produced by",
            "www.tcpdf.org", "www.fpdf.org"
        ]
        text_lower = text.lower()
        if any(wm in text_lower for wm in watermarks):
            stats["skipped"] += 1
            continue

        # Skip if already translated
        if seg.get("translation", "").strip():
            stats["skipped"] += 1
            continue

        to_translate.append(text)
        indices.append(i)

    # Translate in batches
    for batch_start in range(0, len(to_translate), batch_size):
        batch_end = min(batch_start + batch_size, len(to_translate))
        batch_texts = to_translate[batch_start:batch_end]
        batch_indices = indices[batch_start:batch_end]

        try:
            # Translate batch
            translations = translator.translate_batch(batch_texts)

            # Apply translations
            for idx, trans in zip(batch_indices, translations):
                if trans:
                    segments[idx]["translation"] = trans
                    stats["translated"] += 1

            # Small delay to avoid rate limiting
            if batch_end < len(to_translate):
                time.sleep(0.5)

        except Exception as e:
            # Fall back to one-by-one translation
            for idx, text in zip(batch_indices, batch_texts):
                try:
                    trans = translator.translate(text)
                    if trans:
                        segments[idx]["translation"] = trans
                        stats["translated"] += 1
                except Exception as e2:
                    stats["errors"].append(f"Segment {idx}: {e2}")
                time.sleep(0.1)

    # Save updated JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return stats


def apply_overlay(
    pdf_path: str,
    json_path: str,
    output_path: str,
    dpi: int = 150,
    font_path: Optional[str] = None,
) -> dict:
    """
    Apply translations using overlay approach (image background + text overlay).

    This approach:
    1. Converts each page to a high-resolution image
    2. Creates a new PDF with the image as background
    3. Overlays translated text at the correct positions

    More reliable than redaction for complex PDFs.

    Args:
        pdf_path: Path to the original PDF
        json_path: Path to JSON file with translations
        output_path: Path for the output PDF
        dpi: Resolution for page images (higher = better quality, larger file)
        font_path: Optional path to a TTF font file for better character support

    Returns:
        Dictionary with application statistics

    Example:
        >>> apply_overlay("document.pdf", "segments.json", "translated.pdf", dpi=200)
    """
    from PIL import Image
    import io

    # Load JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    doc = fitz.open(pdf_path)
    output_doc = fitz.open()  # New empty PDF

    # Load custom font if provided
    custom_font = None
    if font_path:
        try:
            custom_font = fitz.Font(fontfile=font_path)
        except Exception:
            pass

    stats = {
        "total": len(data.get("segments", [])),
        "translated": 0,
        "applied": 0,
        "pages_processed": 0,
        "errors": [],
    }

    # Group segments by page
    by_page: Dict[int, List[dict]] = {}
    for seg in data.get("segments", []):
        translation = seg.get("translation", "").strip()
        original = seg.get("text", "").strip()

        if not translation or translation == original:
            continue

        stats["translated"] += 1
        page_num = seg.get("page", 0)
        if page_num not in by_page:
            by_page[page_num] = []
        by_page[page_num].append(seg)

    # Process each page
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_rect = page.rect

        # Get segments for this page
        page_segments = by_page.get(page_num, [])

        if not page_segments:
            # No translations - just copy the page as-is
            output_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        else:
            # Convert page to image
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            # Create new page with same dimensions
            new_page = output_doc.new_page(
                width=page_rect.width,
                height=page_rect.height
            )

            # Insert the image as background (covering text areas with white first)
            # First, draw white rectangles over text areas we'll replace
            for seg in page_segments:
                bbox = seg.get("bbox", [0, 0, 0, 0])
                rect = fitz.Rect(bbox)
                # Expand slightly to cover any edges
                rect = rect + (-1, -1, 1, 1)
                shape = new_page.new_shape()
                shape.draw_rect(rect)
                shape.finish(color=(1, 1, 1), fill=(1, 1, 1))
                shape.commit()

            # Now insert the original page image
            img_rect = fitz.Rect(0, 0, page_rect.width, page_rect.height)
            new_page.insert_image(img_rect, pixmap=pix, overlay=False)

            # Draw white boxes over text areas (on top of image)
            for seg in page_segments:
                bbox = seg.get("bbox", [0, 0, 0, 0])
                rect = fitz.Rect(bbox)
                rect = rect + (-1, -1, 1, 1)
                shape = new_page.new_shape()
                shape.draw_rect(rect)
                shape.finish(color=(1, 1, 1), fill=(1, 1, 1))
                shape.commit()

            # Now write translated text
            for seg in page_segments:
                try:
                    bbox = seg.get("bbox", [0, 0, 0, 0])
                    origin = seg.get("origin", [bbox[0], bbox[3]])
                    original_size = seg.get("size", 11)
                    color = tuple(seg.get("color", [0, 0, 0]))
                    rotation = seg.get("rotation", 0)
                    is_bold = seg.get("bold", False)
                    is_italic = seg.get("italic", False)

                    # Select font
                    if custom_font:
                        font = custom_font
                        calc_fontname = "helv"
                    else:
                        fontname = _get_base14_font(
                            seg.get("font", "Helvetica"), is_bold, is_italic
                        )
                        font = fitz.Font(fontname)
                        calc_fontname = fontname

                    # Calculate font size to fit
                    if rotation in (90, -90, 270, -270):
                        virtual_width = bbox[3] - bbox[1]
                        virtual_bbox = [bbox[0], bbox[1], bbox[0] + virtual_width, bbox[3]]
                    else:
                        virtual_bbox = bbox

                    fontsize, _ = _calculate_font_and_bbox(
                        seg["translation"], calc_fontname, virtual_bbox, original_size
                    )

                    # Create text writer
                    tw = fitz.TextWriter(new_page.rect)

                    # Determine position
                    if rotation == 90 or rotation == -270:
                        pos = fitz.Point(bbox[2], bbox[1])
                    elif rotation == -90 or rotation == 270:
                        pos = fitz.Point(bbox[0], bbox[3])
                    elif rotation == 180 or rotation == -180:
                        pos = fitz.Point(bbox[2], bbox[3])
                    else:
                        pos = fitz.Point(origin[0], origin[1])

                    # Add text
                    tw.append(pos, seg["translation"], font=font, fontsize=fontsize)

                    # Write with rotation if needed
                    if rotation != 0:
                        pivot = pos
                        matrix = fitz.Matrix(rotation)
                        tw.write_text(new_page, color=color, morph=(pivot, matrix))
                    else:
                        tw.write_text(new_page, color=color)

                    stats["applied"] += 1

                except Exception as e:
                    stats["errors"].append(f"Segment {seg.get('id')}: {e}")

        stats["pages_processed"] += 1

    # Save output
    output_doc.save(output_path, garbage=4, deflate=True)
    output_doc.close()
    doc.close()

    stats["output_path"] = output_path
    return stats


def translate_pdf(
    pdf_path: str,
    output_path: str,
    source_lang: str = "auto",
    target_lang: str = "en",
    json_path: Optional[str] = None,
) -> dict:
    """
    Complete PDF translation workflow in one function.

    Extracts text, translates it, and applies to PDF.

    Args:
        pdf_path: Path to input PDF
        output_path: Path for translated PDF
        source_lang: Source language code (e.g., 'it', 'de', 'auto')
        target_lang: Target language code (e.g., 'en', 'sq', 'it')
        json_path: Optional path for intermediate JSON (default: auto-generated)

    Returns:
        Statistics dictionary

    Example:
        >>> from pdftradoc.extractor import translate_pdf
        >>> translate_pdf("document.pdf", "translated.pdf", "it", "sq")
    """
    import tempfile
    import os

    # Generate temp JSON path if not provided
    if json_path is None:
        temp_dir = tempfile.gettempdir()
        base_name = Path(pdf_path).stem
        json_path = os.path.join(temp_dir, f"{base_name}_segments.json")

    # Step 1: Extract
    extract_stats = extract(pdf_path, json_path)

    # Step 2: Translate
    translate_stats = translate(json_path, source_lang, target_lang)

    # Step 3: Apply
    apply_stats = apply(pdf_path, json_path, output_path)

    return {
        "extracted": extract_stats["segments"],
        "translated": translate_stats["translated"],
        "applied": apply_stats["applied"],
        "errors": translate_stats["errors"] + apply_stats["errors"],
        "json_path": json_path,
        "output_path": output_path,
    }
