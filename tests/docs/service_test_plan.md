# Service 测试用例设计

## 设计原则
- 全部用例基于真实环境，不做回退或模拟；网络/外部依赖不可用时明确失败或跳过。
- 每个接口包含至少 3 个正例与 3 个反例，覆盖标准、边界与异常依赖状态。

## ProcessService
- 正例：
  1. 启动成功：在端口空闲时 `start()` 使服务可达并按钮置为运行态
  2. 停止成功：运行中调用 `stop()` 服务不可达
  3. 刷新状态：`refresh_status()` 在运行/停止两态下按钮正确切换
- 反例：
  1. Python 缺失：`python_path` 指向不存在，`start()` 记录错误
  2. 主文件缺失：`main.py` 不存在，`start()` 记录错误
  3. 端口被占用：启动前端口占用，触发端口占用分支（真实环境下可跳过）
- 性能临界：
  - 启动监测窗口 30 秒内应可达；停止监测窗口 15 秒内应不可达
- 边界值：
  - 端口取默认 `8188` 与自定义非常规端口（如 `65530`）

## VersionService
- 正例：
  1. 当前版本获取：返回 `tag` 与 `commit`
  2. 稳定版本判断：符合语义规则的 tag 返回 `True`
  3. 最新稳定版本获取：存在 Releases 时返回含 `tag/commit` 的数据
- 反例：
  1. 仓库无远程：`_origin_repo` 不存在，`get_latest_stable_kernel` 返回空列表
  2. 网络不可用：Releases 拉取失败，返回空
  3. 非稳定提交升级：`upgrade_to_commit` 对非稳定返回错误码
- 性能临界：
  - `git` 命令 10-15 秒超时；API 拉取 10 秒超时
- 边界值：
  - tag 前缀含 `v`、包含 `-rc/-beta/-alpha` 等

## UpdateService
- 正例：
  1. 前端更新：返回 `component=frontend` 与版本字段
  2. 模板更新：返回 `component=templates` 与版本字段
  3. 批量摘要：组合多组件的更新结果，摘要包含中文文案
- 反例：
  1. PyPI 不可达：安装返回错误，结果含 `error`
  2. 代理配置无效：自定义 URL 空或非法，使用默认索引
  3. 前端/模板未安装：版本查询返回 `None`
- 性能临界：
  - 安装/更新超时路径（真实环境下仅校验结构与返回）
- 边界值：
  - 代理模式切换（aliyun/custom/none）与 URL 尾部斜杠

## ConfigService
- 正例：
  1. 加载现有配置：包含 `paths` 键
  2. 写入 `comfyui_root` 并保存：再次读取一致
  3. 更新启动与代理设置：`get` 返回更新值
- 反例：
  1. 写入非法路径：保存后读取仍为字符串但后续校验失败
  2. 设置缺失键：`get` 返回默认值
  3. 保存时写入失败：记录错误（需文件锁定场景）

## GitService
- 正例：
  1. 解析系统 Git：返回 `git` 与来源文案
  2. 写入 Manager INI：存在 `git_exe = ...`
  3. 重复写入：不重复添加键
- 反例：
  1. Git 不可用：解析返回 `None`
  2. ComfyUI 路径不存在：`apply_to_manager` 直接返回
  3. INI 路径不可写：记录错误

## NetworkService
- 正例：
  1. 应用代理设置：生成或更新 `pip.ini`
  2. 模式 aliyun：使用镜像 URL
  3. 模式 custom：使用自定义 URL
- 反例：
  1. 自定义 URL 为空：不应用
  2. `python_exec` 无效：处理异常
  3. 文件系统不可写：记录错误

## RuntimeService
- 正例：
  1. 创建模板目录：存在 `.../site-packages/comfyui_workflow_templates/templates`
  2. exe 与非 exe 两种环境路径解析
  3. 幂等执行：目录已存在不报错
- 反例：
  1. `python_exec` 未解析：跳过创建
  2. site-packages 不存在：返回
  3. 文件系统不可写：记录错误