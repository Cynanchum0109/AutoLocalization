#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""pack.py - 打玩家安装包（发 release 用）。

  1. 清空 Installer/LLC_zh-CN，用 Workplace/translated 整份重建（译文范围只能是 translated）
  2. 在 out/ 生成 zip，顶层固定 4 项：install.bat / install.ps1 / README.txt / LLC_zh-CN/
  3. 校验：LLC_zh-CN 与 translated 逐字节一致、zip 顶层恰好 4 项、文件数对得上
  任何一步不对就报错退出，不产出 zip。上传不在本脚本里做，最后会打印上传命令。

用法：
  python pack.py Canto10.2.TheGazeBearing_byBQCynanchum.zip
"""

import argparse
import filecmp
import os
import shutil
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from limbus.jsonio import setup_stdout

INSTALLER_DIR = os.path.join(config.BASE_DIR, "Installer")
PKG_DIR = os.path.join(INSTALLER_DIR, "LLC_zh-CN")
SHELL_FILES = ["install.bat", "install.ps1", "README.txt"]
RELEASE_REPO = "Cynanchum0109/LimbusCompanyTempLoc"


def die(msg):
    print(f"[pack] 错误：{msg}", file=sys.stderr)
    sys.exit(1)


def rel_files(root):
    out = []
    for dirpath, _, names in os.walk(root):
        for n in names:
            out.append(os.path.relpath(os.path.join(dirpath, n), root).replace("\\", "/"))
    return sorted(out)


def main():
    setup_stdout()
    ap =argparse.ArgumentParser(description="打玩家安装包")
    ap.add_argument("zip_name", help="release 附件文件名，和线上同名才能 --clobber 原地替换")
    args = ap.parse_args()
    if not args.zip_name.endswith(".zip") or os.sep in args.zip_name or "/" in args.zip_name:
        die("zip_name 只写文件名，且以 .zip 结尾")

    src = rel_files(config.WORK_ROOT) if os.path.isdir(config.WORK_ROOT) else []
    if not src:
        die(f"{config.WORK_ROOT} 为空，先跑 apply.py")
    for f in SHELL_FILES:
        if not os.path.isfile(os.path.join(INSTALLER_DIR, f)):
            die(f"缺安装包外壳文件 Installer/{f}")

    if os.path.isdir(PKG_DIR):
        shutil.rmtree(PKG_DIR)
    shutil.copytree(config.WORK_ROOT, PKG_DIR)

    pkg = rel_files(PKG_DIR)
    if pkg != src:
        die("Installer/LLC_zh-CN 与 Workplace/translated 文件列表不一致")
    for f in src:
        if not filecmp.cmp(os.path.join(config.WORK_ROOT, f), os.path.join(PKG_DIR, f), shallow=False):
            die(f"内容不一致：{f}")

    os.makedirs(config.OUT_DIR, exist_ok=True)
    zip_path = os.path.join(config.OUT_DIR, args.zip_name)
    tmp_path = zip_path + ".tmp"
    with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in SHELL_FILES:
            z.write(os.path.join(INSTALLER_DIR, f), f)
        for f in pkg:
            z.write(os.path.join(PKG_DIR, f), f"LLC_zh-CN/{f}")

    with zipfile.ZipFile(tmp_path) as z:
        names = z.namelist()
    top = sorted({n.split("/")[0] for n in names})
    if top != sorted(SHELL_FILES + ["LLC_zh-CN"]):
        os.remove(tmp_path)
        die(f"zip 顶层不对：{top}")
    if sum(n.startswith("LLC_zh-CN/") for n in names) != len(src):
        os.remove(tmp_path)
        die("zip 里 LLC_zh-CN 文件数与 translated 不一致")
    os.replace(tmp_path, zip_path)

    print(f"[pack] OK  {zip_path}")
    print(f"[pack] 顶层：{', '.join(top)}；LLC_zh-CN {len(src)} 个文件；{os.path.getsize(zip_path)} 字节")
    print("[pack] 上传（确认后手动执行）：")
    print(f'  gh release upload "<tag>" "out/{args.zip_name}" -R {RELEASE_REPO} --clobber')


if __name__ == "__main__":
    main()
