# license-picker

<p>
  <img alt="license" src="https://img.shields.io/badge/license-MIT-2f7d4f">
  <img alt="python" src="https://img.shields.io/badge/python-3.9%2B-2f5f9e">
  <img alt="deps" src="https://img.shields.io/badge/dependencies-0-e6a13a">
  <img alt="PRs" src="https://img.shields.io/badge/PRs-welcome-7a4fd0">
</p>

> 五个问题，一份带理由的开源许可证推荐。离线、零依赖、能读懂。

## 为什么做这个

选许可证时大家通常遇到三种情况：直接抄别人的 `MIT`、被 choosealicense 的英文长文劝退、或者选了 GPL 却没意识到自己的库会被下游“传染”。

`license-picker` 只做一件事：把「能不能接受下游闭源」「要不要专利授权」「是库还是服务」这几个真正影响选择的判断，换算成一张**可解释**的分数表，然后告诉你排第一的是谁、为什么不是第二。

## 特性

- **零依赖**：只用 Python 标准库，克隆下来就能跑，不需要 `pip install`
- **数据与逻辑分离**：许可证放在 `license_picker/data/licenses.json`，加一种许可证不用改代码
- **可解释**：每条推荐都附逐条加减分理由，而不是一个黑盒答案
- **三种用法**：交互问答、`--profile` 预设画像、`--json` 给脚本消费
- **附带静态对比页**：`python tools/build_web.py` 生成一张可直接打开的 HTML 表格

## 快速开始

```bash
git clone https://github.com/wtw369762-sketch/license-picker_39.git
cd license-picker_39

# 交互问答（回车即用默认值）
python -m license_picker

# 或者用预设画像，跳过问答
python -m license_picker --profile library
python -m license_picker --list
```

想装成全局命令也可以，但不是必须：

```bash
pip install -e .
license-picker --profile saas
```

## 输出示例

```text
$ python -m license_picker --profile saas --top 2
==============================================================
优先推荐
==============================================================
AGPL-3.0（GNU Affero 通用公共许可证 3.0）
  类型：网络 copyleft ｜ 专利授权：有 ｜ OSI 认证：是
  得分：+7
  主要义务：衍生作品整体以 AGPL 分发；网络服务用户有权获取源码；提供完整对应源码
  理由：
    - 强 copyleft：能保证衍生作品继续开源
    - 含明确的专利授权条款
    - 网络服务场景下依然会触发开源义务，堵住 SaaS 漏洞

==============================================================
备选
==============================================================
GPL-3.0（GNU 通用公共许可证 3.0）
  类型：强 copyleft ｜ 专利授权：有 ｜ OSI 认证：是
  得分：+5
  主要义务：衍生作品整体以 GPL 分发；提供完整对应源码；不得附加额外限制
  理由：
    - 强 copyleft：能保证衍生作品继续开源
    - 含明确的专利授权条款
```

`--json` 会给出结构化结果，方便接进 CI 或别的工具：

```bash
python -m license_picker --profile hobby --json
```

## 预设画像

| 画像 | 适用场景 | 典型结果 |
|---|---|---|
| `library` | 被别人链接的库，允许闭源使用，涉及专利 | Apache-2.0 / LGPL-3.0 |
| `saas` | 网络服务，不希望被云厂商闭源托管 | AGPL-3.0 |
| `app` | 桌面或本地应用，希望衍生作品保持开源 | GPL-3.0 |
| `hobby` | 个人小工具，文本越短越好 | BSD-3-Clause / MIT |

> 同分并列是常态。分数只负责把候选缩到 2–3 个，最后一步仍然要人来看义务清单。

## 支持的许可证

`MIT`、`Apache-2.0`、`BSD-3-Clause`、`MPL-2.0`、`LGPL-3.0`、`GPL-3.0`、`AGPL-3.0`、`CC0-1.0`。

完整的义务与专利条款对比见 [docs/license-matrix.md](docs/license-matrix.md)，选型思路见 [docs/design.md](docs/design.md)。

## 项目结构

```text
license-picker_39/
├── license_picker/
│   ├── __init__.py          # 版本信息
│   ├── __main__.py          # python -m license_picker 入口
│   ├── cli.py               # 问答、预设画像、输出渲染
│   ├── core.py              # 打分模型与推荐理由
│   ├── rules.py             # 数据集加载与校验
│   └── data/licenses.json   # 8 种许可证的结构化数据
├── tests/test_core.py       # 18 个单元测试
├── tools/build_web.py       # 生成 web/index.html
├── web/index.html           # 生成的静态对比页
├── docs/                    # 设计与许可证对比文档
├── .github/                 # Issue / PR 模板
├── LICENSE                  # 本项目采用 MIT
└── README.md
```

## 开发

```bash
python -m unittest discover -s tests -v   # 跑测试
python tools/build_web.py                 # 重新生成对比页
```

改了 `licenses.json` 之后请务必跑一遍测试：校验会拦住字段缺失、分类拼错和 SPDX 重复。

## 路线图

- [x] 8 种常见许可证的结构化数据
- [x] 打分模型与可解释输出
- [x] 交互问答与 `--json` 输出
- [x] 静态对比页自动生成
- [ ] 许可证兼容性检查（例如 Apache-2.0 代码进入 GPL-2.0 项目）
- [ ] 根据 `pyproject.toml` / `package.json` 自动探测项目形态
- [ ] 英文界面

## 参与贡献

欢迎提 Issue 和 PR，流程见 [CONTRIBUTING.md](CONTRIBUTING.md)。参与本项目即表示同意遵守 [行为准则](CODE_OF_CONDUCT.md)。

## 许可证

本项目采用 [MIT 许可证](LICENSE)。

选它的理由很具体：这个工具希望被直接复制进课程作业、内部脚手架和别人的小工具里，MIT 的义务只有“保留声明”一条，摩擦最小；项目本身也不含需要专利保护的实现，所以不需要 Apache-2.0 的专利条款。

## 致谢

许可证义务的表述参考了 [choosealicense.com](https://choosealicense.com/)、[SPDX License List](https://spdx.org/licenses/) 与 [OSI](https://opensource.org/licenses) 的公开文本。本项目是《开源文化运动》课程期末作业。
