"""
PDF Segment Extractor - Simple JSON-based workflow.

Three simple functions:
1. extract(pdf_path, json_path) - Extract segments from PDF to JSON
2. translate(json_path, source_lang, target_lang) - Auto-translate segments
3. apply(pdf_path, json_path, output_path) - Apply JSON translations to PDF

Or use the all-in-one function:
- translate_pdf(pdf_path, output_path, source_lang, target_lang) - Complete workflow

Additional utilities:
- merge_segments(json_path, ...) - Merge nearby segments on same line
- verify_with_ocr(pdf_path, json_path, ...) - Verify extraction with OCR
- analyze_segmentation(json_path) - Analyze segmentation quality
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List, Any, Optional
import fitz


def extract(
    pdf_path: str,
    json_path: str,
    merge: bool = False,
    verify_ocr: bool = False,
    ocr_lang: str = "ita+eng",
    merge_gap: float = 15.0,
) -> dict:
    """
    Extract all text segments from a PDF and save to JSON.

    Args:
        pdf_path: Path to the PDF file
        json_path: Path where to save the JSON file
        merge: If True, automatically merge nearby segments on same line
        verify_ocr: If True, verify extraction with OCR and mark discrepancies
        ocr_lang: Tesseract language code for OCR verification (e.g., 'ita', 'eng')
        merge_gap: Maximum horizontal gap in pixels to merge segments (default: 15)

    Returns:
        Dictionary with extraction statistics

    Example:
        >>> from pdftradoc.extractor import extract, apply
        >>> # Basic extraction
        >>> extract("document.pdf", "segments.json")
        >>>
        >>> # With merge and OCR verification
        >>> extract("document.pdf", "segments.json", merge=True, verify_ocr=True)
        >>>
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

    # Save JSON (initial)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    result = {
        "segments": len(output["segments"]),
        "pages": output["pages"],
        "json_path": json_path,
    }

    # Optional: Merge nearby segments
    if merge:
        merge_result = merge_segments(json_path, max_gap=merge_gap)
        result["merged"] = merge_result["merged"]
        result["segments_after_merge"] = merge_result["final"]

    # Optional: Verify with OCR
    if verify_ocr:
        ocr_result = _verify_extraction_with_ocr(pdf_path, json_path, ocr_lang)
        result["ocr_verification"] = ocr_result

    return result


def _verify_extraction_with_ocr(pdf_path: str, json_path: str, ocr_lang: str) -> dict:
    """
    Internal function to verify extraction with OCR and AUTO-CORRECT fragmented segments.

    If OCR detects a complete phrase where extraction has fragments, it merges them
    and replaces the text with the OCR-detected complete phrase.
    """
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return {"error": "pytesseract not installed", "verified": 0}

    # Load JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    doc = fitz.open(pdf_path)
    segments = data.get("segments", [])

    stats = {
        "verified": 0,
        "matches": 0,
        "corrected": 0,  # Segments corrected by OCR
        "merged_by_ocr": 0,  # Fragments merged into complete phrases
        "flagged_segments": [],
    }

    # Group by page
    by_page: Dict[int, List[int]] = {}
    for i, seg in enumerate(segments):
        page_num = seg.get("page", 0)
        if page_num not in by_page:
            by_page[page_num] = []
        by_page[page_num].append(i)

    dpi = 300
    scale = dpi / 72

    # Track segments to merge
    segments_to_remove = set()

    for page_num, seg_indices in by_page.items():
        page = doc[page_num]

        # Render page once
        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Sort segments by position (y then x)
        sorted_indices = sorted(
            seg_indices,
            key=lambda i: (segments[i]["bbox"][1], segments[i]["bbox"][0])
        )

        i = 0
        while i < len(sorted_indices):
            idx = sorted_indices[i]
            if idx in segments_to_remove:
                i += 1
                continue

            seg = segments[idx]
            bbox = seg.get("bbox", [0, 0, 0, 0])
            extracted_text = seg.get("text", "").strip()

            # Skip very short
            if len(extracted_text) < 2:
                i += 1
                continue

            # Scale bbox for OCR
            x0 = max(0, int(bbox[0] * scale) - 2)
            y0 = max(0, int(bbox[1] * scale) - 2)
            x1 = min(img.width, int(bbox[2] * scale) + 2)
            y1 = min(img.height, int(bbox[3] * scale) + 2)

            if x1 <= x0 or y1 <= y0:
                i += 1
                continue

            # OCR single segment first
            region = img.crop((x0, y0, x1, y1))
            try:
                ocr_text = pytesseract.image_to_string(
                    region, lang=ocr_lang, config="--psm 7"
                ).strip()
            except Exception:
                ocr_text = ""

            stats["verified"] += 1

            # Check if OCR detected more words than extracted
            extracted_words = len(extracted_text.split())
            ocr_words = len(ocr_text.split()) if ocr_text else 0

            # If OCR found more content, try expanding to include adjacent segments
            if ocr_words > extracted_words and ocr_text:
                # Look for adjacent segments on same line to potentially merge
                merged_indices = [idx]
                merged_bbox = list(bbox)

                # Check next segments on same line
                for j in range(i + 1, min(i + 5, len(sorted_indices))):
                    next_idx = sorted_indices[j]
                    if next_idx in segments_to_remove:
                        continue
                    next_seg = segments[next_idx]
                    next_bbox = next_seg.get("bbox", [0, 0, 0, 0])

                    # Check if on same line (y similar)
                    y_diff = abs(bbox[1] - next_bbox[1])
                    if y_diff > 8:  # Different line
                        break

                    # Check horizontal proximity
                    x_gap = next_bbox[0] - merged_bbox[2]
                    if x_gap > 30:  # Too far apart
                        break

                    # Expand merged bbox
                    merged_bbox[2] = max(merged_bbox[2], next_bbox[2])
                    merged_bbox[3] = max(merged_bbox[3], next_bbox[3])
                    merged_indices.append(next_idx)

                # If we found segments to merge, OCR the combined area
                if len(merged_indices) > 1:
                    # OCR the combined area
                    cx0 = max(0, int(merged_bbox[0] * scale) - 2)
                    cy0 = max(0, int(merged_bbox[1] * scale) - 2)
                    cx1 = min(img.width, int(merged_bbox[2] * scale) + 2)
                    cy1 = min(img.height, int(merged_bbox[3] * scale) + 2)

                    combined_region = img.crop((cx0, cy0, cx1, cy1))
                    try:
                        combined_ocr = pytesseract.image_to_string(
                            combined_region, lang=ocr_lang, config="--psm 7"
                        ).strip()
                    except Exception:
                        combined_ocr = ""

                    # Combine extracted texts
                    combined_extracted = " ".join(
                        segments[mi].get("text", "") for mi in merged_indices
                    )

                    # If OCR gives a cleaner result, use it
                    if combined_ocr and len(combined_ocr) >= len(combined_extracted) * 0.8:
                        # Update first segment with merged data
                        seg["text"] = combined_ocr
                        seg["bbox"] = merged_bbox
                        seg["_ocr_corrected"] = True
                        seg["_original_text"] = extracted_text
                        seg["_merged_count"] = len(merged_indices)

                        # Mark other segments for removal
                        for mi in merged_indices[1:]:
                            segments_to_remove.add(mi)

                        stats["merged_by_ocr"] += len(merged_indices) - 1
                        stats["corrected"] += 1
                        stats["matches"] += 1
                        i += 1
                        continue

            # Standard comparison for non-merged segments
            extracted_norm = "".join(extracted_text.lower().split())
            ocr_norm = "".join(ocr_text.lower().split()) if ocr_text else ""

            if not ocr_norm:
                seg["_ocr_status"] = "empty"
            elif extracted_norm == ocr_norm:
                seg["_ocr_status"] = "match"
                stats["matches"] += 1
            elif ocr_norm in extracted_norm:
                seg["_ocr_status"] = "match"
                stats["matches"] += 1
            elif extracted_norm in ocr_norm:
                # OCR found more - replace with OCR text
                seg["_ocr_status"] = "corrected"
                seg["_original_text"] = extracted_text
                seg["text"] = ocr_text
                seg["_ocr_corrected"] = True
                stats["corrected"] += 1
            else:
                # Calculate similarity
                common = sum(1 for a, b in zip(extracted_norm, ocr_norm) if a == b)
                max_len = max(len(extracted_norm), len(ocr_norm))
                similarity = common / max_len if max_len > 0 else 0

                if similarity > 0.8:
                    seg["_ocr_status"] = "match"
                    stats["matches"] += 1
                elif similarity > 0.5 and len(ocr_text) > len(extracted_text):
                    # OCR is probably more complete, use it
                    seg["_ocr_status"] = "corrected"
                    seg["_original_text"] = extracted_text
                    seg["text"] = ocr_text
                    seg["_ocr_corrected"] = True
                    stats["corrected"] += 1
                else:
                    seg["_ocr_status"] = "uncertain"
                    seg["_ocr_text"] = ocr_text
                    stats["flagged_segments"].append(seg.get("id"))

            i += 1

    doc.close()

    # Remove merged segments
    if segments_to_remove:
        data["segments"] = [
            seg for i, seg in enumerate(segments)
            if i not in segments_to_remove
        ]
        # Renumber IDs
        for new_id, seg in enumerate(data["segments"]):
            seg["id"] = new_id

    # Save updated JSON
    data["_ocr_verification"] = {
        "verified": stats["verified"],
        "matches": stats["matches"],
        "corrected": stats["corrected"],
        "merged_by_ocr": stats["merged_by_ocr"],
        "segments_removed": len(segments_to_remove),
        "final_segments": len(data["segments"]),
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return stats


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


def analyze_segmentation(json_path: str) -> dict:
    """
    Analyze segmentation quality of extracted segments.

    Identifies potential issues like:
    - Single character segments
    - Very short segments (likely fragmented)
    - Segments that could be merged

    Args:
        json_path: Path to JSON file with segments

    Returns:
        Dictionary with analysis results

    Example:
        >>> from pdftradoc import extract, analyze_segmentation
        >>> extract("document.pdf", "segments.json")
        >>> analysis = analyze_segmentation("segments.json")
        >>> print(f"Single chars: {analysis['single_chars']}")
        >>> print(f"Short segments: {analysis['short_segments']}")
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    segments = data.get("segments", [])

    single_chars = []
    short_segments = []  # 2-3 chars
    normal_segments = []  # 4+ chars
    mergeable_pairs = []

    # Group by page for merge detection
    by_page: Dict[int, List[dict]] = {}
    for seg in segments:
        page_num = seg.get("page", 0)
        if page_num not in by_page:
            by_page[page_num] = []
        by_page[page_num].append(seg)

    # Analyze each segment
    for seg in segments:
        text = seg.get("text", "").strip()
        length = len(text)

        if length == 1:
            single_chars.append({
                "id": seg.get("id"),
                "text": text,
                "page": seg.get("page"),
                "bbox": seg.get("bbox"),
            })
        elif length <= 3:
            short_segments.append({
                "id": seg.get("id"),
                "text": text,
                "page": seg.get("page"),
                "bbox": seg.get("bbox"),
            })
        else:
            normal_segments.append(seg.get("id"))

    # Find mergeable segments (same line, close together)
    for page_num, page_segs in by_page.items():
        # Sort by y position then x position
        sorted_segs = sorted(page_segs, key=lambda s: (s["bbox"][1], s["bbox"][0]))

        for i in range(len(sorted_segs) - 1):
            seg1 = sorted_segs[i]
            seg2 = sorted_segs[i + 1]

            bbox1 = seg1["bbox"]
            bbox2 = seg2["bbox"]

            # Check if on same line (y similar within 5 pixels)
            y_diff = abs(bbox1[1] - bbox2[1])
            if y_diff > 5:
                continue

            # Check horizontal gap (should be small, < 20 pixels)
            x_gap = bbox2[0] - bbox1[2]  # gap between end of seg1 and start of seg2
            if 0 < x_gap < 20:
                mergeable_pairs.append({
                    "seg1_id": seg1.get("id"),
                    "seg2_id": seg2.get("id"),
                    "seg1_text": seg1.get("text", "")[:30],
                    "seg2_text": seg2.get("text", "")[:30],
                    "gap": round(x_gap, 1),
                    "page": page_num,
                })

    return {
        "total_segments": len(segments),
        "single_chars": len(single_chars),
        "short_segments": len(short_segments),
        "normal_segments": len(normal_segments),
        "mergeable_pairs": len(mergeable_pairs),
        "single_char_examples": single_chars[:10],
        "short_segment_examples": short_segments[:10],
        "mergeable_examples": mergeable_pairs[:10],
        "quality_score": round(
            (len(normal_segments) / len(segments) * 100) if segments else 0, 1
        ),
    }


def merge_segments(
    json_path: str,
    output_path: Optional[str] = None,
    max_gap: float = 15.0,
    same_line_threshold: float = 5.0,
    min_merge_length: int = 1,
) -> dict:
    """
    Merge nearby segments on the same line into single segments.

    Useful for PDFs where text is fragmented into multiple small segments.

    Args:
        json_path: Path to JSON file with segments
        output_path: Path for output JSON (default: overwrites input)
        max_gap: Maximum horizontal gap in pixels to merge (default: 15)
        same_line_threshold: Maximum vertical difference to consider same line (default: 5)
        min_merge_length: Minimum text length to consider for merging (default: 1)

    Returns:
        Dictionary with merge statistics

    Example:
        >>> from pdftradoc import extract, merge_segments, translate
        >>> extract("document.pdf", "segments.json")
        >>> merge_segments("segments.json")  # Merges in place
        >>> translate("segments.json", "it", "en")
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    segments = data.get("segments", [])

    if not segments:
        return {"merged": 0, "original": 0, "final": 0}

    original_count = len(segments)

    # Group by page
    by_page: Dict[int, List[dict]] = {}
    for seg in segments:
        page_num = seg.get("page", 0)
        if page_num not in by_page:
            by_page[page_num] = []
        by_page[page_num].append(seg)

    merged_segments = []
    merged_count = 0
    new_id = 0

    for page_num in sorted(by_page.keys()):
        page_segs = by_page[page_num]

        # Sort by y position then x position
        sorted_segs = sorted(page_segs, key=lambda s: (s["bbox"][1], s["bbox"][0]))

        # Mark segments as used
        used = set()

        for i, seg in enumerate(sorted_segs):
            if i in used:
                continue

            # Start a merge group
            group = [seg]
            used.add(i)

            # Look for segments to merge
            current_bbox = list(seg["bbox"])

            for j in range(i + 1, len(sorted_segs)):
                if j in used:
                    continue

                other = sorted_segs[j]
                other_bbox = other["bbox"]

                # Check if on same line
                y_diff = abs(current_bbox[1] - other_bbox[1])
                if y_diff > same_line_threshold:
                    break  # Past this line, no more merges possible

                # Check horizontal gap
                x_gap = other_bbox[0] - current_bbox[2]

                if 0 <= x_gap <= max_gap:
                    # Check minimum length
                    if len(other.get("text", "").strip()) >= min_merge_length:
                        group.append(other)
                        used.add(j)
                        # Expand current bbox
                        current_bbox[2] = other_bbox[2]
                        current_bbox[3] = max(current_bbox[3], other_bbox[3])
                        merged_count += 1

            # Create merged segment
            if len(group) == 1:
                # No merge, keep original
                new_seg = dict(group[0])
                new_seg["id"] = new_id
            else:
                # Merge texts and bboxes
                merged_text = " ".join(s.get("text", "") for s in group)
                # Clean up double spaces
                merged_text = " ".join(merged_text.split())

                # Use first segment's properties
                new_seg = {
                    "id": new_id,
                    "page": page_num,
                    "text": merged_text,
                    "translation": "",
                    "bbox": [
                        min(s["bbox"][0] for s in group),
                        min(s["bbox"][1] for s in group),
                        max(s["bbox"][2] for s in group),
                        max(s["bbox"][3] for s in group),
                    ],
                    "font": group[0].get("font", "Helvetica"),
                    "size": group[0].get("size", 11),
                    "color": group[0].get("color", [0, 0, 0]),
                    "bold": group[0].get("bold", False),
                    "italic": group[0].get("italic", False),
                    "rotation": group[0].get("rotation", 0),
                    "origin": group[0].get("origin", [current_bbox[0], current_bbox[3]]),
                    "_merged_from": [s.get("id") for s in group],
                }

            merged_segments.append(new_seg)
            new_id += 1

    # Update data
    data["segments"] = merged_segments

    # Save
    out_path = output_path or json_path
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return {
        "original": original_count,
        "final": len(merged_segments),
        "merged": merged_count,
        "output_path": out_path,
    }


def verify_with_ocr(
    pdf_path: str,
    json_path: str,
    output_path: Optional[str] = None,
    dpi: int = 300,
    lang: str = "ita+eng",
) -> dict:
    """
    Verify extracted segments using OCR (Optical Character Recognition).

    Compares PyMuPDF extraction with OCR results to identify discrepancies.
    Requires pytesseract and Tesseract OCR to be installed.

    Args:
        pdf_path: Path to PDF file
        json_path: Path to JSON file with extracted segments
        output_path: Optional path for verified JSON output
        dpi: Resolution for OCR (higher = more accurate, slower)
        lang: Tesseract language code (e.g., 'ita', 'eng', 'ita+eng')

    Returns:
        Dictionary with verification results

    Example:
        >>> from pdftradoc import extract, verify_with_ocr
        >>> extract("document.pdf", "segments.json")
        >>> result = verify_with_ocr("document.pdf", "segments.json")
        >>> print(f"Match rate: {result['match_rate']}%")

    Installation:
        pip install pytesseract
        # Also install Tesseract OCR:
        # macOS: brew install tesseract
        # Ubuntu: apt-get install tesseract-ocr
        # Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
    """
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return {
            "error": "pytesseract not installed. Run: pip install pytesseract",
            "verified": 0,
            "match_rate": 0,
        }

    # Load JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    doc = fitz.open(pdf_path)
    segments = data.get("segments", [])

    stats = {
        "total": len(segments),
        "verified": 0,
        "matches": 0,
        "partial_matches": 0,
        "mismatches": 0,
        "ocr_empty": 0,
        "discrepancies": [],
    }

    # Group by page
    by_page: Dict[int, List[dict]] = {}
    for i, seg in enumerate(segments):
        page_num = seg.get("page", 0)
        if page_num not in by_page:
            by_page[page_num] = []
        by_page[page_num].append((i, seg))

    # Process each page
    for page_num, page_segs in by_page.items():
        page = doc[page_num]

        # Render page at high DPI for OCR
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        scale = dpi / 72

        for idx, seg in page_segs:
            bbox = seg.get("bbox", [0, 0, 0, 0])
            extracted_text = seg.get("text", "").strip().lower()

            # Skip very short segments
            if len(extracted_text) < 2:
                continue

            # Scale bbox to image coordinates
            x0 = int(bbox[0] * scale) - 2
            y0 = int(bbox[1] * scale) - 2
            x1 = int(bbox[2] * scale) + 2
            y1 = int(bbox[3] * scale) + 2

            # Ensure valid coordinates
            x0 = max(0, x0)
            y0 = max(0, y0)
            x1 = min(img.width, x1)
            y1 = min(img.height, y1)

            if x1 <= x0 or y1 <= y0:
                continue

            # Crop region
            region = img.crop((x0, y0, x1, y1))

            # OCR the region
            try:
                ocr_text = pytesseract.image_to_string(
                    region, lang=lang, config="--psm 7"
                ).strip().lower()
            except Exception:
                ocr_text = ""

            stats["verified"] += 1

            if not ocr_text:
                stats["ocr_empty"] += 1
                continue

            # Compare texts
            # Normalize for comparison
            extracted_norm = "".join(extracted_text.split())
            ocr_norm = "".join(ocr_text.split())

            if extracted_norm == ocr_norm:
                stats["matches"] += 1
            elif extracted_norm in ocr_norm or ocr_norm in extracted_norm:
                stats["partial_matches"] += 1
            else:
                # Check similarity
                common = sum(1 for a, b in zip(extracted_norm, ocr_norm) if a == b)
                max_len = max(len(extracted_norm), len(ocr_norm))
                similarity = common / max_len if max_len > 0 else 0

                if similarity > 0.7:
                    stats["partial_matches"] += 1
                else:
                    stats["mismatches"] += 1
                    if len(stats["discrepancies"]) < 20:
                        stats["discrepancies"].append({
                            "id": seg.get("id"),
                            "page": page_num,
                            "extracted": extracted_text[:50],
                            "ocr": ocr_text[:50],
                        })

    doc.close()

    # Calculate match rate
    verified = stats["verified"]
    if verified > 0:
        stats["match_rate"] = round(
            (stats["matches"] + stats["partial_matches"]) / verified * 100, 1
        )
    else:
        stats["match_rate"] = 0

    # Optionally save verified data
    if output_path:
        data["_ocr_verification"] = {
            "match_rate": stats["match_rate"],
            "verified": stats["verified"],
            "matches": stats["matches"],
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        stats["output_path"] = output_path

    return stats


def extract_with_ocr(
    pdf_path: str,
    json_path: str,
    dpi: int = 300,
    lang: str = "ita+eng",
) -> dict:
    """
    Extract text from PDF using OCR instead of text layer.

    Useful for scanned PDFs or PDFs with unreliable text extraction.
    Requires pytesseract and Tesseract OCR to be installed.

    Args:
        pdf_path: Path to PDF file
        json_path: Path for output JSON
        dpi: Resolution for OCR (higher = more accurate, slower)
        lang: Tesseract language code (e.g., 'ita', 'eng', 'ita+eng+deu')

    Returns:
        Dictionary with extraction statistics

    Example:
        >>> from pdftradoc import extract_with_ocr, translate, apply_overlay
        >>> extract_with_ocr("scanned.pdf", "segments.json", lang="ita")
        >>> translate("segments.json", "it", "en")
        >>> apply_overlay("scanned.pdf", "segments.json", "translated.pdf")
    """
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return {
            "error": "pytesseract not installed. Run: pip install pytesseract",
            "segments": 0,
        }

    doc = fitz.open(pdf_path)

    output = {
        "source": pdf_path,
        "pages": len(doc),
        "extraction_method": "ocr",
        "ocr_lang": lang,
        "segments": [],
    }

    segment_id = 0

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Render page at high DPI
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Get OCR data with bounding boxes
        try:
            ocr_data = pytesseract.image_to_data(
                img, lang=lang, output_type=pytesseract.Output.DICT
            )
        except Exception as e:
            continue

        scale = 72 / dpi  # Convert back to PDF coordinates

        n_boxes = len(ocr_data["text"])

        # Group words into lines
        lines: Dict[int, List[dict]] = {}

        for i in range(n_boxes):
            text = ocr_data["text"][i].strip()
            if not text:
                continue

            conf = int(ocr_data["conf"][i])
            if conf < 30:  # Skip low confidence
                continue

            line_num = ocr_data["line_num"][i]
            block_num = ocr_data["block_num"][i]
            line_key = block_num * 1000 + line_num

            if line_key not in lines:
                lines[line_key] = []

            lines[line_key].append({
                "text": text,
                "x": ocr_data["left"][i] * scale,
                "y": ocr_data["top"][i] * scale,
                "w": ocr_data["width"][i] * scale,
                "h": ocr_data["height"][i] * scale,
            })

        # Create segments from lines
        for line_key in sorted(lines.keys()):
            words = lines[line_key]
            if not words:
                continue

            # Sort words by x position
            words = sorted(words, key=lambda w: w["x"])

            # Combine into line segment
            line_text = " ".join(w["text"] for w in words)

            bbox = [
                words[0]["x"],
                min(w["y"] for w in words),
                words[-1]["x"] + words[-1]["w"],
                max(w["y"] + w["h"] for w in words),
            ]

            segment = {
                "id": segment_id,
                "page": page_num,
                "text": line_text,
                "translation": "",
                "bbox": bbox,
                "font": "Helvetica",
                "size": round(bbox[3] - bbox[1], 1),
                "color": [0, 0, 0],
                "bold": False,
                "italic": False,
                "rotation": 0,
                "origin": [bbox[0], bbox[3]],
                "_ocr": True,
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
        "method": "ocr",
    }
