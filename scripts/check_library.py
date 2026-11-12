#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""核对 materialLibrary.txt 的真实内容与 registry.json 的编号登记。

换项目 / 换游戏包时，同一个材质词的编号可能不同甚至不存在，
所以任何涉及编号的回答都必须先跑本脚本，禁止凭记忆复用旧编号。

用法:
    python check_library.py <materialLibrary.txt>
    python check_library.py <materialLibrary.txt> --registry <registry.json>
    python check_library.py <materialLibrary.txt> --word 雪 --base "bundle46 | mat_sk_fire_extinguisher_01"
    python check_library.py <...> --json

退出码: 0 = 一致 / 仅查询, 1 = 发现不一致, 2 = 用法或文件错误
"""
import hashlib
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def normalize(s):
    """统一 '|' 两侧空白，避免空格差异造成误报。"""
    return re.sub(r"\s*\|\s*", " | ", s.strip())


def read_library(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read().splitlines()
    valid = [normalize(l) for l in raw if l.strip() and not l.strip().startswith("#")]
    digest = hashlib.sha256("\n".join(valid).encode("utf-8")).hexdigest()
    return valid, digest


def find_line(lines, base):
    return [i for i, l in enumerate(lines) if l == normalize(base)]


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("--"):
        print("用法: python check_library.py <materialLibrary.txt> [--registry <registry.json>] "
              "[--word <词> --base <基底行>] [--json]")
        return 2

    lib_path = args[0]
    if not os.path.isfile(lib_path):
        print("FAIL 库文件不存在: %s" % lib_path)
        return 2

    registry_path, word, base, as_json = None, None, None, False
    i = 1
    while i < len(args):
        if args[i] == "--registry" and i + 1 < len(args):
            registry_path = args[i + 1]; i += 2
        elif args[i] == "--word" and i + 1 < len(args):
            word = args[i + 1]; i += 2
        elif args[i] == "--base" and i + 1 < len(args):
            base = args[i + 1]; i += 2
        elif args[i] == "--json":
            as_json = True; i += 1
        else:
            print("FAIL 无法识别的参数: %s" % args[i])
            return 2

    lines, digest = read_library(lib_path)
    report = {
        "library_path": os.path.abspath(lib_path),
        "line_count": len(lines),
        "next_id": len(lines),
        "fingerprint": digest,
        "lines": lines,
        "checks": [],
        "problems": 0,
    }

    def check(status, label, detail, fix=""):
        report["checks"].append({"status": status, "label": label, "detail": detail, "fix": fix})
        if status in ("MISMATCH", "MISSING", "OUT_OF_RANGE", "DEFAULT_INVALID", "NEW_PROJECT"):
            report["problems"] += 1

    if registry_path:
        if not os.path.isfile(registry_path):
            print("FAIL 登记表不存在: %s" % registry_path)
            return 2
        with open(registry_path, encoding="utf-8") as f:
            reg = json.load(f)

        reg_lib = reg.get("library_path", "")
        if os.path.normcase(os.path.abspath(reg_lib)) != os.path.normcase(os.path.abspath(lib_path)):
            projects = reg.get("projects") or {}
            hit_key = next((k for k in projects
                            if os.path.normcase(os.path.abspath(k)) == os.path.normcase(os.path.abspath(lib_path))), None)
            if hit_key:
                reg = dict(projects[hit_key])
                reg["library_path"] = lib_path
                check("PROJECT_SWITCH", "项目切换", "已载入该库的项目档案：%s" % (reg.get("label") or hit_key),
                      "以该档案的 entries / fingerprint 核对，不使用当前项目的编号")
            else:
                check("NEW_PROJECT", "项目切换",
                      "登记表登记的是 %s，本次库 %s 没有对应的项目档案" % (reg_lib, lib_path),
                      "这是新项目：所有编号必须按本次库内容重新分配，禁止复用当前项目的编号；"
                      "确认后把该项目写入 registry.json 的 projects")
                reg = {"library_path": lib_path, "entries": {},
                       "default_material_id": reg.get("default_material_id"),
                       "library_fingerprint": {}}

        fp = reg.get("library_fingerprint") or {}
        old_count, old_digest = fp.get("line_count"), fp.get("sha256")
        if old_digest and old_digest != digest:
            check("FINGERPRINT_CHANGED", "库指纹", "登记时 %s 行 / %s…，现在 %s 行 / %s…"
                  % (old_count, old_digest[:12], len(lines), digest[:12]),
                  "库内容已变，必须逐词重新核对编号，禁止复用旧值")
        elif not old_digest:
            check("NO_FINGERPRINT", "库指纹", "登记表尚未记录 library_fingerprint",
                  "核对通过后把本次 line_count / sha256 写入登记表")

        default_id = reg.get("default_material_id")
        if default_id is not None:
            if 0 <= int(default_id) < len(lines):
                check("OK", "默认材质ID %s" % default_id, "库[%s] = %s" % (default_id, lines[int(default_id)]))
            else:
                check("DEFAULT_INVALID", "默认材质ID %s" % default_id,
                      "越界：库只有 %d 行" % len(lines),
                      "本项目库里没有这个编号，必须重新指定默认材质ID")

        for w, ent in (reg.get("entries") or {}).items():
            wid, baseline = int(ent.get("id", -1)), ent.get("base_line", "")
            hits = find_line(lines, baseline)
            if wid < 0 or wid >= len(lines):
                check("OUT_OF_RANGE", w, "登记 id=%d，但库只有 %d 行" % (wid, len(lines)),
                      "需追加库行；新编号 = 有效行数 %d" % len(lines))
            elif lines[wid] != normalize(baseline):
                check("MISMATCH", w, "登记 id=%d，库[%d] 实际是 %s，期望 %s"
                      % (wid, wid, lines[wid], baseline),
                      "按库内容重算：该基底行的实际索引 %s；库里没有则追加，编号 = %d"
                      % (hits if hits else "无", len(lines)))
            else:
                check("OK", w, "登记 id=%d 与库一致（%s）" % (wid, baseline))

    if word:
        reg = {}
        if registry_path and os.path.isfile(registry_path):
            with open(registry_path, encoding="utf-8") as f:
                reg = json.load(f)
        ent = (reg.get("entries") or {}).get(word, {})
        baseline = base or ent.get("base_line", "")
        if not baseline:
            check("MISSING", word, "未提供基底行，无法核对")
        else:
            hits = find_line(lines, baseline)
            if hits:
                check("OK", word, "基底行在库中的索引: %s" % hits)
            else:
                check("MISSING", word, "库里找不到 %s" % baseline,
                      "需追加该行，编号 = %d" % len(lines))

    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1 if report["problems"] else 0

    print("库文件: %s" % report["library_path"])
    print("有效行数: %d | 下一个空号: %d | 指纹: %s…" % (len(lines), len(lines), digest[:12]))
    print("--- 库内容 ---")
    for i, l in enumerate(lines):
        print("%2d  %s" % (i, l))
    if report["checks"]:
        print("--- 核对结果 ---")
        for c in report["checks"]:
            print("[%-18s] %s: %s" % (c["status"], c["label"], c["detail"]))
            if c["fix"]:
                print("    → %s" % c["fix"])
    print("结论: %s (%d 个问题)" % ("FAIL" if report["problems"] else "PASS", report["problems"]))
    return 1 if report["problems"] else 0


if __name__ == "__main__":
    sys.exit(main())
