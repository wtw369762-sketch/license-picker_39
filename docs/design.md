# 设计与取舍

## 为什么不用决策树

最初的版本是一棵决策树：

```text
允许闭源?
├─ 是 → 涉及专利?
│        ├─ 是 → Apache-2.0
│        └─ 否 → MIT
└─ 否 → 是网络服务?
         ├─ 是 → AGPL-3.0
         └─ 否 → GPL-3.0
```

它跑起来没问题，但有三个毛病：

1. **无法解释“为什么不是另一个”**。用户看到 MIT，不知道自己离 Apache-2.0 差在哪一条。
2. **维度一多就爆炸**。5 个布尔条件足以让树变成 32 个叶子，加一个条件就要重画。
3. **无法表达并列**。真实场景里 Apache-2.0 和 LGPL-3.0 常常同样合理，树必须强行二选一。

现在改成打分模型：每个许可证对每个偏好给出固定加减分，最后排序。代价是要手工调权重，收益是每条结论都能追溯到具体条款。

## 打分表

| 条件 | 许可证类型 | 分值 | 说明 |
|---|---|---|---|
| 允许下游闭源 | 宽松 | +3 | 商业采用门槛最低 |
| 允许下游闭源 | 强 / 网络 copyleft | −3 | 会要求下游开源 |
| 允许下游闭源 | 弱 copyleft | +1 | 折中 |
| 不允许下游闭源 | 强 / 网络 copyleft | +3 | 能保证衍生作品继续开源 |
| 不允许下游闭源 | 宽松 | −2 | 无法阻止闭源 |
| 需要专利授权 | 有专利条款 | +2 | Apache / MPL / LGPL / GPL / AGPL |
| 需要专利授权 | 无专利条款 | −2 | MIT / BSD |
| 作为库使用 | 弱 copyleft | +2 | 正是 LGPL / MPL 的设计目的 |
| 作为库使用 | 强 copyleft | −1 | 会传染调用方 |
| 网络服务 | 网络 copyleft | +2 | 堵住 SaaS 漏洞 |
| 非网络服务 | 网络 copyleft | −1 | 额外义务用不上，属于过度约束 |
| 要求文本简短 | MIT / BSD / CC0 | +1 | 一页纸以内 |
| 要求文本简短 | Apache-2.0 | −1 | 正文长，还要维护 NOTICE |
| 需要专利且不处理专利 | CC0 | −3 | 公共领域贡献不涉及专利 |

排序规则：得分降序，同分按 SPDX 字母序，保证多次运行结果稳定（有测试覆盖）。

## 数据结构

```json
{
  "spdx": "Apache-2.0",
  "name_zh": "Apache 许可证 2.0",
  "category": "permissive",
  "patent_grant": true,
  "trademark_grant": false,
  "osi_approved": true,
  "software_ready": true,
  "summary": "……",
  "obligations": ["……"],
  "good_for": ["……"]
}
```

`category` 只有五个合法取值：`permissive`、`weak-copyleft`、`strong-copyleft`、`network-copyleft`、`public-domain`。写错会在加载阶段直接抛 `LicenseDataError`，不会带着脏数据跑到打分环节。

## 新增一种许可证

1. 在 `license_picker/data/licenses.json` 里追加一条，字段照抄现有条目；
2. 跑 `python -m unittest discover -s tests`，确认没有字段缺失或 SPDX 重复；
3. 跑 `python tools/build_web.py` 重新生成对比页；
4. 如果它有特殊条款需要额外加减分，再改 `core.py` 的 `score_license` 并补一条测试。

## 已知局限

- **不判断许可证兼容性**。把 Apache-2.0 代码并进 GPL-2.0 项目是兼容性事故，但本项目只做“选一个”，不做“组合检查”。已列入路线图。
- **不构成法律意见**。只处理条款层面的常见差异，不涉及专利有效性、属地法律和具体商业条款。
- **只有 8 种许可证**。`BSL-1.0`、`EPL-2.0`、`Unlicense` 等尚未收录，数据文件是开放的，欢迎 PR。
- **打分权重是启发式的**。它反映的是常见工程实践，不是法律结论；同分并列时请回到义务清单人工判断。
