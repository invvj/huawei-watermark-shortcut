# -*- coding: utf-8 -*-
"""
把改造后的 template.html + 华为 logo 内联进 config.json，
让整套快捷指令只依赖「1 个 config.json」（不再拉远程 template/menu/背景图）。
最终 config.json 含:
  - templateHtml : 改好的整页 HTML（__MODEL__ 优先）
  - brandLogos   : 原 10 品牌内联 SVG + 华为(加 class 适配渐变)
  - modelOptions : ["HUAWEI Mate X6","HUAWEI Mate X7"]
  - 纯色主题(浅色/深色/玫瑰金)，无远程背景图依赖
"""
import json, re, os

BASE = os.path.dirname(os.path.abspath(__file__))
SRC_CONFIG = os.path.join(BASE, "config.json")          # 根目录原 config(v4)，含 10 品牌内联 SVG
TEMPLATE   = os.path.join(BASE, "template.html")        # 已改 __MODEL__ 优先
HUAWEI_SVG = r"E:\Python定制脚本\camera-watermark-plugins\image-watermark\presets\huawei.svg"
OUT        = os.path.join(BASE, "config.json")          # 原地覆盖

def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

# 1) 读原 config（含 10 品牌内联 SVG）
cfg = json.loads(read(SRC_CONFIG))

# 2) 读改造后的 template，作为 templateHtml 内联
template_html = read(TEMPLATE)

# 3) 准备华为 SVG：加 class 以适配模板的渐变/尺寸系统
hv = read(HUAWEI_SVG)
hv = re.sub(r"<svg\b", '<svg class="logo-size"', hv, count=1)
hv = re.sub(r"<path\b", '<path class="logo-color"', hv, count=1)

# 4) 组装新 config
cfg["v"] = "huawei1"
cfg["templateHtml"] = template_html          # 内联模板，.cherri 直接取用，不再 downloadURL
cfg.pop("template", None)                    # 删除旧的远程 template 字段
cfg.pop("assets", None)                       # 删除远程 base/cacheDir

# 品牌：华为置顶，方便默认选
order = cfg.get("brandOrder", [])
if "Huawei" not in order:
    order.insert(0, "Huawei")
cfg["brandOrder"] = order
cfg["brandLogos"]["Huawei"] = hv

# 风格：只保留贴近真机的两种（白字/黑字），去掉渐变与远程背景
cfg["styleOrder"] = ["浅色（暗图用）", "深色（亮图用）"]
cfg["styles"] = {
    "浅色（暗图用）": {"background": "", "slot": "", "css": "Light"},
    "深色（亮图用）": {"background": "", "slot": "", "css": "Dark"},
}

# 机型：一键选 Mate X6 / X7
cfg["modelOptions"] = ["HUAWEI Mate X6", "HUAWEI Mate X7"]
cfg["modelDefault"] = "HUAWEI Mate X6"
cfg["promptModel"] = "请选择华为机型"

# 提示语
cfg["promptSource"] = "请选择要添加水印的照片（可多选批量）"
cfg["promptLogo"]   = "请选择水印品牌图标"
cfg["promptStyle"]  = "请选择水印风格"
cfg["msgDone"]     = "华为水印添加成功～请前往相册查看🎉"

# 不再需要旧的文字模式菜单
cfg.pop("textModes", None)
cfg.pop("textDefault", None)
cfg.pop("modelDefault_old", None)

# 5) 写出（保留中文，UTF-8）
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(cfg, f, ensure_ascii=False, indent=2)

print("OK config.json 已生成")
print("  总大小:", os.path.getsize(OUT), "bytes")
print("  品牌:", cfg["brandOrder"])
print("  风格:", cfg["styleOrder"])
print("  机型:", cfg["modelOptions"])
print("  含 templateHtml:", "templateHtml" in cfg and len(cfg["templateHtml"]) > 1000)
print("  含华为 logo:", "Huawei" in cfg["brandLogos"])
