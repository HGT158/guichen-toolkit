# PythonProject Script Toolkit | 脚本工具合集

EN: A personal toolbox of Python scripts for automation, image processing, and model list management.  
中文：一个个人 Python 脚本仓库，用于自动化、小工具处理、图片处理和模型列表管理。

## Project Structure | 项目结构

- `finalshell破解.py`
- `openrouter模型自动获取.py`
- `图片转latex(知乎 如何评价知乎修改经典惊喜表情？）.py`
- `批量复制图片.py`
- `openrouter_models/`
  - `models.txt`
  - `models_comma.txt`
  - `models_openai.json`
  - `models_pure.txt`
- `img.png`, `.jpg`

## Script Overview | 脚本说明

### 1) `openrouter模型自动获取.py`

EN:
- Calls OpenRouter API to fetch available model IDs.
- Exports a comma-separated file `models_comma.txt` and a line-by-line file `models_pure.txt`.
- Reads API key from environment variable `OPENROUTER_API_KEY`.

中文：
- 调用 OpenRouter API 获取可用模型 ID 列表。
- 输出两个文件：逗号拼接版 `models_comma.txt` 与逐行版 `models_pure.txt`。
- API Key 通过环境变量 `OPENROUTER_API_KEY` 读取。

### 2) `图片转latex(知乎 如何评价知乎修改经典惊喜表情？）.py`

EN:
- Converts an image into LaTeX color block expressions.
- Supports color precision reduction and consecutive color merge to shorten output.
- Useful for visual/text rendering experiments in LaTeX.

中文：
- 将图片转换为 LaTeX 彩色块表达式。
- 支持颜色降精度与连续同色合并，减少输出长度。
- 适合做 LaTeX 图形文本化实验。

### 3) `批量复制图片.py`

EN:
- Recursively scans a source folder and copies image files to a target folder.
- Supports common image extensions (`.jpg`, `.jpeg`, `.png`).
- Handles filename conflicts by auto-renaming duplicate files.

中文：
- 递归扫描源目录并将图片复制到目标目录。
- 支持常见格式（`.jpg`、`.jpeg`、`.png`）。
- 遇到重名文件时自动改名，避免覆盖。

### 4) `finalshell破解.py`

EN:
- Generates hash-based code strings from machine ID for different FinalShell versions.
- Uses `pycryptodome` when available, otherwise falls back to `hashlib`.
- For learning and research only; comply with all software license terms.

中文：
- 根据机器码生成不同版本 FinalShell 对应的哈希字符串。
- 优先使用 `pycryptodome`，不可用时回退到 `hashlib`。
- 仅用于学习与研究，请遵守软件许可与法律法规。

## Requirements | 运行环境

EN:
- Python 3.9+
- Recommended packages: `requests`, `Pillow`
- Optional package: `pycryptodome`

中文：
- Python 3.9 及以上
- 推荐依赖：`requests`、`Pillow`
- 可选依赖：`pycryptodome`

Install dependencies | 安装依赖：

```bash
pip install requests pillow pycryptodome
```

## Usage | 使用方式

### OpenRouter API script | OpenRouter 脚本

PowerShell:

```powershell
$env:OPENROUTER_API_KEY="your_api_key_here"
python .\openrouter模型自动获取.py
```

### Batch image copy script | 批量复制图片脚本

EN: Edit `source_folder` and `target_folder` in `批量复制图片.py`, then run the script.  
中文：先在 `批量复制图片.py` 中修改 `source_folder` 和 `target_folder`，再运行脚本。

### Image to LaTeX script | 图片转 LaTeX 脚本

EN: Update `img_path` and size parameters in the script, then run it to print LaTeX output.  
中文：修改脚本中的 `img_path` 与尺寸参数，运行后会在控制台输出 LaTeX 表达式。

## Git Backup | Git 备份

```bash
git add .
git commit -m "update scripts"
git push
```

Remote | 远程仓库：`https://github.com/HGT158/guichen-toolkit.git`
