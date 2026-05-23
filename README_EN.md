# PythonProject Script Toolkit

English | [中文](README.md)

A personal Python script repository for automation, utility scripts, image processing, OCR document conversion, and model list management.

## Project Structure

```text
.
├── pdf_to_md_ocr.py              # PDF to Markdown + OCR
├── pdf2md/                       # Batch PDF conversion input/output folders
│   ├── source/                   # Put source PDFs here
│   └── result/                   # Generated Markdown files
├── main - retry.py               # Duifene auto sign-in (Tkinter GUI)
├── openrouter模型自动获取.py      # OpenRouter model list fetcher
├── 图片转latex(…).py             # Image to LaTeX color blocks
├── 批量复制图片.py                # Recursive batch image copier
├── finalshell破解.py             # FinalShell activation-code calculator
├── openrouter_models/            # Model list output directory
│   ├── models.txt
│   ├── models_comma.txt
│   ├── models_openai.json
│   └── models_pure.txt
├── tests/                        # Unit tests
│   └── test_pdf_to_md_ocr.py
├── README.md                     # Chinese documentation
└── README_EN.md                  # English documentation
```

## Script Overview

### 1. `pdf_to_md_ocr.py`

Converts a PDF into structured Markdown and performs OCR on every embedded image.

- Extracts page text with PyMuPDF (`fitz`).
- Runs RapidOCR on embedded PDF images.
- Batch reads all `.pdf` files from `pdf2md/source/` by default.
- Saves generated Markdown files to `pdf2md/result/` with the same base filename as each PDF.
- Supports `--no-image-ocr` to skip image OCR.

```bash
python pdf_to_md_ocr.py
python pdf_to_md_ocr.py --no-image-ocr
```

Usage:

1. Put PDF files into `pdf2md/source/`.
2. Run `python pdf_to_md_ocr.py`.
3. Check generated Markdown files in `pdf2md/result/`.

### 2. `main - retry.py`

A Tkinter desktop client for automated check-in on the Duifene education platform.

- Supports account/password login.
- Supports WeChat OAuth link login.
- Monitors numeric-code, QR-code, and GPS-location check-ins.
- Automatically reconnects when the session expires.
- Supports a configurable sign-in threshold before joining automatically.

```bash
python "main - retry.py"
```

Launch the GUI, log in, choose a course, and start monitoring.

### 3. `openrouter模型自动获取.py`

Fetches available model IDs from the OpenRouter API.

- Reads the API key from the `OPENROUTER_API_KEY` environment variable.
- Exports comma-separated model IDs to `models_comma.txt`.
- Exports one-model-per-line IDs to `models_pure.txt`.

PowerShell example:

```powershell
$env:OPENROUTER_API_KEY="your_api_key_here"
python .\openrouter模型自动获取.py
```

### 4. `图片转latex(知乎 如何评价知乎修改经典惊喜表情？）.py`

Converts an image into LaTeX color block expressions.

- Supports reducing RGB color precision.
- Supports merging consecutive same-color blocks to shorten output.
- Useful for LaTeX visual text rendering, pixel-art-style output, and visualization experiments.

Before running, update these values in the script:

- `img_path`: input image path.
- `img_size`: resized image dimensions.
- `block_size`: color block size.
- `prec_lv`: color precision level.

### 5. `批量复制图片.py`

Recursively scans a source directory and copies image files into a target directory.

- Supports common image formats such as `.jpg`, `.jpeg`, and `.png`.
- Automatically renames duplicate files to avoid overwriting existing files.
- Useful for collecting image assets from nested folders.

Before running, update these values in the script:

- `source_folder`: source directory.
- `target_folder`: target directory.

### 6. `finalshell破解.py`

Generates hash-based strings from a machine ID for different FinalShell versions.

- Supports FinalShell `< 3.9.6`.
- Supports FinalShell `>= 3.9.6`.
- Supports FinalShell `4.5` and `4.6`.
- Uses `pycryptodome` when available, otherwise falls back to `hashlib`.

```bash
python finalshell破解.py
```

Enter the machine ID when prompted.

For learning and research only. Please comply with software licenses and applicable laws.

## Requirements

- Python 3.9+
- Core dependencies: `requests`, `Pillow`, `PyMuPDF`, `RapidOCR`, `beautifulsoup4`
- Optional dependency: `pycryptodome`

Install dependencies:

```bash
pip install requests pillow pymupdf rapidocr_onnxruntime beautifulsoup4 pycryptodome
```

## Testing

```bash
python -m pytest tests/
```

## Git Backup

```bash
git add .
git commit -m "update scripts"
git push
```

Remote repository: `https://github.com/HGT158/guichen-toolkit.git`
