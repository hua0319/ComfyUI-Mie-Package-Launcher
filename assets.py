from pathlib import Path
import sys
import os


def resolve_asset(filename: str) -> Path:
    """在多种运行环境中解析资源路径（PyInstaller/源码/当前目录）。"""
    candidates = []
    try:
        # 1) 运行时临时目录（PyInstaller）
        candidates.append(Path(getattr(sys, '_MEIPASS', '')) / 'assets' / filename)
    except Exception:
        pass
    try:
        # 2) 源码所在的 launcher 目录
        candidates.append(Path(__file__).resolve().parent / 'assets' / filename)
    except Exception:
        pass
    try:
        # 3) 项目根目录下的 launcher 目录
        candidates.append(Path('launcher').resolve() / 'assets' / filename)
    except Exception:
        pass
    try:
        # 4) 可执行文件所在目录（打包场景）
        candidates.append(Path(sys.executable).resolve().parent / 'assets' / filename)
    except Exception:
        pass
    try:
        # 5) 当前工作目录下的 launcher 目录
        candidates.append(Path.cwd() / 'launcher' / 'assets' / filename)
    except Exception:
        pass
    for p in candidates:
        try:
            if p.exists():
                return p
        except Exception:
            pass
    return candidates[0] if candidates else Path(filename)


def resolve_asset_variants(filenames):
    """按顺序尝试多个文件名变体，返回第一个存在的路径。"""
    for name in filenames:
        try:
            p = resolve_asset(name)
            try:
                if p.exists():
                    return p
            except Exception:
                pass
        except Exception:
            pass
    # 兜底返回第一个的解析结果
    try:
        return resolve_asset(filenames[0])
    except Exception:
        return Path(filenames[0])


# ---------------- 图标解析辅助 ----------------
def icon_base_paths():
    """收集用于查找图标的基础目录列表。"""
    bases = []
    try:
        bases.append(Path(getattr(sys, '_MEIPASS', '')))
    except Exception:
        pass
    try:
        bases.append(Path(__file__).resolve().parent)
    except Exception:
        pass
    try:
        bases.append(Path('launcher').resolve())
    except Exception:
        pass
    try:
        bases.append(Path(sys.executable).resolve().parent)
    except Exception:
        pass
    # 仅返回存在的路径
    present = []
    for b in bases:
        try:
            if b and b.exists():
                present.append(b)
        except Exception:
            pass
    return present


def icon_candidates(filename: str):
    """基于基础目录生成图标候选路径列表。"""
    return [b / 'assets' / filename for b in icon_base_paths()]


def icon_candidates_ico():
    return icon_candidates('rabbit.ico')


def icon_candidates_png():
    return icon_candidates('rabbit.png')


def skip_icons() -> bool:
    """检查是否跳过窗口图标设置。"""
    try:
        env = (os.environ.get('COMFYUI_LAUNCHER_SKIP_ICONS') or '').strip().lower() in ('1', 'true', 'yes', 'on')
    except Exception:
        env = False
    file_flag = False
    try:
        file_flag = (Path.cwd() / 'launcher' / 'skip_icons').exists()
    except Exception:
        file_flag = False
    return bool(env or file_flag)


def enable_ico() -> bool:
    """检查是否启用 .ico 的 iconbitmap 设置。"""
    try:
        env = (os.environ.get('COMFYUI_LAUNCHER_ENABLE_ICO') or '').strip().lower() in ('1', 'true', 'yes', 'on')
    except Exception:
        env = False
    file_flag = False
    try:
        file_flag = (Path.cwd() / 'launcher' / 'enable_ico').exists()
    except Exception:
        file_flag = False
    return bool(env or file_flag)