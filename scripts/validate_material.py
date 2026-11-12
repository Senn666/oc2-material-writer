#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验 oc2-material-writer 产出的 material.txt。

用法:
    python validate_material.py <输出文件> [common|glass]

第二参数省略时从头部注释的「基底: bundle166 ...」推断。
校验项: 头部元信息 / 行内注释 / 单个等号 / 参数白名单 / 数值格式 /
KEYWORD 合法 / 全量参数完整性（与纯净模板逐项对齐）。
退出码 0 = PASS, 1 = FAIL, 2 = 用法或文件错误。
"""
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(SKILL_DIR, "assets")

# 极哑光词允许额外追加的 Unity 编译期开关；模板自带的 6 个 KEYWORD 仍必须齐全。
# 插件只有 EnableKeyword、没有 DisableKeyword，所以「关闭」只能靠 Enable 这些 *_OFF 变体。
MATTE_EXTRA_KEYWORDS = {"_SPECULARHIGHLIGHTS_OFF", "_GLOSSYREFLECTIONS_OFF"}


def parse_template(base):
    path = os.path.join(ASSETS, "template_common.txt" if base == "common" else "template_glass.txt")
    keys, keywords = [], []
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("KEYWORD="):
                keywords.append(line[8:].strip())
            elif "=" in line:
                keys.append(line.split("=", 1)[0].strip())
    return keys, keywords


def is_float(s):
    try:
        float(s.strip())
        return True
    except (ValueError, AttributeError):
        return False


def main():
    if len(sys.argv) < 2:
        print("用法: python validate_material.py <输出文件> [common|glass]")
        return 2

    target = sys.argv[1]
    if not os.path.isfile(target):
        print("FAIL 文件不存在: %s" % target)
        return 2

    with open(target, encoding="utf-8") as f:
        raw_lines = f.read().splitlines()

    base = sys.argv[2].strip().lower() if len(sys.argv) > 2 else None
    if base and base not in ("common", "glass"):
        print("FAIL 基底只能是 common 或 glass，收到: %s" % base)
        return 2
    if not base:
        head = "\n".join(raw_lines[:10])
        base = "glass" if ("bundle166" in head or "玻璃" in head) else "common"

    tpl_keys, tpl_keywords = parse_template(base)
    allowed = set(tpl_keys)
    errors, warnings = [], []
    seen_keys, seen_keywords = [], []
    header_hits = {"OC2 材质": False, "材质ID": False, "基底": False}

    for no, raw in enumerate(raw_lines, 1):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            for k in header_hits:
                if k in line:
                    header_hits[k] = True
            continue

        if "#" in line:
            errors.append("L%d 行内注释会破坏解析: %s" % (no, line[:60]))
            continue

        if line.startswith("KEYWORD="):
            kw = line[8:].strip()
            seen_keywords.append(kw)
            if not kw:
                errors.append("L%d KEYWORD 为空" % no)
            elif base == "glass":
                errors.append("L%d 玻璃基底不应有 KEYWORD: %s" % (no, kw))
            elif kw not in tpl_keywords and kw not in MATTE_EXTRA_KEYWORDS:
                errors.append("L%d KEYWORD 既不在模板自带列表、也不是允许的极哑光开关: %s" % (no, kw))
            continue

        if line.count("=") != 1:
            errors.append("L%d 必须恰好一个 '=': %s" % (no, line[:60]))
            continue
        key, val = (p.strip() for p in line.split("=", 1))

        if not key.startswith("_"):
            errors.append("L%d 参数名应以 _ 开头: %s" % (no, key))
        if key not in allowed:
            errors.append("L%d 参数名不在 %s 基底模板中（会被静默忽略）: %s" % (no, base, key))
        seen_keys.append(key)

        if "," in val:
            parts = [p.strip() for p in val.split(",")]
            if len(parts) not in (3, 4):
                errors.append("L%d 颜色必须是 3 或 4 段: %s" % (no, val[:60]))
                continue
            for p in parts:
                if not is_float(p):
                    errors.append("L%d 颜色分量不是数字: %s" % (no, val[:60]))
                    break
                if not (0.0 <= float(p) <= 1.0):
                    errors.append("L%d 颜色分量超出 0~1: %s" % (no, val[:60]))
                    break
        elif not is_float(val):
            errors.append("L%d 标量不是数字: %s" % (no, val[:60]))

    for k, hit in header_hits.items():
        if not hit:
            warnings.append("头部注释缺少「%s」" % k)

    dup = sorted({k for k in seen_keys if seen_keys.count(k) > 1})
    if dup:
        warnings.append("重复参数（后者覆盖前者）: %s" % ", ".join(dup))

    missing = [k for k in tpl_keys if k not in seen_keys]
    extra = [k for k in seen_keys if k not in allowed]
    if missing:
        errors.append("全量文件缺少 %d 项模板参数: %s" % (len(missing), ", ".join(missing[:10])))
    if extra:
        errors.append("多出 %d 项非模板参数: %s" % (len(extra), ", ".join(sorted(set(extra))[:10])))
    if base == "common":
        miss_kw = [k for k in tpl_keywords if k not in seen_keywords]
        if miss_kw:
            errors.append("缺少模板自带 KEYWORD: %s" % ", ".join(miss_kw))
    elif seen_keywords:
        errors.append("玻璃基底不应包含 KEYWORD 行")

    print("基底: %s | 模板参数 %d 项 | 文件参数 %d 项 | KEYWORD %d 条"
          % (base, len(tpl_keys), len(seen_keys), len(seen_keywords)))
    for w in warnings:
        print("WARN " + w)
    if errors:
        for e in errors:
            print("FAIL " + e)
        print("结果: FAIL (%d 个错误)" % len(errors))
        return 1
    print("结果: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
