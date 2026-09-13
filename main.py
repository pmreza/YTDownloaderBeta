import os
import sys
import subprocess

# --- ۱. بخش نصب خودکار کتابخانه‌ها ---
def install_dependencies():
    required_libs = {"customtkinter": "customtkinter", "Pillow": "PIL"}
    for lib_name, import_name in required_libs.items():
        try:
            __import__(import_name)
        except ImportError:
            print(f"--- Library '{lib_name}' not found. Installing now... ---")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib_name])
                print(f"--- {lib_name} installed successfully. ---")
            except Exception as e:
                print(f"--- Failed to install {lib_name}: {e} ---")

install_dependencies()

# --- ۲. وارد کردن کتابخانه‌های اصلی ---
import customtkinter as ctk
import threading
import queue
import re
import urllib.request
from tkinter import messagebox, filedialog
from PIL import Image

# --- 🎨 پالت ۳۰ تم کامل ---
COLOR_THEMES = {
    "Infinite Midnight": {"mode": "Dark", "bg": "#0B0F19", "frame": "#161D2F", "accent": "#38BDF8"},
    "YouTube Pro": {"mode": "Dark", "bg": "#0F0F0F", "frame": "#212121", "accent": "#FF0000"},
    "Deep Space": {"mode": "Dark", "bg": "#1A1A2E", "frame": "#16213E", "accent": "#E94560"},
    "Dracula": {"mode": "Dark", "bg": "#282A36", "frame": "#44475A", "accent": "#BD93F9"},
    "Nordic": {"mode": "Dark", "bg": "#2E3440", "frame": "#3B4252", "accent": "#88C0D0"},
    "Cyberpunk": {"mode": "Dark", "bg": "#000000", "frame": "#1A1A1A", "accent": "#FCEE09"},
    "Ocean Blue": {"mode": "Dark", "bg": "#0D1117", "frame": "#161B22", "accent": "#58A6FF"},
    "Forest Green": {"mode": "Dark", "bg": "#141E14", "frame": "#1E2E1E", "accent": "#4ADE80"},
    "Tokyo Night": {"mode": "Dark", "bg": "#1A1B26", "frame": "#24283B", "accent": "#7AA2F7"},
    "Material Dark": {"mode": "Dark", "bg": "#212121", "frame": "#303030", "accent": "#00E5FF"},
    "Vampire": {"mode": "Dark", "bg": "#100000", "frame": "#200000", "accent": "#FF0000"},
    "Obsidian": {"mode": "Dark", "bg": "#000000", "frame": "#111111", "accent": "#FFFFFF"},
    "Neon Purple": {"mode": "Dark", "bg": "#0D0221", "frame": "#240B36", "accent": "#AF52BF"},
    "Gold & Black": {"mode": "Dark", "bg": "#121212", "frame": "#1E1E1E", "accent": "#D4AF37"},
    "Slate Night": {"mode": "Dark", "bg": "#0F172A", "frame": "#1E293B", "accent": "#94A3B8"},
    "Matrix": {"mode": "Dark", "bg": "#000000", "frame": "#0D0D0D", "accent": "#00FF41"},
    "Sunset Neon": {"mode": "Dark", "bg": "#2D1B2E", "frame": "#412B42", "accent": "#FF7E5F"},
    "Electric": {"mode": "Dark", "bg": "#120129", "frame": "#21034D", "accent": "#BC13FE"},
    "Flamingo": {"mode": "Dark", "bg": "#2F1B25", "frame": "#4B2C3A", "accent": "#F687B3"},
    "Aurora": {"mode": "Dark", "bg": "#111827", "frame": "#1F2937", "accent": "#10B981"},
    "Clean Blue": {"mode": "Light", "bg": "#F8FAFC", "frame": "#FFFFFF", "accent": "#2563EB"},
    "Soft Peach": {"mode": "Light", "bg": "#FFF5F5", "frame": "#FFFFFF", "accent": "#F87171"},
    "Apple White": {"mode": "Light", "bg": "#F5F5F7", "frame": "#FFFFFF", "accent": "#000000"},
    "Mint Fresh": {"mode": "Light", "bg": "#F0FFF4", "frame": "#FFFFFF", "accent": "#10B981"},
    "Lavender": {"mode": "Light", "bg": "#F5F3FF", "frame": "#FFFFFF", "accent": "#8B5CF6"},
    "Sunny Day": {"mode": "Light", "bg": "#FFFBEB", "frame": "#FFFFFF", "accent": "#F59E0B"},
    "Milk Coffee": {"mode": "Light", "bg": "#FAF7F2", "frame": "#FFFFFF", "accent": "#8B4513"},
    "Minimalist": {"mode": "Light", "bg": "#FFFFFF", "frame": "#F2F2F2", "accent": "#333333"},
    "Rose Light": {"mode": "Light", "bg": "#FFF1F2", "frame": "#FFFFFF", "accent": "#FB7185"},
    "Sky Bright": {"mode": "Light", "bg": "#F0F9FF", "frame": "#FFFFFF", "accent": "#0EA5E9"},
}

LANGUAGES = {
    "English": {
        "title": "INFINITE DOWNLOAD", "url_lbl": "Enter URLs (One per line):", "save_btn": "📂 Choose Save Path",
        "start_btn": "ADD TO QUEUE & START", "stop_btn": "STOP & CLEAR QUEUE", "single": "Single Video", "playlist": "Playlist",
        "prog_v": "Video Progress:", "prog_l": "Playlist Status:", "log_done": "Done", "sett_t": "Settings",
        "theme_lbl": "🌓 Appearance", "lang_lbl": "🌐 Language", "success": "All queued downloads finished!",
        "queue_lbl": "Items in queue:"
    },
    "فارسی": {
        "title": "اینفینیت دانلود", "url_lbl": "لینک‌ها را وارد کنید (هر خط یک لینک):", "save_btn": "📂 انتخاب محل ذخیره",
        "start_btn": "افزودن به صف و شروع", "stop_btn": "توقف و حذف صف", "single": "تک ویدیو", "playlist": "لیست پخش",
        "prog_v": "پیشرفت ویدیو:", "prog_l": "وضعیت لیست:", "log_done": "انجام شد", "sett_t": "تنظیمات",
        "theme_lbl": "🌓 ظاهر برنامه", "lang_lbl": "🌐 زبان برنامه", "success": "تمامی دانلودهای صف با موفقیت تمام شد!",
        "queue_lbl": "تعداد در صف:"
    }
}

class InfiniteDownload(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.geometry("1000x980")
        self.title("Infinite Download Pro")

        # --- تنظیمات مسیرها ---
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.bin_path = os.path.join(self.base_path, "bin")
        if not os.path.exists(self.bin_path): os.makedirs(self.bin_path)

        self.yt_dlp = os.path.join(self.bin_path, "yt-dlp.exe")
        self.icon_path = os.path.join(self.base_path, "logo.ico")
        self.save_dir = os.path.join(os.path.expanduser("~"), "Desktop", "Infinite_Downloads")
        
        if not os.path.exists(self.save_dir): os.makedirs(self.save_dir)
        
        self.check_yt_dlp()
        threading.Thread(target=self.update_bin_apps, daemon=True).start()

        try:
            if os.path.exists(self.icon_path):
                self.iconbitmap(self.icon_path)
        except: pass

        self.current_lang = "فارسی"
        self.menu_visible = False
        
        # --- متغیرهای مربوط به صف ---
        self.download_process = None
        self.dl_queue = queue.Queue()
        self.is_downloading = False

        # --- 🏗️ رابط کاربری (UI) ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(expand=True, fill="both", padx=25, pady=(40, 10))
        
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.header_frame.pack(pady=(10, 10))

        try:
            logo_img = ctk.CTkImage(light_image=Image.open(self.icon_path), 
                                  dark_image=Image.open(self.icon_path), 
                                  size=(60, 60))
            self.logo_label = ctk.CTkLabel(self.header_frame, image=logo_img, text="")
            self.logo_label.pack(side="left", padx=15)
        except: pass

        self.lbl_title = ctk.CTkLabel(self.header_frame, text="INFINITE DOWNLOAD", font=("Impact", 55))
        self.lbl_title.pack(side="left")

        # لیبل و باکس دریافت لینک (چند خطی)
        self.lbl_url_instruction = ctk.CTkLabel(self.main_container, text="لینک‌ها را وارد کنید (هر خط یک لینک):", font=("Segoe UI", 14, "bold"))
        self.lbl_url_instruction.pack(anchor="w", padx=65, pady=(10, 0))
        
        self.url_box = ctk.CTkTextbox(self.main_container, height=100, font=("Segoe UI", 14), border_width=2)
        self.url_box.pack(fill="x", padx=60, pady=(5, 10))

        self.row1 = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.row1.pack(fill="x", padx=60)
        self.quality_var = ctk.StringVar(value="720p")
        self.combo_quality = ctk.CTkComboBox(self.row1, values=["2160p", "1080p", "720p", "480p"], variable=self.quality_var, width=120)
        self.combo_quality.pack(side="left", padx=5)
        self.btn_folder = ctk.CTkButton(self.row1, command=self.select_folder, height=45, font=("Segoe UI", 13, "bold"))
        self.btn_folder.pack(side="right", expand=True, fill="x", padx=5)

        self.mode_frame = ctk.CTkFrame(self.main_container, corner_radius=15)
        self.mode_frame.pack(fill="x", padx=60, pady=15)
        self.mode_var = ctk.IntVar(value=1)
        self.radio_single = ctk.CTkRadioButton(self.mode_frame, variable=self.mode_var, value=1, font=("Segoe UI", 14, "bold"))
        self.radio_single.pack(side="left", padx=40, pady=20)
        self.radio_playlist = ctk.CTkRadioButton(self.mode_frame, variable=self.mode_var, value=2, font=("Segoe UI", 14, "bold"))
        self.radio_playlist.pack(side="left", padx=10, pady=20)

        # دکمه شروع و توقف صف
        self.btn_start = ctk.CTkButton(self.main_container, command=self.add_to_queue, height=65, font=("Segoe UI", 20, "bold"))
        self.btn_start.pack(fill="x", padx=60, pady=10)
        
        self.queue_status_lbl = ctk.CTkLabel(self.main_container, text="تعداد در صف: 0", font=("Segoe UI", 14, "bold"), text_color="#F59E0B")
        self.queue_status_lbl.pack(pady=(0, 5))

        self.btn_stop = ctk.CTkButton(self.main_container, command=self.stop_download, height=40, fg_color="#ef4444", text="STOP & CLEAR QUEUE")
        self.btn_stop.pack(pady=5)

        self.log_box = ctk.CTkTextbox(self.main_container, height=140, font=("Consolas", 13), border_width=2, corner_radius=15)
        self.log_box.pack(fill="x", padx=60, pady=10)

        self.prog_label_curr = ctk.CTkLabel(self.main_container, font=("Segoe UI", 13, "bold"))
        self.prog_label_curr.pack(anchor="w", padx=65)
        self.prog_bar_curr = ctk.CTkProgressBar(self.main_container, height=15)
        self.prog_bar_curr.pack(fill="x", padx=60, pady=(2, 10))
        self.prog_bar_curr.set(0)

        self.prog_label_total = ctk.CTkLabel(self.main_container, font=("Segoe UI", 12))
        self.prog_label_total.pack(anchor="w", padx=65)
        self.prog_bar_total = ctk.CTkProgressBar(self.main_container, height=10)
        self.prog_bar_total.pack(fill="x", padx=60, pady=(2, 20))
        self.prog_bar_total.set(0)

        # --- ⚙️ منوی تنظیمات ---
        self.overlay_menu = ctk.CTkFrame(self, height=180, corner_radius=30, border_width=2)
        self.sett_container = ctk.CTkFrame(self.overlay_menu, fg_color="transparent")
        self.sett_container.pack(expand=True, fill="both", padx=20, pady=10)

        self.f_theme = ctk.CTkFrame(self.sett_container, fg_color="transparent")
        self.f_theme.pack(side="left", expand=True)
        self.lbl_sett_theme = ctk.CTkLabel(self.f_theme, text="", font=("Segoe UI", 12, "bold"))
        self.lbl_sett_theme.pack(pady=5)
        self.opt_theme = ctk.CTkOptionMenu(self.f_theme, values=list(COLOR_THEMES.keys()), command=self.apply_theme, width=150)
        self.opt_theme.pack()

        self.f_lang = ctk.CTkFrame(self.sett_container, fg_color="transparent")
        self.f_lang.pack(side="left", expand=True)
        self.lbl_sett_lang = ctk.CTkLabel(self.f_lang, text="", font=("Segoe UI", 12, "bold"))
        self.lbl_sett_lang.pack(pady=5)
        self.opt_lang = ctk.CTkOptionMenu(self.f_lang, values=["فارسی", "English"], command=self.change_lang, width=130)
        self.opt_lang.pack()

        self.f_credit = ctk.CTkFrame(self.sett_container, fg_color="transparent")
        self.f_credit.pack(side="left", expand=True)
        ctk.CTkLabel(self.f_credit, text="👨‍💻 Creator", font=("Segoe UI", 12, "bold")).pack(pady=5)
        ctk.CTkLabel(self.f_credit, text="pmreza", font=("Segoe UI", 18, "bold"), text_color="#38BDF8").pack()

        self.btn_menu = ctk.CTkButton(self, text="⚙", width=50, height=50, font=("Arial", 25), command=self.toggle_menu, fg_color="transparent", hover_color="gray30")
        self.btn_menu.place(relx=0.98, rely=0.02, anchor="ne")

        self.change_lang("فارسی")
        self.apply_theme("Infinite Midnight")

    # --- 🛠️ توابع عملیاتی ---
    def check_yt_dlp(self):
        if not os.path.exists(self.yt_dlp):
            print("--- yt-dlp.exe missing. Downloading... ---")
            try:
                url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
                urllib.request.urlretrieve(url, self.yt_dlp)
            except Exception as e:
                print(f"Error downloading yt-dlp: {e}")

    def update_bin_apps(self):
        update_flag = os.path.join(self.bin_path, "last_update.txt")
        import time
        current_time = time.time()
        
        if os.path.exists(update_flag):
            try:
                with open(update_flag, "r") as f:
                    last_update = float(f.read().strip())
                    if current_time - last_update < 86400:
                        print("--- Bin apps are up to date (checked recently) ---")
                        return
            except:
                pass

        print("--- Checking for updates for bin apps ---")
        self.after(0, lambda: self.btn_start.configure(state="disabled", text="UPDATING COMPONENTS..."))
        
        if os.path.exists(self.yt_dlp):
            try:
                print("Updating yt-dlp...")
                subprocess.run([self.yt_dlp, "-U"], check=False, creationflags=0x08000000)
            except Exception as e:
                print(f"Error updating yt-dlp: {e}")
                
        deno_path = os.path.join(self.bin_path, "deno.exe")
        if os.path.exists(deno_path):
            try:
                print("Updating deno...")
                subprocess.run([deno_path, "upgrade"], check=False, creationflags=0x08000000)
            except Exception as e:
                print(f"Error updating deno: {e}")
                
        try:
            with open(update_flag, "w") as f:
                f.write(str(current_time))
        except:
            pass

        ln = LANGUAGES[self.current_lang]
        self.after(0, lambda: self.btn_start.configure(state="normal", text=ln["start_btn"]))

    def toggle_menu(self):
        if not self.menu_visible:
            self.overlay_menu.place(relx=0.5, y=100, anchor="n", relwidth=0.85)
            self.btn_menu.configure(text="✕")
            self.menu_visible = True
        else:
            self.overlay_menu.place_forget()
            self.btn_menu.configure(text="⚙")
            self.menu_visible = False

    def change_lang(self, choice):
        self.current_lang = choice
        ln = LANGUAGES[choice]
        self.lbl_url_instruction.configure(text=ln["url_lbl"])
        self.btn_folder.configure(text=ln["save_btn"])
        self.radio_single.configure(text=ln["single"])
        self.radio_playlist.configure(text=ln["playlist"])
        self.btn_start.configure(text=ln["start_btn"])
        self.btn_stop.configure(text=ln["stop_btn"])
        self.prog_label_curr.configure(text=f"{ln['prog_v']} 0%")
        self.prog_label_total.configure(text=f"{ln['prog_l']} 0/0")
        self.lbl_sett_theme.configure(text=ln["theme_lbl"])
        self.lbl_sett_lang.configure(text=ln["lang_lbl"])
        self.update_queue_ui()

    def apply_theme(self, theme_name):
        c = COLOR_THEMES.get(theme_name, COLOR_THEMES["Infinite Midnight"])
        ctk.set_appearance_mode(c["mode"])
        self.configure(fg_color=c["bg"])
        self.overlay_menu.configure(fg_color=c["frame"], border_color=c["accent"])
        self.lbl_title.configure(text_color=c["accent"])
        self.btn_start.configure(fg_color=c["accent"], hover_color=c["accent"])
        self.prog_bar_curr.configure(progress_color=c["accent"])
        self.btn_folder.configure(fg_color=c["frame"], border_color=c["accent"], border_width=1, text_color=c["accent"])
        self.radio_single.configure(fg_color=c["accent"])
        self.radio_playlist.configure(fg_color=c["accent"])
        self.url_box.configure(border_color=c["accent"])
        self.log_box.configure(border_color=c["accent"])

    def select_folder(self):
        d = filedialog.askdirectory()
        if d: 
            self.save_dir = d
            self.btn_folder.configure(text=f"📂 {os.path.basename(d)}")

    def update_queue_ui(self):
        ln = LANGUAGES[self.current_lang]
        self.queue_status_lbl.configure(text=f"{ln['queue_lbl']} {self.dl_queue.qsize()}")

    def stop_download(self):
        # 1. خالی کردن صف
        with self.dl_queue.mutex:
            self.dl_queue.queue.clear()
        self.update_queue_ui()
        
        # 2. متوقف کردن پردازش فعلی
        if self.download_process:
            try:
                subprocess.run(f"taskkill /F /T /PID {self.download_process.pid}", shell=True)
            except:
                pass
        
        self.is_downloading = False
        self.btn_start.configure(state="normal")
        self.log_box.insert("end", "\n--- All downloads STOPPED and queue CLEARED ---\n")
        self.log_box.see("end")

    def add_to_queue(self):
        # دریافت تمام لینک‌ها از تکست‌باکس و جداسازی با خط جدید
        raw_text = self.url_box.get("1.0", "end").strip()
        if not raw_text: 
            return
            
        urls = raw_text.split('\n')
        
        # اضافه کردن لینک‌های معتبر به صف
        added_count = 0
        for url in urls:
            url = url.strip()
            if url:
                self.dl_queue.put(url)
                added_count += 1
                
        if added_count > 0:
            self.url_box.delete("1.0", "end") # پاک کردن کادر بعد از اضافه شدن به صف
            self.update_queue_ui()
            self.log_box.insert("end", f"\n--- {added_count} URL(s) added to queue ---\n")
            self.log_box.see("end")
            
            # اگر वर्کر در حال اجرا نیست، روشنش کن
            if not self.is_downloading:
                self.btn_start.configure(state="disabled")
                threading.Thread(target=self.queue_worker, daemon=True).start()

    def queue_worker(self):
        self.is_downloading = True
        ln = LANGUAGES[self.current_lang]
        
        while not self.dl_queue.empty():
            current_url = self.dl_queue.get()
            self.update_queue_ui()
            
            self.log_box.insert("end", f"\n>>> Starting Download: {current_url}\n")
            self.log_box.see("end")
            
            # اجرای دانلود برای لینک فعلی
            self.run_process(current_url)
            
            self.dl_queue.task_done()
            
        # وقتی صف خالی شد
        self.is_downloading = False
        self.btn_start.configure(state="normal")
        messagebox.showinfo("Infinite", ln["success"])

    def run_process(self, url):
        q = self.quality_var.get().replace("p", "")
        mode = "--yes-playlist" if self.mode_var.get() == 2 else "--no-playlist"
        ln = LANGUAGES[self.current_lang]
        
        ffmpeg_exe = os.path.join(self.bin_path, "ffmpeg.exe")
        format_str = f"bestvideo[height<={q}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={q}]+bestaudio/best[height<={q}]"
        
        cmd = [self.yt_dlp, url, mode, "--output", os.path.join(self.save_dir, "%(title)s.%(ext)s"),
               "--ffmpeg-location", ffmpeg_exe, "--newline", "--progress", "--continue",
               "-f", format_str, "--merge-output-format", "mp4"]
        
        env = os.environ.copy()
        env["PATH"] = self.bin_path + os.pathsep + env.get("PATH", "")
        
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, 
                                 encoding='utf-8', errors='replace', startupinfo=subprocess.STARTUPINFO(dwFlags=subprocess.STARTF_USESHOWWINDOW),
                                 env=env)
            self.download_process = p
            for line in p.stdout:
                self.log_box.insert("end", line)
                self.log_box.see("end")
                if "[download]" in line and "%" in line:
                    m = re.search(r"(\d+\.\d+)%", line)
                    if m:
                        val = float(m.group(1)) / 100
                        self.prog_bar_curr.set(val)
                        self.prog_label_curr.configure(text=f"{ln['prog_v']} {m.group(1)}%")
            p.wait()
        except Exception as e: 
            self.log_box.insert("end", f"Error: {str(e)}\n")

if __name__ == "__main__":
    app = InfiniteDownload()
    app.mainloop()