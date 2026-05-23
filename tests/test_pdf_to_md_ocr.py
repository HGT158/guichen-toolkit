from pathlib import Path

from pdf_to_md_ocr import (
    build_markdown,
    default_output_path,
    find_default_pdf,
    rapidocr_result_to_text,
)


def test_default_output_path_uses_pdf_stem():
    pdf_path = Path("paper.pdf")

    assert default_output_path(pdf_path) == Path("paper.md")


def test_find_default_pdf_uses_agenticrag_pattern(tmp_path):
    expected = tmp_path / (
        "Suresh sample - 2026 - AgenticRAG Agentic Retrieval "
        "for Enterprise Knowledge Bases.pdf"
    )
    expected.write_bytes(b"%PDF-1.7")
    (tmp_path / "other.pdf").write_bytes(b"%PDF-1.7")

    assert find_default_pdf(tmp_path) == expected


def test_rapidocr_result_to_text_accepts_common_result_shapes():
    result = [
        ([[0, 0], [1, 0], [1, 1], [0, 1]], "Figure title", 0.98),
        ("Axis label", 0.91),
    ]

    assert rapidocr_result_to_text(result) == "Figure title\nAxis label"


def test_build_markdown_keeps_page_text_and_image_ocr():
    markdown = build_markdown(
        "AgenticRAG",
        [
            {
                "page_number": 1,
                "text": "Main PDF text",
                "images": [
                    {"index": 1, "ocr_text": "Diagram node A\nDiagram node B"},
                    {"index": 2, "ocr_text": ""},
                ],
            }
        ],
    )

    assert "# AgenticRAG" in markdown
    assert "## Page 1" in markdown
    assert "Main PDF text" in markdown
    assert "### Image 1 OCR" in markdown
    assert "Diagram node A\nDiagram node B" in markdown
    assert "### Image 2 OCR" in markdown
    assert "_No OCR text detected._" in markdown
