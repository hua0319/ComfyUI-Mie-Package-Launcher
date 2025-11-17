# 缺陷与改进建议

## 缺陷摘要
- `ProcessManager.toggle_comfyui` 端口占用分支依赖 GUI 交互；在 headless 测试中不可触达，建议统一走日志与自动化策略。
- `RuntimeService.pre_start_up` 对非 exe 环境路径解析依赖 `sysconfig`，在打包环境可能不稳定；建议注入路径或在 Service 层暴露配置。
- `GitService.apply_to_manager` 依赖 `paths.comfyui_root`，界面设置与 Service 使用需要完全统一；已统一为 `root + ComfyUI`，但部分遗留代码仍取绝对 `comfyui_path`。
- 多处 UI 代码未覆盖导致整体覆盖率未达 85%，但这些不属于 Service 范畴；建议按模块拆分覆盖率指标。

## 影响
- 在真实运行的环境中，若已有 ComfyUI 实例运行，接口测试需要先行终止；已提供 `stop_all_comfyui_instances`，但在权限不足时可能失败。

## 建议
- 把 `ProcessManager` 的占用处理抽象为策略接口，可由 Service 注入无界面实现。
- 为 `VersionService` 增加离线缓存与代理重试，降低网络波动影响。
- 为 `UpdateService` 增加安装超时与错误码映射，便于测试断言更细化。