#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动更新看板并推送到GitHub
流程: build_dashboard.py → git add → git commit → git push
"""

import subprocess
import sys
import os
from datetime import datetime

REPO_DIR = '/mnt/d/CC勋章看板'
BUILD_SCRIPT = os.path.join(REPO_DIR, 'build_dashboard.py')
TARGET_FILE = 'CC采销岗勋章看板.html'

def run(cmd, cwd=REPO_DIR):
    """运行命令并实时输出"""
    print(f"  > {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.returncode != 0 and result.stderr:
        print(f"  stderr: {result.stderr.strip()}")
    return result.returncode == 0

def main():
    print("=" * 50)
    print(f"自动更新看板并推送 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 1. 运行 build_dashboard.py 更新数据
    print("\n[1/4] 更新看板数据...")
    if not run(f'python3 {BUILD_SCRIPT}'):
        print("❌ 看板数据更新失败，中止推送")
        sys.exit(1)

    # 1.5. 同步到 index.html（GitHub Pages 入口）
    print("\n[1.5] 同步到 index.html...")
    import shutil
    src = os.path.join(REPO_DIR, TARGET_FILE)
    dst = os.path.join(REPO_DIR, 'index.html')
    shutil.copy2(src, dst)
    print("  ✅ 已同步")

    # 2. 检查是否有变更
    print("\n[2/4] 检查数据变更...")
    result = subprocess.run('git diff --name-only', shell=True, cwd=REPO_DIR, capture_output=True, text=True)
    changed = result.stdout.strip()

    # 也检查 untracked 的目标文件
    result2 = subprocess.run(f'git status --porcelain {TARGET_FILE} index.html', shell=True, cwd=REPO_DIR, capture_output=True, text=True)

    if not changed and not result2.stdout.strip():
        print("  没有数据变更，无需推送 ✅")
        return

    print(f"  变更文件: {changed or TARGET_FILE}")

    # 3. Git commit
    print("\n[3/4] 提交变更...")
    today = datetime.now().strftime('%Y-%m-%d')
    run(f'git add {TARGET_FILE} index.html')
    run(f'git commit -m "自动更新看板数据 {today}"')

    # 4. Git push
    print("\n[4/4] 推送到GitHub...")
    if not run('git push origin main'):
        print("❌ 推送失败")
        sys.exit(1)

    print(f"\n✅ 完成！看板已更新并推送到GitHub")
    print(f"  访问: https://jiacuicui27-arch.github.io/medal-dashboard/")

if __name__ == '__main__':
    main()
