# 工作区组织设计

父目录是 gb28181-workspace，产品目录是各自独立 Git 根。父 .gitignore 排除产品目录，manifest 只记录路径、URL、main，不存产品固定 SHA。gb28181.code-workspace 仅方便编辑器导航，不改变 Git 或 Agent 规则加载范围。

## 工具

`scripts/workspace.py status` 检查目录、Git 根、origin、分支、工作区状态；`sync` 默认预览，`sync --apply` 对不存在的目录 clone，对已存在且远程/分支正确、工作区干净的仓库 fetch 后 fast-forward。目录越界、符号链接、错误 Git 根、origin 不匹配、非 main、脏树、本地超前或分叉都报错并保留现场，不自动 reset、stash、checkout 或强推。

manifest 中 URL 属于受审查配置，不从远程 README 或任意输入自动执行命令。脚本使用 subprocess 参数数组，Git 失败非零退出；先预检现有两个仓库，避免已知错误时更新另一仓库。网络阶段仍可能部分完成，状态输出明确范围；重试前先查看状态。

## 文档与资料

产品需求/设计/解释归产品；共同联调与原始标准归工作区。产品的共享链接使用 GitHub URL，工作区本机路径不进入产品代码。独立 clone 后不要求兄弟产品存在；运行时标准浏览采用本地导入或许可允许的打包。原文哈希是资料完整性，不是完整符合性证明。

用户事项统一到根 USER-ACTIONS；产品导航保留旧锚点和迁移说明。开发后续各自记录 status，Agent 能完成的事不变成用户审批任务。重要跨项目决定在这里记录，产品适用影响在产品 ADR 记录。

## 验证

verify.py 聚合文档登记/链接、标准清单/哈希、工具回归、语法和空白检查；不从产品目录递归构建应用。涉及产品时分别执行其门禁。GitHub CI 用同一入口，Ruleset 生效前须有一次真实成功的 repository-quality；外部状态与期望 JSON 分开记录。
