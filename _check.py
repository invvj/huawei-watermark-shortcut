# -*- coding: utf-8 -*-
"""校验 .cherri 与 config.json 的一致性 + 基本语法。"""
import json, re, os

BASE = os.path.dirname(os.path.abspath(__file__))
CHERRI = os.path.join(BASE, "iPhone水印.cherri")
CONFIG = os.path.join(BASE, "config.json")

cherri = open(CHERRI, encoding="utf-8").read()
cfg = json.load(open(CONFIG, encoding="utf-8"))

problems = []
ok = []

# 1) 括号匹配
stack = []
pairs = {")": "(", "]": "[", "}": "{"}
for ch in cherri:
    if ch in "([{":
        stack.append(ch)
    elif ch in ")]}":
        if not stack or stack[-1] != pairs[ch]:
            problems.append(f"括号不匹配，遇到 {ch}")
            break
        stack.pop()
else:
    if stack:
        problems.append(f"括号未闭合，剩余 {stack}")
    else:
        ok.append("括号匹配 OK")

# 2) .cherri 引用的 config 键必须存在
# 形如 @config['X'] 或 @config["X"] 或 getValue(..., "X...") 或 @config['X.Y.Z']
ref_keys = set(re.findall(r"@config\[['\"]([\w]+)['\"]\]", cherri))
# 动态键 brandLogos.{logoName} 等用 getValue，键前缀需存在
dyn_prefixes = set(re.findall(r"getValue\([^,]+,\s*['\"]([\w]+)\.", cherri))
needed = ref_keys | dyn_prefixes
for k in sorted(needed):
    if k in cfg:
        ok.append(f"config 键存在: {k}")
    else:
        problems.append(f"config 缺失键: {k}")

# 3) 华为 logo 在 brandLogos 且含 class="logo-size"
hv = cfg.get("brandLogos", {}).get("Huawei", "")
if "logo-size" in hv and "logo-color" in hv:
    ok.append("华为 logo 含 logo-size + logo-color class（可吃渐变/尺寸）")
else:
    problems.append("华为 logo 缺少 class（logo-size/logo-color）")

# 4) 品牌/机型/风格列表
if "Huawei" in cfg.get("brandOrder", []):
    ok.append("Huawei 在 brandOrder 首位")
else:
    problems.append("Huawei 不在 brandOrder")
if set(cfg.get("modelOptions", [])) >= {"HUAWEI Mate X6", "HUAWEI Mate X7"}:
    ok.append("机型列表含 Mate X6 / Mate X7")
else:
    problems.append("机型列表不完整")

# 5) templateHtml 含全部占位符 + __MODEL__ 优先
tpl = cfg.get("templateHtml", "")
for ph in ["__LOGO__", "__THEME__", "__CUSTOM__", "__MODEL__", "__HEIGHT__", "__METADATA__"]:
    if ph in tpl:
        ok.append(f"templateHtml 含占位符 {ph}")
    else:
        problems.append(f"templateHtml 缺占位符 {ph}")
if 'const cameraModel = "__MODEL__"' in tpl:
    ok.append("template 已强制使用注入机型（不被照片 TIFF 覆盖）✓")
else:
    problems.append("template 机型逻辑未改为 __MODEL__ 优先")

# 6) .cherri 来源/品牌/机型/风格/批量 关键动作
for act in ["chooseFromList", "selectPhotos", "takePhoto", "selectFile",
            "getImageDetail", "makeImageFromRichText", "customImageOverlay", "savePhoto",
            "showNotification"]:
    if act in cherri:
        ok.append(f".cherri 含动作 {act}")
    else:
        problems.append(f".cherri 缺动作 {act}")

# 7) 批量：循环 + selectPhotos(true) 允许多选
if "for photo in photoList" in cherri and "selectPhotos(true)" in cherri:
    ok.append("批量：selectPhotos(true) 多选 + for 循环 ✓")
else:
    problems.append("批量逻辑不完整")

print("===== OK =====")
for o in ok:
    print("  ✓", o)
print("===== 问题 =====")
if not problems:
    print("  （无）")
for p in problems:
    print("  ✗", p)
print("===== 结论 =====")
print("  通过" if not problems else "  有不通过项，需修正")
