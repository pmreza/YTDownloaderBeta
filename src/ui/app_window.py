import os
import customtkinter as ctk
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
from PIL import Image

from .themes import COLOR_THEMES
from .locales import LANGUAGES
from src.core.downloader import YoutubeDownloader
from src.utils.logger import AppLogger
from src.core.deps_manager import DependencyManager

class InfiniteDownload(ctk.CTk):
    def __init__(self, base_path: str):
        super().__init__()
        
        self.geometry("1000x980")
        self.title("Infinite Download Pro")

        self.base_path = base_path
        self.bin_path = os.path.join(self.base_path, "bin")
        self.save_dir = os.path.join(os.path.expanduser("~"), "Desktop", "Infinite_Downloads")
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            
        self.icon_path = os.path.join(self.base_path, "logo.ico")
        try:
            if os.path.exists(self.icon_path):
                self.iconbitmap(self.icon_path)
        except:
            pass
            
        # Variables
        self.current_lang = "فارسی"
        self.menu_visible = False
        self.mode_var = ctk.IntVar(value=1)
        self.quality_var = ctk.StringVar(value="720p")
        
        # Setup UI
        self._build_ui()
        
        # Setup Logger
        self.app_logger = AppLogger(log_box_widget=self.log_box)
        
        # Setup Downloader
        self.downloader = YoutubeDownloader(self.bin_path, self.save_dir, logger=self.app_logger)
        self.downloader.on_queue_update = self.update_queue_ui
        self.downloader.on_progress = self.update_progress
        self.downloader.on_finish_all = self.on_downloads_finished
        
        # Setup Deps Manager
        self.deps_manager = DependencyManager(self.bin_path, logger=self.app_logger)
        
        # Initialize
        self.change_lang("فارسی")
        self.apply_theme("Infinite Midnight")

    def _build_ui(self):
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

        self.lbl_url_instruction = ctk.CTkLabel(self.main_container, text="", font=("Segoe UI", 14, "bold"))
        self.lbl_url_instruction.pack(anchor="w", padx=65, pady=(10, 0))
        
        self.url_box = ctk.CTkTextbox(self.main_container, height=100, font=("Segoe UI", 14), border_width=2)
        self.url_box.pack(fill="x", padx=60, pady=(5, 10))

        self.row1 = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.row1.pack(fill="x", padx=60)
        self.combo_quality = ctk.CTkComboBox(self.row1, values=["2160p", "1080p", "720p", "480p"], variable=self.quality_var, width=120)
        self.combo_quality.pack(side="left", padx=5)
        self.btn_folder = ctk.CTkButton(self.row1, command=self.select_folder, height=45, font=("Segoe UI", 13, "bold"))
        self.btn_folder.pack(side="right", expand=True, fill="x", padx=5)

        self.mode_frame = ctk.CTkFrame(self.main_container, corner_radius=15)
        self.mode_frame.pack(fill="x", padx=60, pady=15)
        self.radio_single = ctk.CTkRadioButton(self.mode_frame, variable=self.mode_var, value=1, font=("Segoe UI", 14, "bold"))
        self.radio_single.pack(side="left", padx=40, pady=20)
        self.radio_playlist = ctk.CTkRadioButton(self.mode_frame, variable=self.mode_var, value=2, font=("Segoe UI", 14, "bold"))
        self.radio_playlist.pack(side="left", padx=10, pady=20)

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

        # Settings Menu Overlay
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

    def run_startup_checks(self):
        """Called after mainloop starts so UI doesn't block."""
        def checks():
            self.btn_start.configure(state="disabled", text="CHECKING DEPENDENCIES...")
            self.deps_manager.verify_and_download()
            self.deps_manager.update_apps_if_needed()
            
            ln = LANGUAGES[self.current_lang]
            self.after(0, lambda: self.btn_start.configure(state="normal", text=ln["start_btn"]))
            
        import threading
        threading.Thread(target=checks, daemon=True).start()

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
        if not self.downloader.is_downloading:
            self.btn_start.configure(text=ln["start_btn"])
        self.btn_stop.configure(text=ln["stop_btn"])
        self.prog_label_curr.configure(text=f"{ln['prog_v']} 0%")
        self.prog_label_total.configure(text=f"{ln['prog_l']} 0/0")
        self.lbl_sett_theme.configure(text=ln["theme_lbl"])
        self.lbl_sett_lang.configure(text=ln["lang_lbl"])
        self.update_queue_ui(self.downloader.dl_queue.qsize())

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
            self.downloader.save_dir = d
            self.btn_folder.configure(text=f"📂 {os.path.basename(d)}")

    def update_queue_ui(self, qsize: int):
        ln = LANGUAGES[self.current_lang]
        self.queue_status_lbl.configure(text=f"{ln['queue_lbl']} {qsize}")

    def update_progress(self, percent: float):
        ln = LANGUAGES[self.current_lang]
        self.prog_bar_curr.set(percent / 100.0)
        self.prog_label_curr.configure(text=f"{ln['prog_v']} {percent}%")

    def stop_download(self):
        self.downloader.stop()
        self.btn_start.configure(state="normal")
        self.app_logger.log("\n--- All downloads STOPPED and queue CLEARED ---\n")

    def add_to_queue(self):
        raw_text = self.url_box.get("1.0", "end").strip()
        if not raw_text: 
            return
            
        urls = raw_text.split('\n')
        added = self.downloader.add_urls(urls)
        
        if added > 0:
            self.url_box.delete("1.0", "end")
            self.app_logger.log(f"\n--- {added} URL(s) added to queue ---\n")
            
            if not self.downloader.is_downloading:
                self.btn_start.configure(state="disabled")
                is_playlist = (self.mode_var.get() == 2)
                self.downloader.start_worker(self.quality_var.get(), is_playlist)

    def on_downloads_finished(self):
        ln = LANGUAGES[self.current_lang]
        self.btn_start.configure(state="normal")
        messagebox.showinfo("Infinite", ln["success"])
