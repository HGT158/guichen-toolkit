import requests
import json
import os
from datetime import datetime

# 从环境变量读取密钥，避免把敏感信息写入代码仓库
API_KEY = os.getenv("OPENROUTER_API_KEY")

url = "https://openrouter.ai/api/v1/models"
if not API_KEY:
    raise ValueError("请先设置环境变量 OPENROUTER_API_KEY")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()["data"]

    # 生成带逗号的 txt：每个模型ID后加逗号
    model_ids = [model["id"] for model in data]
    comma_separated = ",".join(model_ids)  # ID1,ID2,ID3,...

    with open("models_comma.txt", "w", encoding="utf-8") as f:
        f.write(comma_separated)

    print("带逗号列表已保存到 models_comma.txt，共", len(model_ids), "个模型")
    print("示例前10个：", ",".join(model_ids[:10]))

    # 也生成纯 ID txt（备用）
    with open("models_pure.txt", "w", encoding="utf-8") as f:
        for model_id in model_ids:
            f.write(model_id + "\n")

    print("纯 ID 也保存到 models_pure.txt")

else:
    print("错误:", response.status_code, response.text)
