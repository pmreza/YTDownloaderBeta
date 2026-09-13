import os
import webview
import tkinter.filedialog as filedialog
import tkinter as tk

from src.core.downloader import YoutubeDownloader
from src.core.deps_manager import DependencyManager

class WebViewLogger:
    def __init__(self, window):
        self.window = window

    def log(self, message: str):
        if self.window:
            safe_msg = message.replace('"', '\\"').replace('\n', '\\n')
            self.window.evaluate_js(f'if(window.logMessage) window.logMessage("{safe_msg}");')

    def handle_error(self, e, context=""):
        self.log(f"ERROR ({context}): {str(e)}")

class Api:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.bin_path = os.path.join(self.base_path, "bin")
        self.save_dir = os.path.join(os.path.expanduser("~"), "Desktop", "Infinite_Downloads")
        
        self.window = None
        self.app_logger = None
        self.downloader = None
        self.deps_manager = DependencyManager(self.bin_path, logger=None)

    def set_window(self, window):
        self.window = window
        self.app_logger = WebViewLogger(self.window)
        
        self.downloader = YoutubeDownloader(self.bin_path, self.save_dir, logger=self.app_logger)
        self.downloader.on_queue_update = self.on_queue_update
        self.downloader.on_progress = self.on_progress
        self.downloader.on_finish_all = self.on_finish_all
        
        self.deps_manager.logger = self.app_logger

    def run_startup_checks(self):
        self.deps_manager.verify_and_download()
        self.deps_manager.update_apps_if_needed()

    def select_folder(self):
        root = tk.Tk()
        root.withdraw()
        d = filedialog.askdirectory()
        root.destroy()
        if d:
            self.save_dir = d
            if self.downloader:
                self.downloader.save_dir = d
            return os.path.basename(d)
        return None

    def add_to_queue(self, urls_text: str, quality: str, is_playlist: bool):
        urls = urls_text.split('\n')
        added = self.downloader.add_urls(urls)
        
        if added > 0 and not self.downloader.is_downloading:
            self.downloader.start_worker(quality, is_playlist)
            
    def stop_download(self):
        if self.downloader:
            self.downloader.stop()

    def on_queue_update(self, qsize: int):
        if self.window:
            self.window.evaluate_js(f'if(window.updateQueueStatus) window.updateQueueStatus({qsize});')

    def on_progress(self, percent: float):
        if self.window:
            self.window.evaluate_js(f'if(window.updateProgress) window.updateProgress({percent});')

    def on_finish_all(self):
        if self.window:
            self.window.evaluate_js('if(window.updateQueueStatus) window.updateQueueStatus(0);')

class InfiniteDownload:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.api = Api(base_path)

    def run_startup_checks(self):
        import threading
        threading.Thread(target=self.api.run_startup_checks, daemon=True).start()

    def mainloop(self):
        html_path = os.path.join(self.base_path, "src", "ui", "index.html")
        window = webview.create_window('COSMIC DOWNLOADER', url=f'file:///{html_path.replace(os.sep, "/")}',
                                       js_api=self.api, width=1000, height=750, 
                                       frameless=False, easy_drag=False, background_color='#0B0F19')
        self.api.set_window(window)
        webview.start()
