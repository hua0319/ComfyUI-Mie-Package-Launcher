# 迁移指南（模块化重构）

## 导入路径迁移对照

- `from logger_setup import install_logging` → `from utils.logging import install_logging`
- `import paths as PATHS` → `from utils import paths as PATHS`
- `import pip_utils as PIPUTILS` → `from utils import pip as PIPUTILS`
- `import net_utils as NETUTILS` → `from utils import net as NETUTILS`
- `from utils import run_hidden, have_git, is_git_repo` → `from utils.common import run_hidden, have_git, is_git_repo`
- `from version_manager import VersionManager` → `from core.version_manager import VersionManager`
- `from process_manager import ProcessManager` → `from core.process_manager import ProcessManager`
- `import assets as ASSETS` → `from ui import assets_helper as ASSETS`

## 模块职责说明

- `core/`：核心业务逻辑
  - `process_manager.py`：ComfyUI 子进程的启动/停止/监控
  - `version_manager.py`：内核版本查询与更新

- `ui/`：界面与资源
  - `theme.py`、各 `*_panel.py`：UI 组件
  - `assets_helper.py`：窗口图标解析与应用

- `utils/`：通用工具
  - `paths.py`：路径解析与 Python 解析
  - `pip.py`：pip 包查询/安装/更新
  - `net.py`：pip.ini 代理写入等
  - `common.py`：run_hidden、Git 检测、单实例锁
  - `logging.py`：统一日志安装

- `config/manager.py`：配置的加载/保存/默认值维护

## 行为兼容性

- 入口文件未改名，原有调用方式保持不变。
- 日志、路径解析、pip 代理等行为与原实现一致；仅导入路径发生变化。