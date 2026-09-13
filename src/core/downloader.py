import os
import re
import queue
import threading
import subprocess

class YoutubeDownloader:
    def __init__(self, bin_path: str, save_dir: str, logger=None):
        self.bin_path = bin_path
        self.save_dir = save_dir
        self.logger = logger
        
        self.yt_dlp = os.path.join(self.bin_path, "yt-dlp.exe")
        self.ffmpeg = os.path.join(self.bin_path, "ffmpeg.exe")
        
        self.dl_queue = queue.Queue()
        self.is_downloading = False
        self.download_process = None
        self.is_cancelled = False
        
        # Callbacks
        self.on_queue_update = None
        self.on_progress = None
        self.on_finish_all = None

    def log(self, message: str):
        if self.logger:
            self.logger.log(message)
        else:
            print(message)

    def add_urls(self, urls: list):
        added_count = 0
        for url in urls:
            url = url.strip()
            if url:
                self.dl_queue.put(url)
                added_count += 1
                
        if self.on_queue_update:
            self.on_queue_update(self.dl_queue.qsize())
            
        return added_count

    def start_worker(self, quality: str, is_playlist: bool):
        if not self.is_downloading:
            self.is_downloading = True
            threading.Thread(target=self._queue_worker, args=(quality, is_playlist), daemon=True).start()

    def _queue_worker(self, quality: str, is_playlist: bool):
        while not self.dl_queue.empty():
            current_url = self.dl_queue.get()
            
            if self.on_queue_update:
                self.on_queue_update(self.dl_queue.qsize())
            
            self.log(f"\n>>> Starting Download: {current_url}\n")
            
            self.is_cancelled = False
            self._run_process(current_url, quality, is_playlist)
            
            self.dl_queue.task_done()
            
        self.is_downloading = False
        if self.on_finish_all:
            self.on_finish_all()

    def _run_process(self, url: str, quality: str, is_playlist: bool):
        q = quality.replace("p", "")
        mode = "--yes-playlist" if is_playlist else "--no-playlist"
        
        format_str = f"bestvideo[height<={q}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={q}]+bestaudio/best[height<={q}]"
        
        cmd = [self.yt_dlp, url, mode, "--output", os.path.join(self.save_dir, "%(title)s.%(ext)s"),
               "--ffmpeg-location", self.ffmpeg, "--newline", "--progress", "--continue",
               "-f", format_str, "--merge-output-format", "mp4"]
        
        env = os.environ.copy()
        env["PATH"] = self.bin_path + os.pathsep + env.get("PATH", "")
        
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, 
                                 encoding='utf-8', errors='replace', startupinfo=subprocess.STARTUPINFO(dwFlags=subprocess.STARTF_USESHOWWINDOW),
                                 env=env)
            self.download_process = p
            for line in p.stdout:
                line_str = line.strip()
                if not line_str:
                    continue
                    
                self.log(line_str)
                
                if "[download]" in line_str and "%" in line_str:
                    m = re.search(r"(\d+\.\d+)%", line_str)
                    if m:
                        val = float(m.group(1))
                        if self.on_progress:
                            self.on_progress(val)
                            
            p.wait()
            if p.returncode != 0:
                if self.is_cancelled:
                    self.log("--- Download was paused/cancelled by user ---")
                else:
                    raise Exception(f"yt-dlp exited with code {p.returncode}. See log for details.")
                
        except Exception as e:
            if self.logger:
                self.logger.handle_error(e, context="YT-DLP Subprocess")
            else:
                self.log(f"Error: {str(e)}")

    def stop(self):
        with self.dl_queue.mutex:
            self.dl_queue.queue.clear()
            
        if self.on_queue_update:
            self.on_queue_update(0)
            
        self.cancel_current()
        self.is_downloading = False

    def cancel_current(self):
        self.is_cancelled = True
        if self.download_process:
            try:
                subprocess.run(f"taskkill /F /T /PID {self.download_process.pid}", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            except:
                pass
