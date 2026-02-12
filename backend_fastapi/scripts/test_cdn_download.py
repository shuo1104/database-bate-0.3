# -*- coding: utf-8 -*-
"""
测试 cdn-mineru.openxlab.org.cn 的连通性和下载能力。
运行: python scripts/test_cdn_download.py
"""
import os
import platform
import ssl
import subprocess
import sys
import urllib.request

TEST_URL = "https://cdn-mineru.openxlab.org.cn/pdf/2026-02-11/64cd1797-aec2-4fde-b169-f921d1a2963e.zip"

print(f"Python: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"SSL version: {ssl.OPENSSL_VERSION}")
print(f"Test URL: {TEST_URL[:80]}...")
print()

# --- Test 1: DNS ---
print("="*50)
print("Test 1: DNS Resolution")
print("="*50)
import socket
try:
    ips = socket.getaddrinfo("cdn-mineru.openxlab.org.cn", 443)
    print(f"  [OK] Resolved to {len(ips)} addresses:")
    seen = set()
    for info in ips:
        ip = info[4][0]
        if ip not in seen:
            print(f"       {ip}")
            seen.add(ip)
except Exception as e:
    print(f"  [FAIL] DNS failed: {e}")

# --- Test 2: TCP Connect ---
print("\n" + "="*50)
print("Test 2: TCP Connect (port 443)")
print("="*50)
try:
    sock = socket.create_connection(("cdn-mineru.openxlab.org.cn", 443), timeout=10)
    print(f"  [OK] TCP connection succeeded")
    sock.close()
except Exception as e:
    print(f"  [FAIL] TCP connect failed: {e}")

# --- Test 3: SSL Handshake ---
print("\n" + "="*50)
print("Test 3: SSL Handshake (default)")
print("="*50)
try:
    ctx = ssl.create_default_context()
    with socket.create_connection(("cdn-mineru.openxlab.org.cn", 443), timeout=10) as sock:
        with ctx.wrap_socket(sock, server_hostname="cdn-mineru.openxlab.org.cn") as ssock:
            print(f"  [OK] SSL version: {ssock.version()}")
            print(f"  [OK] Cipher: {ssock.cipher()}")
except Exception as e:
    print(f"  [FAIL] SSL handshake failed: {e}")

# --- Test 4: SSL Handshake (TLS 1.2 only) ---
print("\n" + "="*50)
print("Test 4: SSL Handshake (TLS 1.2 forced)")
print("="*50)
try:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.maximum_version = ssl.TLSVersion.TLSv1_2
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with socket.create_connection(("cdn-mineru.openxlab.org.cn", 443), timeout=10) as sock:
        with ctx.wrap_socket(sock, server_hostname="cdn-mineru.openxlab.org.cn") as ssock:
            print(f"  [OK] SSL version: {ssock.version()}")
            print(f"  [OK] Cipher: {ssock.cipher()}")
except Exception as e:
    print(f"  [FAIL] TLS 1.2 handshake failed: {e}")

# --- Test 5: SSL Handshake (no verify, relaxed ciphers) ---
print("\n" + "="*50)
print("Test 5: SSL Handshake (relaxed, SECLEVEL=1)")
print("="*50)
try:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_ciphers("DEFAULT@SECLEVEL=1")
    with socket.create_connection(("cdn-mineru.openxlab.org.cn", 443), timeout=10) as sock:
        with ctx.wrap_socket(sock, server_hostname="cdn-mineru.openxlab.org.cn") as ssock:
            print(f"  [OK] SSL version: {ssock.version()}")
            print(f"  [OK] Cipher: {ssock.cipher()}")
except Exception as e:
    print(f"  [FAIL] Relaxed SSL failed: {e}")

# --- Test 6: curl.exe (Windows built-in, uses Schannel) ---
print("\n" + "="*50)
print("Test 6: curl.exe (Windows Schannel TLS)")
print("="*50)
try:
    # Only try HEAD request first to avoid downloading
    result = subprocess.run(
        ["curl.exe", "-sS", "-I", "-L", "--connect-timeout", "10",
         "--max-time", "15", TEST_URL],
        capture_output=True, text=True, timeout=20,
    )
    print(f"  Exit code: {result.returncode}")
    print(f"  Headers:\n{result.stdout[:500]}")
    if result.stderr:
        print(f"  Stderr: {result.stderr[:300]}")
except FileNotFoundError:
    print("  [SKIP] curl.exe not found")
except Exception as e:
    print(f"  [FAIL] {type(e).__name__}: {e}")

# --- Test 7: PowerShell TLS 1.2 only ---
print("\n" + "="*50)
print("Test 7: PowerShell (TLS 1.2 only, HEAD)")
print("="*50)
try:
    ps_cmd = (
        '[Net.ServicePointManager]::SecurityProtocol = '
        '[Net.SecurityProtocolType]::Tls12; '
        f'$r = Invoke-WebRequest -Uri "{TEST_URL}" '
        '-Method Head -UseBasicParsing; '
        '$r.StatusCode'
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_cmd],
        capture_output=True, text=True, timeout=20,
    )
    print(f"  Exit code: {result.returncode}")
    if result.stdout.strip():
        print(f"  Output: {result.stdout.strip()}")
    if result.stderr.strip():
        print(f"  Stderr: {result.stderr[:300]}")
except Exception as e:
    print(f"  [FAIL] {type(e).__name__}: {e}")

print("\n" + "="*50)
print("Done. 请将以上输出贴给我。")
print("="*50)
