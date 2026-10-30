# 贡献指南

感谢你愿意改进 license-picker。这个项目很小，所以流程也尽量短。

## 先开 Issue 的情况

- 想新增许可证或修改已有条款描述
- 想调整打分权重
- 发现推荐结果与你预期不符

条款描述涉及事实，先说清楚依据（官方文本链接、SPDX 页面），比直接提 PR 更快。

## 分支管理

我们采用一条长期分支加短生命周期特性分支的模型：

```text
main                 受保护，始终可运行、测试全绿
├── feature/web-page      新增功能
├── fix/agpl-reason       修 bug
└── docs/faq              只改文档
```

规则：

1. 从最新的 `main` 切分支，命名用 `feature/`、`fix/`、`docs/` 前缀加简短描述；
2. 分支生命周期尽量不超过一周，避免和 `main` 拉开太远；
3. 合并前先把 `main` 合进自己的分支解冲突，**不要在 PR 里制造新的冲突**；
4. 合并后删除远端分支。

## 提交信息

采用 Conventional Commits：

```text
feat: 增加 MPL-2.0 专利条款说明
fix: 修正 AGPL 在网络服务场景的降权条件
docs: 补充 BSD-3 与 MIT 的差异
test: 覆盖并列排序的稳定性
chore: 更新编辑器配置
```

一次提交只做一件事。改数据的提交和改逻辑的提交请分开，方便回滚。

## 提 PR 之前

```bash
python -m unittest discover -s tests -v
python tools/build_web.py
```

- 测试必须全绿；
- 改了 `licenses.json` 要同步 `docs/license-matrix.md`；
- 改了 `tools/build_web.py` 要提交重新生成的 `web/index.html`；
- PR 描述里写清楚“改了什么、为什么、怎么验证”。

## 审查清单

- [ ] 新许可证的 SPDX 标识与官方一致
- [ ] `obligations` 是可执行的动作，不是形容词
- [ ] 新增测试覆盖了新的分支逻辑
- [ ] 没有引入第三方依赖（本项目的卖点之一）
- [ ] 中文表述与现有文档风格一致

## 行为准则

参与本项目即表示同意遵守 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。技术分歧请针对代码和依据，不要针对人。
