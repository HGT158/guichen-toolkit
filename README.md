# PythonProject 脚本工具合集

[English](README_EN.md) | 中文

一个个人 Python 脚本仓库，用于自动化、小工具处理、图片处理、OCR 文档转换和模型列表管理。

## 项目结构

```text
.
├── pdf_to_md_ocr.py              # PDF 转 Markdown + OCR
├── pdf2md/                       # PDF 批量转换输入/输出目录
│   ├── source/                   # 放入待转换 PDF
│   └── result/                   # 输出 Markdown
├── main - retry.py               # 对分易自动签到（Tkinter GUI）
├── openrouter模型自动获取.py      # OpenRouter 模型列表获取
├── 图片转latex(…).py             # 图片转 LaTeX 彩色块
├── 批量复制图片.py                # 递归批量复制图片
├── finalshell破解.py             # FinalShell 激活码计算
├── openrouter_models/            # 模型列表输出目录
│   ├── models.txt
│   ├── models_comma.txt
│   ├── models_openai.json
│   └── models_pure.txt
├── tests/                        # 单元测试
│   └── test_pdf_to_md_ocr.py
├── README.md                     # 中文说明
└── README_EN.md                  # 英文说明
```

## 脚本说明

### 1. `pdf_to_md_ocr.py`

将 PDF 转换为结构化 Markdown，并对每张嵌入图片执行 OCR 识别。

- 使用 PyMuPDF (`fitz`) 提取页面文字。
- 使用 RapidOCR 对 PDF 中的嵌入图片进行文字识别。
- 默认批量读取 `pdf2md/source/` 中的所有 `.pdf` 文件。
- 转换结果自动保存到 `pdf2md/result/`，文件名与 PDF 同名，扩展名为 `.md`。
- 支持通过 `--no-image-ocr` 跳过图片 OCR。

```bash
python pdf_to_md_ocr.py
python pdf_to_md_ocr.py --no-image-ocr
```

使用方式：

1. 将 PDF 文件放入 `pdf2md/source/`。
2. 运行 `python pdf_to_md_ocr.py`。
3. 在 `pdf2md/result/` 查看生成的 Markdown 文件。

### 2. `main - retry.py`

基于 Tkinter 的对分易平台自动签到桌面客户端。

- 支持账号密码登录。
- 支持微信授权链接登录。
- 自动监听数字签到、二维码签到和定位签到。
- Session 过期后支持自动重连。
- 支持配置签到比例阈值，达到指定比例后再自动签到。

```bash
python "main - retry.py"
```

启动 GUI 界面后，登录账号、选择课程，再点击开始监听即可。

### 3. `openrouter模型自动获取.py`

调用 OpenRouter API 获取可用模型 ID 列表。

- API Key 从环境变量 `OPENROUTER_API_KEY` 读取。
- 输出逗号拼接版模型列表：`models_comma.txt`。
- 输出逐行模型列表：`models_pure.txt`。

PowerShell 示例：

```powershell
$env:OPENROUTER_API_KEY="your_api_key_here"
python .\openrouter模型自动获取.py
```

### 4. `图片转latex(知乎 如何评价知乎修改经典惊喜表情？）.py`

将图片转换为 LaTeX 彩色块表达式。

- 支持降低 RGB 颜色精度。
- 支持合并连续同色块，减少输出长度。
- 适合做 LaTeX 图形文本化、像素风表达或可视化实验。

使用前需要在脚本中修改：

- `img_path`：输入图片路径。
- `img_size`：缩放后的图片尺寸。
- `block_size`：色块大小。
- `prec_lv`：颜色精度等级。

### 5. `批量复制图片.py`

递归扫描源目录，并将图片文件复制到目标目录。

- 支持 `.jpg`、`.jpeg`、`.png` 等常见图片格式。
- 遇到目标目录中存在同名文件时，会自动重命名，避免覆盖。
- 适合从多级目录中集中整理图片素材。

使用前需要在脚本中修改：

- `source_folder`：源目录。
- `target_folder`：目标目录。

### 6. `finalshell破解.py`

根据机器码生成不同版本 FinalShell 对应的哈希字符串。

- 支持 FinalShell `< 3.9.6`。
- 支持 FinalShell `>= 3.9.6`。
- 支持 FinalShell `4.5`、`4.6`。
- 优先使用 `pycryptodome`，不可用时回退到 `hashlib`。

```bash
python finalshell破解.py
```

运行后按照提示输入机器码即可。

仅用于学习与研究，请遵守软件许可与法律法规。

## 运行环境

- Python 3.9 及以上
- 核心依赖：`requests`、`Pillow`、`PyMuPDF`、`RapidOCR`、`beautifulsoup4`
- 可选依赖：`pycryptodome`

安装依赖：

```bash
pip install requests pillow pymupdf rapidocr_onnxruntime beautifulsoup4 pycryptodome
```

## 测试

```bash
python -m pytest tests/
```

## Git 备份

```bash
git add .
git commit -m "update scripts"
git push
```

远程仓库：`https://github.com/HGT158/guichen-toolkit.git`
