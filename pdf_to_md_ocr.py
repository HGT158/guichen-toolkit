"""Convert a PDF into AI-friendly Markdown with OCR text for embedded images."""

from __future__ import annotations

import argparse
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

import fitz


DEFAULT_PDF_PATTERN = "*AgenticRAG*Enterprise Knowledge Bases.pdf"


def default_output_path(pdf_path: Path) -> Path:
    return pdf_path.with_suffix(".md")


def find_default_pdf(search_dir: Path) -> Path:
    matches = sorted(search_dir.glob(DEFAULT_PDF_PATTERN))
    if not matches:
        raise FileNotFoundError(
            f"No PDF matching {DEFAULT_PDF_PATTERN!r} found in {search_dir}"
        )
    return matches[0]


def rapidocr_result_to_text(result: Any) -> str:
    lines = _collect_ocr_text(result)
    return "\n".join(_clean_line(line) for line in lines if _clean_line(line))


def build_markdown(
    title: str,
    pages: Sequence[dict[str, Any]],
    source_pdf: str | None = None,
) -> str:
    lines: list[str] = [f"# {title}", ""]

    if source_pdf:
        lines.extend([f"_Source PDF: {source_pdf}_", ""])

    for page in pages:
        page_number = page["page_number"]
        page_text = _normalize_page_text(page.get("text", ""))

        lines.extend([f"## Page {page_number}", ""])
        lines.extend([page_text or "_No extractable page text._", ""])

        images = page.get("images", [])
        if images:
            lines.extend(["### Image OCR", ""])
            for image in images:
                image_index = image["index"]
                ocr_text = _normalize_page_text(image.get("ocr_text", ""))
                lines.extend(
                    [
                        f"#### Image {image_index} OCR",
                        "",
                        ocr_text or "_No OCR text detected._",
                        "",
                    ]
                )

    return "\n".join(lines).rstrip() + "\n"


def convert_pdf_to_markdown(
    pdf_path: Path,
    output_path: Path | None = None,
    *,
    ocr_images: bool = True,
) -> Path:
    pdf_path = pdf_path.resolve()
    if output_path is None:
        output_path = default_output_path(pdf_path)
    else:
        output_path = output_path.resolve()

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    ocr_engine = _create_ocr_engine() if ocr_images else None
    pages: list[dict[str, Any]] = []

    with fitz.open(pdf_path) as document:
        for page_index, page in enumerate(document, start=1):
            images: list[dict[str, Any]] = []
            for image_index, image_bytes in enumerate(
                _extract_page_image_bytes(document, page),
                start=1,
            ):
                ocr_text = ""
                if ocr_engine is not None:
                    try:
                        ocr_text = rapidocr_result_to_text(ocr_engine(image_bytes))
                    except Exception as exc:  # Keep the image represented in output.
                        ocr_text = f"[OCR failed: {type(exc).__name__}: {exc}]"

                images.append({"index": image_index, "ocr_text": ocr_text})

            pages.append(
                {
                    "page_number": page_index,
                    "text": page.get_text("text", sort=True),
                    "images": images,
                }
            )

    markdown = build_markdown(pdf_path.stem, pages, source_pdf=pdf_path.name)
    output_path.write_text(markdown, encoding="utf-8")
    return output_path


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a PDF to Markdown and OCR every embedded page image.",
    )
    parser.add_argument(
        "pdf",
        nargs="?",
        type=Path,
        help="PDF file to convert. Defaults to the AgenticRAG paper in this folder.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Markdown output path. Defaults to the PDF filename with .md suffix.",
    )
    parser.add_argument(
        "--no-image-ocr",
        action="store_true",
        help="Skip OCR. Embedded images are still listed with empty OCR text.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    pdf_path = args.pdf or find_default_pdf(Path(__file__).parent)
    output_path = convert_pdf_to_markdown(
        pdf_path,
        args.output,
        ocr_images=not args.no_image_ocr,
    )
    print(f"Wrote Markdown: {output_path}")
    return 0


def _create_ocr_engine() -> Any:
    from rapidocr import RapidOCR

    return RapidOCR()


def _extract_page_image_bytes(document: fitz.Document, page: fitz.Page) -> Iterable[bytes]:
    for image_info in page.get_images(full=True):
        xref = image_info[0]
        pixmap = fitz.Pixmap(document, xref)
        if pixmap.alpha or pixmap.n >= 5:
            pixmap = fitz.Pixmap(fitz.csRGB, pixmap)
        yield pixmap.tobytes("png")


def _collect_ocr_text(value: Any) -> list[str]:
    if value is None:
        return []

    txts = getattr(value, "txts", None)
    if txts is not None:
        return _collect_ocr_text(txts)

    if isinstance(value, str):
        return [value]

    if isinstance(value, dict):
        for key in ("text", "txt", "rec_text", "label"):
            if key in value:
                return _collect_ocr_text(value[key])
        collected: list[str] = []
        for item in value.values():
            collected.extend(_collect_ocr_text(item))
        return collected

    if isinstance(value, tuple):
        if len(value) >= 2 and isinstance(value[1], str):
            return [value[1]]
        if len(value) >= 1 and isinstance(value[0], str):
            return [value[0]]

    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
        collected = []
        for item in value:
            collected.extend(_collect_ocr_text(item))
        return collected

    return []


def _normalize_page_text(text: str) -> str:
    normalized_lines = [_clean_line(line) for line in text.splitlines()]
    return "\n".join(line for line in normalized_lines if line).strip()


def _clean_line(line: str) -> str:
    return " ".join(str(line).strip().split())


if __name__ == "__main__":
    raise SystemExit(main())
