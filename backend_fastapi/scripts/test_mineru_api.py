# -*- coding: utf-8 -*-
"""
MinerU Cloud API v4 诊断脚本
逐步测试 batch file upload → poll → download 流程，打印每步完整响应。

使用方法:
  cd backend_fastapi
  python scripts/test_mineru_api.py

会使用 .env.dev 中的 MINERU_API_URL 和 MINERU_API_KEY。
如果没有可用的测试文件，脚本会自动创建一个简单的文本图片。
"""

import json
import os
import sys
import time

import requests

# ---- 配置 ----
# 优先从 .env.dev 读取
ENV_FILE = os.path.join(os.path.dirname(__file__), "..", "env", ".env.dev")


def load_env(path: str) -> dict[str, str]:
    env = {}
    if not os.path.exists(path):
        return env
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, val = line.partition("=")
            env[key.strip()] = val.strip().strip('"').strip("'")
    return env


env = load_env(ENV_FILE)
BASE_URL = env.get("MINERU_API_URL", "https://mineru.net/api/v4").rstrip("/")
API_KEY = env.get("MINERU_API_KEY", "")

if not API_KEY:
    print("ERROR: MINERU_API_KEY 未配置，请检查 .env.dev")
    sys.exit(1)

AUTH_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}",
}

# ---- 测试文件 ----
# 使用已存在的上传文件，或者自动创建一个小的测试 JPG
TEST_FILE = None
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "uploads", "agent")
# 查找最近上传的文件
for root, dirs, files in os.walk(UPLOAD_DIR):
    for fname in files:
        if fname.lower().endswith((".jpg", ".jpeg", ".png", ".pdf")):
            TEST_FILE = os.path.join(root, fname)
            break
    if TEST_FILE:
        break

if not TEST_FILE:
    # 创建一个最小的有效 JPEG 文件 (1x1 白色像素)
    TEST_FILE = os.path.join(os.path.dirname(__file__), "test_mineru_sample.jpg")
    # 最小有效 JPEG (1x1 pixel)
    jpeg_bytes = bytes([
        0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
        0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
        0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
        0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
        0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
        0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
        0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
        0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
        0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00,
        0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
        0x09, 0x0A, 0x0B, 0xFF, 0xC4, 0x00, 0xB5, 0x10, 0x00, 0x02, 0x01, 0x03,
        0x03, 0x02, 0x04, 0x03, 0x05, 0x05, 0x04, 0x04, 0x00, 0x00, 0x01, 0x7D,
        0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12, 0x21, 0x31, 0x41, 0x06,
        0x13, 0x51, 0x61, 0x07, 0x22, 0x71, 0x14, 0x32, 0x81, 0x91, 0xA1, 0x08,
        0x23, 0x42, 0xB1, 0xC1, 0x15, 0x52, 0xD1, 0xF0, 0x24, 0x33, 0x62, 0x72,
        0x82, 0x09, 0x0A, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x25, 0x26, 0x27, 0x28,
        0x29, 0x2A, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x43, 0x44, 0x45,
        0x46, 0x47, 0x48, 0x49, 0x4A, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59,
        0x5A, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A, 0x73, 0x74, 0x75,
        0x76, 0x77, 0x78, 0x79, 0x7A, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89,
        0x8A, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9A, 0xA2, 0xA3,
        0xA4, 0xA5, 0xA6, 0xA7, 0xA8, 0xA9, 0xAA, 0xB2, 0xB3, 0xB4, 0xB5, 0xB6,
        0xB7, 0xB8, 0xB9, 0xBA, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8, 0xC9,
        0xCA, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9, 0xDA, 0xE1, 0xE2,
        0xE3, 0xE4, 0xE5, 0xE6, 0xE7, 0xE8, 0xE9, 0xEA, 0xF1, 0xF2, 0xF3, 0xF4,
        0xF5, 0xF6, 0xF7, 0xF8, 0xF9, 0xFA, 0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01,
        0x00, 0x00, 0x3F, 0x00, 0x7B, 0x94, 0x11, 0x00, 0x00, 0x00, 0x00, 0xFF,
        0xD9,
    ])
    with open(TEST_FILE, "wb") as f:
        f.write(jpeg_bytes)
    print(f"[INFO] 已创建测试 JPEG 文件: {TEST_FILE}")

TEST_FILENAME = os.path.basename(TEST_FILE)
print(f"\n{'='*60}")
print("MinerU Cloud API v4 诊断")
print(f"{'='*60}")
print(f"Base URL:   {BASE_URL}")
print(f"API Key:    {API_KEY[:20]}...{API_KEY[-10:]}")
print(f"Test File:  {TEST_FILE}")
print(f"File Name:  {TEST_FILENAME}")
print(f"File Size:  {os.path.getsize(TEST_FILE)} bytes")
print()

# =====================================================================
# Step 1: 请求预签名上传 URL
# =====================================================================
print(f"{'='*60}")
print("Step 1: POST /file-urls/batch (请求预签名上传 URL)")
print(f"{'='*60}")

batch_payload = {
    "files": [{"name": TEST_FILENAME, "is_ocr": True}],
    "model_version": "vlm",
    "enable_formula": True,
    "enable_table": True,
    "language": "ch",
}

try:
    resp1 = requests.post(
        f"{BASE_URL}/file-urls/batch",
        headers=AUTH_HEADERS,
        json=batch_payload,
        timeout=30,
    )
    print(f"  HTTP Status: {resp1.status_code}")
    print(f"  Response Body:\n{json.dumps(resp1.json(), indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"  FAILED: {type(e).__name__}: {e}")
    sys.exit(1)

if resp1.status_code >= 400:
    print(f"\n  [FAIL] HTTP {resp1.status_code}, 停止。")
    sys.exit(1)

body1 = resp1.json()
if body1.get("code") != 0:
    print(f"\n  [FAIL] API code={body1.get('code')}, msg={body1.get('msg')}, 停止。")
    sys.exit(1)

batch_id = body1["data"]["batch_id"]
file_urls = body1["data"].get("file_urls") or []
print(f"\n  [OK] batch_id = {batch_id}")
print(f"  [OK] file_urls count = {len(file_urls)}")

if not file_urls:
    print("  [FAIL] 未返回上传 URL，停止。")
    sys.exit(1)

upload_url = file_urls[0]
print(f"  [OK] upload_url = {upload_url[:80]}...")

# =====================================================================
# Step 2: 上传文件到预签名 URL
# =====================================================================
print(f"\n{'='*60}")
print("Step 2: PUT file (上传文件到预签名 URL)")
print(f"{'='*60}")

try:
    with open(TEST_FILE, "rb") as f:
        # 注意：不设置任何额外 header，尤其不能设置 Content-Type
        resp2 = requests.put(upload_url, data=f, timeout=60)
    print(f"  HTTP Status: {resp2.status_code}")
    print(f"  Response Headers: {dict(resp2.headers)}")
    if resp2.text:
        print(f"  Response Body (first 500 chars): {resp2.text[:500]}")
    else:
        print(f"  Response Body: (empty)")
except Exception as e:
    print(f"  FAILED: {type(e).__name__}: {e}")
    sys.exit(1)

if resp2.status_code >= 300:
    print(f"\n  [FAIL] Upload HTTP {resp2.status_code}, 停止。")
    sys.exit(1)

print(f"\n  [OK] 文件上传成功")

# =====================================================================
# Step 3: 轮询批量任务结果
# =====================================================================
print(f"\n{'='*60}")
print("Step 3: GET /extract/task/batch/{batch_id} (轮询结果)")
print(f"{'='*60}")

poll_url = f"{BASE_URL}/extract/task/batch/{batch_id}"
print(f"  Poll URL: {poll_url}")

# 等待 MinerU 扫描文件并创建任务
print(f"\n  等待 8 秒让 MinerU 扫描并创建任务...")
time.sleep(8)

max_polls = 60  # 最多轮询 60 次，每次间隔 5 秒 = 5 分钟
for i in range(max_polls):
    print(f"\n  --- Poll #{i+1} (elapsed ~{8 + i*5}s) ---")
    try:
        resp3 = requests.get(poll_url, headers=AUTH_HEADERS, timeout=30)
        print(f"  HTTP Status: {resp3.status_code}")

        if resp3.status_code >= 400:
            print(f"  Response Body: {resp3.text[:500]}")
            print(f"  [WARN] HTTP {resp3.status_code}, 继续轮询...")
            time.sleep(5)
            continue

        body3 = resp3.json()
        print(f"  Response Body:\n{json.dumps(body3, indent=2, ensure_ascii=False)}")

        if body3.get("code") != 0:
            print(f"  [WARN] code={body3.get('code')}, msg={body3.get('msg')}, 继续轮询...")
            time.sleep(5)
            continue

        data3 = body3.get("data", {})
        print(f"\n  data keys: {list(data3.keys())}")

        # 尝试获取 extract_result
        extract_result = data3.get("extract_result") or data3.get("extract_results") or []
        print(f"  extract_result type: {type(extract_result).__name__}, len: {len(extract_result) if isinstance(extract_result, list) else 'N/A'}")

        if isinstance(extract_result, list) and extract_result:
            first = extract_result[0]
            state = first.get("state", "")
            print(f"  first_task state: {state}")
            if state == "done":
                zip_url = first.get("full_zip_url", "")
                print(f"\n  [SUCCESS] 任务完成!")
                print(f"  full_zip_url: {zip_url}")
                sys.exit(0)
            elif state == "failed":
                print(f"\n  [FAIL] 任务失败: {first.get('err_msg', 'unknown')}")
                sys.exit(1)
        elif data3.get("state"):
            state = data3["state"]
            print(f"  batch-level state: {state}")
            if state == "done":
                zip_url = data3.get("full_zip_url", "")
                print(f"\n  [SUCCESS] 任务完成!")
                print(f"  full_zip_url: {zip_url}")
                sys.exit(0)
            elif state == "failed":
                print(f"\n  [FAIL] 任务失败: {data3.get('err_msg', 'unknown')}")
                sys.exit(1)
        else:
            print(f"  [INFO] 无 extract_result / state，任务可能仍在初始化...")

    except Exception as e:
        print(f"  FAILED: {type(e).__name__}: {e}")

    time.sleep(5)

print(f"\n  [TIMEOUT] 轮询超时 ({max_polls * 5}秒)")
sys.exit(1)
