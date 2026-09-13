import os
import webview
import tkinter.filedialog as filedialog
import tkinter as tk

from src.core.downloader import YoutubeDownloader
from src.core.deps_manager import DependencyManager

class WebViewLogger:
    def __init__(self, api):
        self._api = api

    def log(self, message: str):
        if self._api:
            self._api._log_queue.append(message)

    def handle_error(self, e, context=""):
        self.log(f"ERROR ({context}): {str(e)}")

class Api:
    def __init__(self, base_path: str, exe_dir: str):
        self._base_path = base_path
        
        # Use AppData to hide the bin folder from the user's desktop
        app_data_dir = os.path.join(os.getenv("APPDATA", os.path.expanduser("~")), "InfiniteDownloader")
        if not os.path.exists(app_data_dir):
            os.makedirs(app_data_dir, exist_ok=True)
            
        self._bin_path = os.path.join(app_data_dir, "bin")
        self._save_dir = os.path.join(os.path.expanduser("~"), "Desktop", "Infinite_Downloads")
        
        self._window = None
        self._app_logger = WebViewLogger(self)
        self._downloader = None
        self._deps_manager = DependencyManager(self._bin_path, logger=None)
        
        self._log_queue = []
        self._qsize = -1
        self._progress = -1
        self._hide_loading = False

    def get_state(self):
        logs = self._log_queue.copy()
        self._log_queue.clear()
        
        state = {
            "logs": logs,
            "qsize": self._qsize,
            "progress": self._progress,
            "hide_loading": self._hide_loading
        }
        
        self._qsize = -1
        self._progress = -1
        self._hide_loading = False
        
        return state

    def set_window(self, window):
        self._window = window
        
        self._downloader = YoutubeDownloader(self._bin_path, self._save_dir, logger=self._app_logger)
        self._downloader.on_queue_update = self.on_queue_update
        self._downloader.on_progress = self.on_progress
        self._downloader.on_finish_all = self.on_finish_all
        
        self._deps_manager.logger = self._app_logger

    def run_startup_checks(self):
        self._deps_manager.verify_and_download()
        self._deps_manager.update_apps_if_needed()
        self._hide_loading = True
        
    def start_dependencies(self):
        import threading
        threading.Thread(target=self.run_startup_checks, daemon=True).start()

    def select_folder(self):
        root = tk.Tk()
        root.withdraw()
        d = filedialog.askdirectory()
        root.destroy()
        if d:
            self._save_dir = d
            if self._downloader:
                self._downloader.save_dir = d
            return os.path.basename(d)
        return None

    def add_to_queue(self, urls_text: str, quality: str, is_playlist: bool):
        urls = urls_text.split('\n')
        added = self._downloader.add_urls(urls)
        
        if added > 0 and not self._downloader.is_downloading:
            self._downloader.start_worker(quality, is_playlist)
            
    def stop_download(self):
        if self._downloader:
            self._downloader.stop()
            
    def cancel_current_download(self):
        if self._downloader:
            self._downloader.cancel_current()

    def open_save_folder(self):
        import platform
        import subprocess
        
        if not os.path.exists(self._save_dir):
            os.makedirs(self._save_dir, exist_ok=True)
            
        if platform.system() == "Windows":
            os.startfile(self._save_dir)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", self._save_dir])
        else:
            subprocess.Popen(["xdg-open", self._save_dir])

    def on_queue_update(self, qsize: int):
        self._qsize = qsize

    def on_progress(self, percent: float):
        self._progress = percent

    def on_finish_all(self):
        self._qsize = 0

class InfiniteDownload:
    def __init__(self, base_path: str, exe_dir: str):
        self.base_path = base_path
        self.api = Api(base_path, exe_dir)

    def mainloop(self):
        html_path = os.path.join(self.base_path, "src", "ui", "index.html")
        window = webview.create_window('INFINITE DOWNLOADER', url=f'file:///{html_path.replace(os.sep, "/")}',
                                       js_api=self.api, width=1000, height=750, 
                                       frameless=False, easy_drag=False, background_color='#0B0F19')
        self.api.set_window(window)
        webview.start()
