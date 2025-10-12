from pathlib import Path


def get_comfy_root(paths_cfg: dict) -> Path:
    """Resolve ComfyUI root from config paths.
    Fallback to 'ComfyUI' relative directory if missing.
    """
    try:
        raw = (paths_cfg or {}).get("comfyui_path", "ComfyUI")
    except Exception:
        raw = "ComfyUI"
    p = Path(raw)
    try:
        return p.resolve()
    except Exception:
        return p


def logs_file(comfy_root: Path) -> Path:
    return comfy_root / "user" / "comfyui.log"


def input_dir(comfy_root: Path) -> Path:
    return comfy_root / "input"


def output_dir(comfy_root: Path) -> Path:
    return comfy_root / "output"


def plugins_dir(comfy_root: Path) -> Path:
    return comfy_root / "custom_nodes"


def workflows_dir(comfy_root: Path) -> Path:
    return comfy_root / "user" / "default" / "workflows"