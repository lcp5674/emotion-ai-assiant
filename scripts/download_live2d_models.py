#!/usr/bin/env python3
"""
Live2D模型下载脚本
从immuncle/live2d仓库下载模型
"""
import os
import requests
import time
import sys

# 配置
BASE_DIR = "/opt/emotion-ai-assiant/frontend/web/public/live2d"
REPO_URL = "https://api.github.com/repos/imuncle/live2d"
MODELS_TO_DOWNLOAD = ["haru", "Epsilon2.1", "hibiki", "Pio", "YuzukiYukari", "Tia"]

# 备用下载源
MIRRORS = [
    "https://raw.githubusercontent.com/imuncle/live2d/master",
    "https://cdn.jsdelivr.net/gh/imuncle/live2d@master",
]

def get_file(url, retries=3):
    """下载文件，带重试"""
    for i in range(retries):
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                return resp.content
            print(f"  状态码: {resp.status_code}")
        except Exception as e:
            print(f"  重试 {i+1}/{retries}: {e}")
            time.sleep(2)
    return None

def list_model_files(model_name):
    """获取模型文件列表"""
    url = f"{REPO_URL}/contents/model/{model_name}"
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"获取模型文件列表失败: {e}")
    return []

def download_model(model_name):
    """下载单个模型"""
    print(f"\n正在下载模型: {model_name}")
    model_dir = os.path.join(BASE_DIR, model_name)
    os.makedirs(model_dir, exist_ok=True)

    files = list_model_files(model_name)
    if not files:
        print(f"  无法获取模型文件列表")
        return False

    success_count = 0
    for f in files:
        if f["type"] == "dir":
            # 处理子目录
            subdir = os.path.join(model_dir, f["name"])
            os.makedirs(subdir, exist_ok=True)
            # 获取子目录内容
            try:
                sub_resp = requests.get(f["url"], timeout=30)
                if sub_resp.status_code == 200:
                    sub_files = sub_resp.json()
                    for sf in sub_files:
                        if sf["type"] == "file":
                            # 尝试多个镜像
                            content = None
                            for mirror in MIRRORS:
                                path = sf["path"]
                                url = f"{mirror}/{path}"
                                print(f"  尝试: {url[:60]}...")
                                content = get_file(url)
                                if content:
                                    break
                            if content:
                                sf_path = os.path.join(model_dir, sf["name"])
                                with open(sf_path, "wb") as fp:
                                    fp.write(content)
                                print(f"  保存: {sf['name']}")
                                success_count += 1
                            else:
                                print(f"  失败: {sf['name']}")
            except Exception as e:
                print(f"  处理子目录失败: {e}")
        else:
            # 处理文件
            content = None
            for mirror in MIRRORS:
                url = f"{mirror}/model/{model_name}/{f['name']}"
                print(f"  尝试: {url[:60]}...")
                content = get_file(url)
                if content:
                    break
            if content:
                f_path = os.path.join(model_dir, f["name"])
                with open(f_path, "wb") as fp:
                    fp.write(content)
                print(f"  保存: {f['name']}")
                success_count += 1
            else:
                print(f"  失败: {f['name']}")

    print(f"  完成: {success_count} 个文件")
    return success_count > 0

def main():
    print("=" * 50)
    print("Live2D模型下载工具")
    print("=" * 50)

    os.makedirs(BASE_DIR, exist_ok=True)

    # 创建模型列表文件
    list_file = os.path.join(BASE_DIR, "models.txt")

    # 下载模型
    for model in MODELS_TO_DOWNLOAD:
        try:
            download_model(model)
        except KeyboardInterrupt:
            print("\n用户中断")
            break
        except Exception as e:
            print(f"下载 {model} 失败: {e}")

    # 尝试下载已存在的shizuku模型（之前下载的）
    shizuku_dir = os.path.join(BASE_DIR, "default")
    if os.path.exists(shizuku_dir):
        print("\n复制shizuku模型...")
        # 重命名为model.json
        for f in os.listdir(shizuku_dir):
            if f.endswith(".model.json"):
                import shutil
                shutil.copy(
                    os.path.join(shizuku_dir, f),
                    os.path.join(shizuku_dir, "model.json")
                )
                print(f"  已复制为 model.json")

    print("\n下载完成!")
    print(f"模型目录: {BASE_DIR}")

if __name__ == "__main__":
    main()