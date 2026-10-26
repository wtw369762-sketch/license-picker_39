"""命令行入口：交互问答 / 预设画像 / JSON 输出。"""

from __future__ import annotations

import argparse
import json
import sys

from .core import Preferences, top

PROFILES = {
    "library": Preferences(allow_closed_source=True, need_patent_grant=True, is_library=True),
    "saas": Preferences(
        allow_closed_source=False,
        need_patent_grant=True,
        is_network_service=True,
    ),
    "app": Preferences(allow_closed_source=False),
    "hobby": Preferences(allow_closed_source=True, keep_it_short=True),
}

QUESTIONS = [
    ("allow_closed_source", "是否允许下游闭源使用你的代码？", True),
    ("need_patent_grant", "项目是否涉及专利，需要明确的专利授权？", False),
    ("is_library", "它是否主要作为库被其他项目链接？", False),
    ("is_network_service", "它是否以网络服务（SaaS）形式对外提供？", False),
    ("keep_it_short", "是否希望许可文本尽量短？", False),
]

SIGNS = {"y": True, "yes": True, "是": True, "n": False, "no": False, "否": False}


def pad(text: str, width: int) -> str:
    """按显示宽度补空格：中日韩字符占两列，避免列表错位。"""
    shown = sum(2 if ord(char) > 0x2E7F else 1 for char in text)
    return text + " " * max(0, width - shown)


def ask_bool(prompt: str, default: bool) -> bool:
    """问一个是非题，回车取默认值，输入非法时重问。"""
    hint = " [Y/n] " if default else " [y/N] "
    while True:
        try:
            answer = input(prompt + hint).strip().lower()
        except EOFError:
            return default
        if not answer:
            return default
        if answer in SIGNS:
            return SIGNS[answer]
        print("  请输入 y 或 n（直接回车用默认值）。")


def collect_interactive() -> Preferences:
    print("license-picker：5 个问题，帮你缩小到合适的许可证。\n")
    values = {}
    for name, prompt, default in QUESTIONS:
        values[name] = ask_bool(prompt, default)
        print()
    return Preferences(**values)


def render(rec) -> str:
    lic = rec.license
    flag = "有" if lic.patent_grant else "无"
    lines = [
        "%s（%s）" % (lic.spdx, lic.name_zh),
        "  类型：%s ｜ 专利授权：%s ｜ OSI 认证：%s"
        % (lic.category_label, flag, "是" if lic.osi_approved else "否"),
        "  得分：%+d" % rec.score,
        "  主要义务：%s" % "；".join(lic.obligations),
        "  理由：",
    ]
    if rec.reasons:
        lines.extend("    - %s" % reason for reason in rec.reasons)
    else:
        lines.append("    - 对你给出的条件没有明显加分或减分项")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="license-picker",
        description="根据项目特征推荐开源许可证（离线、无第三方依赖）。",
    )
    parser.add_argument(
        "-p",
        "--profile",
        choices=sorted(PROFILES),
        help="使用预设画像，跳过问答：library / saas / app / hobby",
    )
    parser.add_argument("-n", "--top", type=int, default=3, help="输出前 N 名，默认 3")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出，便于脚本调用")
    parser.add_argument("--list", action="store_true", help="列出数据集里的全部许可证")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)

    if args.list:
        from .rules import load_licenses

        for lic in load_licenses():
            print("%s%s %s" % (pad(lic.spdx, 14), pad(lic.category_label, 14), lic.name_zh))
        return 0

    prefs = PROFILES[args.profile] if args.profile else collect_interactive()
    ranked = top(prefs, count=max(1, args.top))

    if args.json:
        payload = {
            "preferences": prefs.__dict__,
            "recommendations": [
                {
                    "spdx": item.spdx,
                    "name_zh": item.license.name_zh,
                    "category": item.license.category,
                    "score": item.score,
                    "reasons": list(item.reasons),
                    "obligations": list(item.license.obligations),
                }
                for item in ranked
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print("=" * 62)
    print("优先推荐")
    print("=" * 62)
    print(render(ranked[0]))
    if len(ranked) > 1:
        print("\n" + "=" * 62)
        print("备选")
        print("=" * 62)
        for item in ranked[1:]:
            print(render(item))
            print()
    print("提示：落盘前请把许可证全文放进仓库根目录的 LICENSE 文件。")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
