import threading

def monitor(app, process_manager):
    while True:
        try:
            if getattr(app, "_shutting_down", False):
                break
            if process_manager.comfyui_process and process_manager.comfyui_process.poll() is not None:
                process_manager.comfyui_process = None
            process_manager.refresh_running_status_async()
            threading.Event().wait(2)
        except Exception:
            break