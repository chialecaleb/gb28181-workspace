# GB28181 Workspace

国标平台与协议模拟实验室的开发协作工作区。管理共同开发入口、用户事项、原始标准资料与联调证据；不包含产品代码，不提供产品运行时服务。

| 仓库 | 技术与职责 |
| --- | --- |
| [gb28181-hub](https://github.com/chialecaleb/gb28181-hub) | Java + Netty / Spring Cloud Alibaba + Vue，国标接入与管理 |
| [gb28181-lab](https://github.com/chialecaleb/gb28181-lab) | Go + React，Wails 桌面/Linux Web，设备与平台模拟、协议实验 |

三个独立 Git 仓库，默认 main 最新实现；无 submodule 和组合版本锁。产品目录在本仓库 .gitignore 中忽略，clone 本仓库不会自动下载产品。

## 开始

前置 Python 3.10+、Git。`python scripts/workspace.py status` 查看目录、Git 状态与远程；`python scripts/workspace.py sync` 只打印计划，`python scripts/workspace.py sync --apply` 获取缺失仓库并对干净的 main 执行 fetch 与 fast-forward。脚本遇到脏工作区、错误远程、非 main 或分叉会拒绝，不自动 stash/reset/强推。

单项目开发在子仓库启动 Agent；跨项目比较与联调在这里启动，先读 [AGENTS](AGENTS.md)并显式读取涉及的产品规则。VS Code 可打开 gb28181.code-workspace。

## 文档

- [文档导航](docs/README.md)：工作流、架构边界、联调与标准。
- [用户事项唯一清单](USER-ACTIONS.md)：所有用户决定、外部配置与人工检查。
- [当前状态](docs/delivery/status.md)：实际交付与后续。
- [标准资料](docs/standards/README.md)：两项原文、OCR、图片与哈希。
- [开发指南](CONTRIBUTING.md)与[评审](REVIEW.md)。

验证入口：`python scripts/verify.py`。当前只有文档和工作区工具，两款应用均尚未实现，无可用启动/联调命令或安装包。仓库组织跟随最新实现，具体依赖、标准引用和测试证据仍需要可复现记录。
