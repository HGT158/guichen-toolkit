# PythonProject Script Toolkit

A personal script collection for small utilities, experiments, and data processing tasks.

## Contents

- `openrouter.py`: fetch model list from OpenRouter API and export:
  - `models_comma.txt`
  - `models_pure.txt`
- `finalshell.py`: utility script related to FinalShell usage.
- `脚本.py`: custom local script.
- `图片转latex(知乎 如何评价知乎修改经典惊喜表情？）.py`: image to LaTeX related script.
- `models.txt`, `models_openai.json`: model data files.
- `img.png`, `.jpg`: local image assets.

## Requirements

- Python 3.9+
- Recommended package:
  - `requests`

Install dependency:

```bash
pip install requests
```

## OpenRouter Script Usage

`openrouter.py` requires environment variable `OPENROUTER_API_KEY`.

PowerShell:

```powershell
$env:OPENROUTER_API_KEY="your_api_key_here"
python openrouter.py
```

After running successfully, model IDs are exported to:

- `models_comma.txt`
- `models_pure.txt`

## Git Backup Workflow

Quick backup commands:

```bash
git add .
git commit -m "update scripts"
git push
```

Remote repository:

- `origin`: `https://github.com/HGT158/guichen-toolkit.git`
