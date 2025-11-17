# Service 接口清单

## ProcessService
- 签名：`toggle() -> None`, `start() -> None`, `stop() -> bool`, `refresh_status() -> None`, `monitor() -> None`
- 功能：管理 ComfyUI 进程的启动/停止与状态刷新
- 依赖：`core.process_manager`, 端口探测(`core.probe`), `runner_start/runner_stop`

## VersionService
- 签名：
  - `refresh(scope: str = "all") -> None`
  - `is_stable_version(tag: str) -> bool`
  - `get_latest_stable_kernel(force_refresh: bool = False) -> Dict[str, Any]`
  - `upgrade_latest(stable_only: bool = True) -> Dict[str, Any]`
  - `upgrade_to_commit(commit: str, stable_only: bool = False) -> Dict[str, Any]`
  - `get_current_kernel_version() -> Dict[str, Any]`
- 功能：查询与升级内核版本，获取稳定版本与当前版本
- 依赖：`git` 可执行、GitHub Releases API（网络）、仓库根路径

## UpdateService
- 签名：
  - `update_frontend(notify: bool = False) -> Dict[str, Any]`
  - `update_templates(notify: bool = False) -> Dict[str, Any]`
  - `perform_batch_update() -> Tuple[List[Dict[str, Any]], str]`
  - `get_frontend_version() -> Optional[str]`
  - `get_templates_version() -> Optional[str]`
- 功能：前端与模板库版本查询与更新、批量更新摘要生成
- 依赖：`pip` 安装/更新、PyPI 代理设置、`python_exec`

## ConfigService
- 签名：
  - `load() -> dict`, `save(data: dict | None = None) -> None`
  - `get(key_path: str, default: Any = None) -> Any`
  - `set(key_path: str, value: Any) -> None`
  - `update_launch_options(**kwargs) -> None`
  - `update_proxy_settings(**kwargs) -> None`
  - `get_config() -> dict`
- 功能：配置读写与选项更新
- 依赖：文件系统(`launcher/config.json`)

## GitService
- 签名：
  - `resolve_git() -> Tuple[Optional[str], str]`
  - `apply_to_manager(git_path: str) -> None`
- 功能：解析 Git 路径并写入 ComfyUI-Manager 配置
- 依赖：`git` 可执行、`user/default/ComfyUI-Manager/config.ini`

## NetworkService
- 签名：`apply_pip_proxy_settings() -> None`
- 功能：将 PyPI 代理设置应用到 `pip.ini`
- 依赖：`python_exec`、文件系统

## RuntimeService
- 签名：`pre_start_up() -> None`
- 功能：运行前准备（创建模板目录等）
- 依赖：`python_exec` 对应的 site-packages 目录