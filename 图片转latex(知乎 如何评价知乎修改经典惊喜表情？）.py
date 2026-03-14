from PIL import Image

def reduce_color_prec(rgb: tuple[int, int, int], levels: int = 4) -> tuple[int, int, int]:
    """降低RGB精度"""
    if levels <= 1:
        return (0, 0, 0)
    step = 255 // (levels - 1)
    return tuple(round(c / step) * step for c in rgb)

def rgb_short(rgb: tuple[int, int, int], prec_lv: int) -> str:
    """返回较短颜色表示"""
    step = 255 // (prec_lv - 1) if prec_lv > 1 else 1
    if all(c % step == 0 for c in rgb):
        comp = [c // 16 for c in rgb]
        if all(0 <= c <= 15 for c in comp):
            return f"#{''.join(f'{c:X}' for c in comp)}"
    return f"#{''.join(f'{c:02X}' for c in rgb)}"

def merge_colors(colors: list[str]) -> list[tuple[str, int]]:
    """合并连续颜色"""
    if not colors:
        return []
    colors_ls = list(colors)
    merged = []
    current_color = colors_ls[0]
    count = 1
    for color in colors_ls[1:]:
        if color == current_color:
            count += 1
        else:
            merged.append((current_color, count))
            current_color = color
            count = 1
    merged.append((current_color, count))
    return merged

# 配置参数
img_path = "D:\PythonProject\.jpg"
img_size, block_size, prec_lv = (40,40), 5, 8

img = Image.open(img_path).convert("RGB").resize(img_size, resample=Image.Resampling.BILINEAR)
w, h = img.size
latex = []

for col in range(w):
    col_colors = [rgb_short(reduce_color_prec(img.getpixel((col, 0 if j==0 else h-j)), prec_lv), prec_lv) for j in range(h)]
    merged = merge_colors(col_colors)
    col, total = "", 0
    for color, l in merged:
        total += l * block_size
        col = f"\\rlap{{\\color{{{color}}}{{\\rule{{{block_size}px}}{{{total}px}}}}}}{{{col}}}" if col else f"\\color{{{color}}}{{\\rule{{{block_size}px}}{{{total}px}}}}"
    latex.append(col)

print(f"${''.join(latex)}$")

