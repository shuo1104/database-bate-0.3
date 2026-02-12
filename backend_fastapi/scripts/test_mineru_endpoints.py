# -*- coding: utf-8 -*-
"""
MinerU 批量结果查询端点探测脚本
尝试多个可能的端点路径，找到返回非 404 的正确端点。

使用方法:
  cd backend_fastapi
  python scripts/test_mineru_endpoints.py <batch_id>

  例如:
  python scripts/test_mineru_endpoints.py 713b29d4-9221-403f-8d9f-fe353a8c1169
"""

import json
import os
import sys

import requests

# ---- 配置 ----
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
    print("ERROR: MINERU_API_KEY 未配置")
    sys.exit(1)

BATCH_ID = sys.argv[1] if len(sys.argv) > 1 else "713b29d4-9221-403f-8d9f-fe353a8c1169"

AUTH_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}",
}

# ---- 尝试所有可能的端点 ----
candidate_endpoints = [
    # GET 请求
    ("GET", f"{BASE_URL}/extract/task/batch/{BATCH_ID}"),
    ("GET", f"{BASE_URL}/extract/task/{BATCH_ID}"),
    ("GET", f"{BASE_URL}/extract/batch/{BATCH_ID}"),
    ("GET", f"{BASE_URL}/file-urls/batch/{BATCH_ID}"),
    ("GET", f"{BASE_URL}/extract-results/batch/{BATCH_ID}"),
    ("GET", f"{BASE_URL}/extract/result/batch/{BATCH_ID}"),
    ("GET", f"{BASE_URL}/extract/task/batch/result/{BATCH_ID}"),
    ("GET", f"{BASE_URL}/batch/{BATCH_ID}"),
    ("GET", f"{BASE_URL}/batch/result/{BATCH_ID}"),
    ("GET", f"{BASE_URL}/batch-result/{BATCH_ID}"),
    # 带 query parameter 的方式
    ("GET", f"{BASE_URL}/extract/task/batch?batch_id={BATCH_ID}"),
    ("GET", f"{BASE_URL}/extract/batch?batch_id={BATCH_ID}"),
    # POST 请求 (某些 API 使用 POST 查询)
    ("POST_JSON", f"{BASE_URL}/extract/task/batch/{BATCH_ID}"),
    ("POST_JSON", f"{BASE_URL}/extract/batch/result"),
]

print(f"Base URL: {BASE_URL}")
print(f"Batch ID: {BATCH_ID}")
print(f"Testing {len(candidate_endpoints)} candidate endpoints...\n")

for method, url in candidate_endpoints:
    try:
        if method == "GET":
            resp = requests.get(url, headers=AUTH_HEADERS, timeout=10)
        elif method == "POST_JSON":
            resp = requests.post(
                url,
                headers=AUTH_HEADERS,
                json={"batch_id": BATCH_ID},
                timeout=10,
            )
        else:
            continue

        status = resp.status_code
        marker = "✓ HIT!" if status < 400 else "✗"

        # 精简输出
        body_preview = resp.text[:300] if resp.text else "(empty)"

        print(f"  {marker} {method:10s} {url}")
        print(f"       Status: {status}")
        if status < 400:
            try:
                print(f"       Body: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")
            except Exception:
                print(f"       Body: {body_preview}")
        else:
            print(f"       Body: {body_preview}")
        print()

    except Exception as e:
        print(f"  ✗ {method:10s} {url}")
        print(f"       Error: {type(e).__name__}: {e}")
        print()

print("Done.")
