# 工作区开发指南

先读 [AGENTS](AGENTS.md) 与[文档导航](docs/README.md)。这里只维护协作基础，不实现 Java/Go 应用，也不把产品目录纳入 Git。

使用 Python 3.10+、Git。仓库获取与更新：`python scripts/workspace.py status`、`python scripts/workspace.py sync`，确认计划后用 `sync --apply` 执行；不覆盖本地修改。工作区更新脚本不自动合并产品功能分支。

文档变更同步登记与索引；新增工具包含有意义的失败路径回归。按路径暂存后运行 `python scripts/verify.py` 并阅读最终差异，按[Git 规则](docs/dev-rules/git-and-github.md)提交。共享标准移动核对逐文件哈希，原文不可静默修改。

跨项目任务分开记录双方修改与验证，使用[联调流程](docs/integration/workflow.md)。用户事项只维护 [USER-ACTIONS](USER-ACTIONS.md)，工程后续放 status。许可证尚未确定，不能继承参考工程的许可声明。
