# 更新日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 与 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 计划中

- 许可证兼容性检查
- 从 `pyproject.toml` / `package.json` 探测项目形态
- 英文界面

## [0.3.0] - 2026-10-31

### 新增

- 交互问答模式，回车即采用默认值
- `--profile` 预设画像：`library` / `saas` / `app` / `hobby`
- `--json` 结构化输出，便于脚本消费
- 静态对比页由 `tools/build_web.py` 从数据集生成
- 许可证数量扩到 8 种，补上 `CC0-1.0`

### 变更

- 决策树重构为打分模型，每条推荐附带加减分理由
- 并列结果的排序改为按 SPDX 字母序，保证多次运行稳定

### 修复

- 中英文混排时 `--list` 输出错位

## [0.2.0] - 2026-10-26

### 新增

- `--list` 列出全部许可证
- 单元测试覆盖数据集校验与打分边界

### 变更

- 数据集从 Python 字面量迁到 `licenses.json`，新增许可证不再需要改代码

## [0.1.0] - 2026-10-24

### 新增

- 项目骨架与 4 种许可证数据（MIT / Apache-2.0 / GPL-3.0 / AGPL-3.0）
- MIT 许可证与 README 初稿
