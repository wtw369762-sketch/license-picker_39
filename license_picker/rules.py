"""许可证数据集的加载与校验。

数据集放在 ``license_picker/data/licenses.json``，以 SPDX 标识为主键。
新增许可证只需改数据文件，不必动代码。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "data" / "licenses.json"

CATEGORY_LABELS = {
    "permissive": "宽松",
    "weak-copyleft": "弱 copyleft",
    "strong-copyleft": "强 copyleft",
    "network-copyleft": "网络 copyleft",
    "public-domain": "公共领域",
}

REQUIRED_FIELDS = {
    "spdx",
    "name_zh",
    "category",
    "patent_grant",
    "trademark_grant",
    "osi_approved",
    "software_ready",
    "summary",
    "obligations",
    "good_for",
}


class LicenseDataError(ValueError):
    """数据集字段缺失或取值非法。"""


@dataclass(frozen=True)
class License:
    spdx: str
    name_zh: str
    category: str
    patent_grant: bool
    trademark_grant: bool
    osi_approved: bool
    software_ready: bool
    summary: str
    obligations: tuple
    good_for: tuple

    @property
    def category_label(self) -> str:
        return CATEGORY_LABELS.get(self.category, self.category)

    @property
    def is_copyleft(self) -> bool:
        return self.category in {"strong-copyleft", "network-copyleft"}

    @property
    def is_weak_copyleft(self) -> bool:
        return self.category == "weak-copyleft"


def parse_license(raw: dict) -> License:
    missing = REQUIRED_FIELDS - set(raw)
    if missing:
        raise LicenseDataError(
            "许可证 %s 缺少字段：%s" % (raw.get("spdx", "<未知>"), ", ".join(sorted(missing)))
        )
    if raw["category"] not in CATEGORY_LABELS:
        raise LicenseDataError(
            "许可证 %s 的 category 非法：%s" % (raw["spdx"], raw["category"])
        )
    return License(
        spdx=raw["spdx"],
        name_zh=raw["name_zh"],
        category=raw["category"],
        patent_grant=bool(raw["patent_grant"]),
        trademark_grant=bool(raw["trademark_grant"]),
        osi_approved=bool(raw["osi_approved"]),
        software_ready=bool(raw["software_ready"]),
        summary=raw["summary"],
        obligations=tuple(raw["obligations"]),
        good_for=tuple(raw["good_for"]),
    )


def load_licenses(path=None):
    """读取并校验全部许可证，返回按 SPDX 排序的列表。"""
    file = Path(path) if path else DATA_FILE
    with file.open(encoding="utf-8") as handle:
        raw_list = json.load(handle)
    if not isinstance(raw_list, list) or not raw_list:
        raise LicenseDataError("数据集必须是非空数组")
    licenses = [parse_license(item) for item in raw_list]
    duplicates = {lic.spdx for lic in licenses if [x.spdx for x in licenses].count(lic.spdx) > 1}
    if duplicates:
        raise LicenseDataError("SPDX 标识重复：%s" % ", ".join(sorted(duplicates)))
    return sorted(licenses, key=lambda lic: lic.spdx)


def find(spdx, licenses=None):
    """按 SPDX 标识精确查找，找不到时抛 KeyError。"""
    pool = licenses if licenses is not None else load_licenses()
    for lic in pool:
        if lic.spdx == spdx:
            return lic
    raise KeyError("未知的 SPDX 标识：%s" % spdx)
