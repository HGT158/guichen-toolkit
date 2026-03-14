import os
import shutil
from pathlib import Path


def collect_images(source_dir, target_dir):
    # 支持的图片后缀名
    extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}

    # 确保目标文件夹存在，如果不存在则创建
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"创建目标文件夹: {target_dir}")

    count = 0

    # 使用 os.walk 递归遍历文件夹
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            # 检查文件后缀
            if Path(file).suffix in extensions:
                source_path = os.path.join(root, file)
                target_path = os.path.join(target_dir, file)

                # 处理重名问题：如果目标文件夹已有同名文件，自动重命名
                if os.path.exists(target_path):
                    name, ext = os.path.splitext(file)
                    target_path = os.path.join(target_dir, f"{name}_副本{ext}")

                try:
                    shutil.copy2(source_path, target_path)
                    print(f"已复制: {file}")
                    count += 1
                except Exception as e:
                    print(f"复制 {file} 时出错: {e}")

    print(f"\n任务完成！共复制了 {count} 张图片到 {target_dir}")


# --- 使用设置 ---
source_folder = r'1111'  # 替换为你的源文件夹地址
target_folder = r'1111\1'  # 替换为你想存放图片的地址

collect_images(source_folder, target_folder)