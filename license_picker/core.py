"""打分模型：把项目偏好换算成每个许可证的得分与推荐理由。

这里刻意不用决策树，因为决策树对新用户是一串黑盒分支；打分模型能给出
"为什么是它、为什么不是别人"，方便在 README 与课堂上解释。
"""

from __future__ import annotations

from dataclasses import dataclass

from .rules import load_licenses

# 打分权重集中在这里，方便调整后一眼看出影响范围
PATENT_BONUS = 2
PATENT_MALUS = -2


@dataclass(frozen=True)
class Preferences:
    """用户对项目的五个判断。"""

    allow_closed_source: bool = True
    need_patent_grant: bool = False
    is_library: bool = False
    is_network_service: bool = False
    keep_it_short: bool = False


@dataclass(frozen=True)
class Recommendation:
    license: object
    score: int
    reasons: tuple

    @property
    def spdx(self) -> str:
        return self.license.spdx


def score_license(license, prefs: Preferences) -> Recommendation:
    """按偏好给单个许可证打分，返回得分与逐条理由。"""
    score = 0
    reasons = []

    # 1. 是否允许下游闭源：这是最关键的一维
    if prefs.allow_closed_source:
        if license.category == "permissive":
            score += 3
            reasons.append("宽松许可：下游可以闭源，商业采用门槛最低")
        elif license.is_copyleft:
            score -= 3
            reasons.append("强 copyleft：会要求下游开源，可能劝退商业用户")
        elif license.is_weak_copyleft:
            score += 1
            reasons.append("弱 copyleft：改动需要开源，调用方仍可闭源")
    else:
        if license.is_copyleft:
            score += 3
            reasons.append("强 copyleft：能保证衍生作品继续开源")
        elif license.is_weak_copyleft:
            score += 1
            reasons.append("弱 copyleft：只锁住被修改的文件，保护范围有限")
        else:
            score -= 2
            reasons.append("宽松许可：无法阻止别人闭源你的代码")

    # 2. 专利条款
    if prefs.need_patent_grant:
        if license.patent_grant:
            score += PATENT_BONUS
            reasons.append("含明确的专利授权条款（如 Apache-2.0 第 3 条）")
        else:
            score += PATENT_MALUS
            reasons.append("没有专利授权条款，专利权人仍可单独主张")

    # 3. 是否作为被链接的库
    if prefs.is_library:
        if license.is_weak_copyleft:
            score += 2
            reasons.append("适合作为库被其他项目链接")
        if license.category == "strong-copyleft":
            score -= 1
            reasons.append("作为库使用会把开源义务传染给调用方")

    # 4. 是否是网络服务
    if prefs.is_network_service and license.category == "network-copyleft":
        score += 2
        reasons.append("网络服务场景下依然会触发开源义务，堵住 SaaS 漏洞")
    if not prefs.is_network_service and license.category == "network-copyleft":
        score -= 1
        reasons.append("不是网络服务，AGPL 的额外义务用不上，属于过度约束")

    # 5. 是否要求文本简短
    if prefs.keep_it_short:
        if license.spdx in {"MIT", "BSD-3-Clause", "CC0-1.0"}:
            score += 1
            reasons.append("许可文本短，适合要求极简的项目")
        if license.spdx == "Apache-2.0":
            score -= 1
            reasons.append("文本较长，还要求长期维护 NOTICE 文件")

    # 6. 不处理专利的公共领域许可，在专利敏感场景要额外降权
    if not license.software_ready and prefs.need_patent_grant:
        score -= 3
        reasons.append("属于著作权层面的公共领域贡献，不涉及专利授权")

    return Recommendation(license=license, score=score, reasons=tuple(reasons))


def recommend(prefs: Preferences, licenses=None):
    """返回按得分降序排列的推荐列表，同分按 SPDX 字母序稳定排序。"""
    pool = licenses if licenses is not None else load_licenses()
    scored = [score_license(lic, prefs) for lic in pool]
    scored.sort(key=lambda item: (-item.score, item.spdx))
    return scored


def top(prefs: Preferences, count: int = 3, licenses=None):
    """只取前 ``count`` 名，便于 CLI 输出。"""
    return recommend(prefs, licenses)[:count]
