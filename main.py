import flet as ft
import os
import subprocess
import json
import threading
import queue
import time
import re
import urllib.request

# Global state
save_dir = os.path.join(os.path.expanduser("~"), "Downloads")
bin_path = os.path.join(os.getcwd(), "bin")
yt_dlp_path = os.path.join(bin_path, "yt-dlp.exe")
ffmpeg_path = os.path.join(bin_path, "ffmpeg.exe")
os.makedirs(bin_path, exist_ok=True)

dl_queue = queue.Queue()
is_paused = False
download_process = None
current_url = None
current_file_path = None

def check_yt_dlp():
    if not os.path.exists(yt_dlp_path):
        try:
            urllib.request.urlretrieve("https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe", yt_dlp_path)
        except:
            pass

def main(page: ft.Page):
    global save_dir, is_paused, download_process, current_url, current_file_path
    
    page.title = "Infinite Downloader"
    page.window.icon = "logo.ico"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 1100
    page.window.height = 750
    page.window.min_width = 900
    page.window.min_height = 600
    
    # Custom Fonts (English as main, IranianSans fallback)
    page.fonts = {
        "IranianSans": "Iranian Sans.ttf",
        "Inter": "https://raw.githubusercontent.com/rsms/inter/master/docs/font-files/Inter-Regular.woff2"
    }
    page.theme = ft.Theme(font_family="Inter")
    
    BRAND_COLOR = "#E3182C"
    ACTION_COLOR = "#0078D4"
    BG_BLUR = ft.Blur(15, 15)
    
    # --- Views ---
    
    # 1. Home View
    search_input = ft.TextField(
        hint_text="Paste YouTube link here...",
        border_radius=20,
        filled=True,
        bgcolor="#99ffffff",
        expand=True,
        border_color="transparent",
        text_size=16
    )
    
    cards_list = ft.ListView(expand=True, spacing=15, padding=20)
    
    def on_check_click(e):
        url = search_input.value.strip()
        if not url: return
        check_btn.disabled = True
        check_btn.content = "Checking..."
        page.update()
        threading.Thread(target=fetch_metadata, args=(url,), daemon=True).start()

    check_btn = ft.ElevatedButton(
        "Check Link", 
        on_click=on_check_click, 
        bgcolor=ACTION_COLOR, 
        color=ft.Colors.WHITE,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20), padding=20)
    )
    
    home_view = ft.Column(
        expand=True,
        controls=[
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.SEARCH, color=ft.Colors.GREY_600),
                    search_input,
                    check_btn
                ]),
                padding=20,
                bgcolor="#66ffffff",
                blur=BG_BLUR,
                border_radius=20,
                margin=ft.Margin(top=40, left=40, right=40, bottom=10)
            ),
            cards_list
        ]
    )
    
    def fetch_metadata(url):
        try:
            cmd = [yt_dlp_path, "-j", "--no-warnings", url]
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', startupinfo=startupinfo)
            if res.returncode != 0: raise Exception(res.stderr)
            
            data = json.loads(res.stdout.splitlines()[-1])
            title = data.get('title', 'Unknown Title')
            channel = data.get('uploader', 'Unknown Channel')
            thumb = data.get('thumbnail', '')
            
            add_video_card(url, title, channel, thumb)
        except Exception as ex:
            print("Error fetching metadata:", ex)
        finally:
            check_btn.disabled = False
            check_btn.content = "Check Link"
            search_input.value = ""
            page.update()

    def add_video_card(url, title, channel, thumb_url):
        format_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("1080p MP4"),
                ft.dropdown.Option("720p MP4"),
                ft.dropdown.Option("Audio MP3")
            ],
            value="1080p MP4",
            width=150,
            border_radius=15,
            bgcolor="#ccffffff"
        )
        
        def start_dl(e):
            dl_queue.put((url, format_dropdown.value))
            cards_list.controls.remove(card)
            navigate("downloads")
            page.update()
            
        dl_btn = ft.ElevatedButton("Download", on_click=start_dl, bgcolor=BRAND_COLOR, color=ft.Colors.WHITE, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=15)))
        
        card = ft.Container(
            content=ft.Row([
                ft.Image(src=thumb_url, width=200, height=112, fit=ft.BoxFit.COVER, border_radius=10) if thumb_url else ft.Container(width=200, height=112, bgcolor=ft.Colors.GREY_300, border_radius=10),
                ft.Column([
                    ft.Text(title, weight=ft.FontWeight.BOLD, size=18, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(channel, color=ft.Colors.GREY_600, size=14),
                    ft.Row([format_dropdown, dl_btn], spacing=15)
                ], expand=True, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ]),
            bgcolor="#80ffffff",
            blur=BG_BLUR,
            border_radius=20,
            padding=15,
            margin=ft.Margin(left=40, right=40, top=10, bottom=10)
        )
        cards_list.controls.insert(0, card)
        page.update()

    # 2. Downloads View
    dl_title = ft.Text("Active Downloads", size=28, weight="bold", color=ft.Colors.BLACK_87)
    prog_lbl = ft.Text("Idle", size=14, color=ft.Colors.GREY_700)
    prog_bar = ft.ProgressBar(value=0, height=10, color=ACTION_COLOR, bgcolor="#4dffffff")
    
    log_box = ft.ListView(expand=True, auto_scroll=True, padding=10)
    
    def toggle_pause(e):
        global is_paused, download_process
        is_paused = not is_paused
        pause_btn.content = "Resume" if is_paused else "Pause"
        pause_btn.icon = ft.Icons.PLAY_ARROW if is_paused else ft.Icons.PAUSE
        if is_paused and download_process:
            try: subprocess.run(f"taskkill /F /T /PID {download_process.pid}", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            except: pass
        page.update()

    def cancel_dl(e):
        global current_url, current_file_path, is_paused, download_process
        with dl_queue.mutex: dl_queue.queue.clear()
        if download_process:
            try: subprocess.run(f"taskkill /F /T /PID {download_process.pid}", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            except: pass
            
        if current_file_path and os.path.exists(current_file_path + ".part"):
            try:
                import glob
                for f in glob.glob(current_file_path + "*"): os.remove(f)
            except: pass
            
        current_url = None
        current_file_path = None
        is_paused = False
        pause_btn.content = "Pause"
        pause_btn.icon = ft.Icons.PAUSE
        prog_bar.value = 0
        prog_lbl.value = "Canceled and cleared."
        log_box.controls.append(ft.Text("--- Download canceled ---", color=ft.Colors.RED_500))
        page.update()

    pause_btn = ft.ElevatedButton("Pause", icon=ft.Icons.PAUSE, on_click=toggle_pause, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)))
    cancel_btn = ft.ElevatedButton("Cancel", icon=ft.Icons.STOP, on_click=cancel_dl, bgcolor=BRAND_COLOR, color=ft.Colors.WHITE, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)))
    
    dl_view = ft.Column(
        expand=True,
        visible=False,
        controls=[
            ft.Container(
                content=ft.Column([
                    ft.Row([dl_title, ft.Row([pause_btn, cancel_btn])], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    prog_lbl,
                    prog_bar
                ]),
                padding=30,
                bgcolor="#66ffffff",
                blur=BG_BLUR,
                border_radius=20,
                margin=40
            ),
            ft.Container(
                content=log_box,
                expand=True,
                padding=20,
                bgcolor="#4dffffff",
                blur=BG_BLUR,
                border_radius=20,
                margin=ft.Margin(left=40, right=40, bottom=40, top=0)
            )
        ]
    )
    
    # 3. Settings View
    def on_path_change(e):
        global save_dir
        save_dir = e.control.value
        
    path_input = ft.TextField(
        value=save_dir,
        label="Download Directory Path",
        on_change=on_path_change,
        width=500,
        border_radius=10,
        bgcolor="#99ffffff"
    )
    
    sett_view = ft.Column(
        expand=True,
        visible=False,
        controls=[
            ft.Container(
                content=ft.Column([
                    ft.Text("Settings", size=28, weight="bold", color=ft.Colors.BLACK_87),
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    ft.Text("Download Directory", size=16, weight="bold"),
                    path_input,
                    ft.Divider(height=40, color=ft.Colors.TRANSPARENT),
                    ft.Text("Creator Info", size=16, weight="bold"),
                    ft.Text("Developed by You\nTelegram: @YourID", size=14, color=ft.Colors.GREY_700)
                ]),
                padding=40,
                bgcolor="#66ffffff",
                blur=BG_BLUR,
                border_radius=20,
                margin=40
            )
        ]
    )

    # --- Navigation ---
    def navigate(route):
        home_view.visible = (route == "home")
        dl_view.visible = (route == "downloads")
        sett_view.visible = (route == "settings")
        
        for btn in [btn_home, btn_dl, btn_sett]:
            btn.bgcolor = "#330078d4" if btn.data == route else ft.Colors.TRANSPARENT
            btn.color = ACTION_COLOR if btn.data == route else ft.Colors.GREY_800
        page.update()

    btn_home = ft.TextButton("Home", icon=ft.Icons.HOME, data="home", on_click=lambda e: navigate("home"), height=50)
    btn_dl = ft.TextButton("Downloads", icon=ft.Icons.DOWNLOAD, data="downloads", on_click=lambda e: navigate("downloads"), height=50)
    btn_sett = ft.TextButton("Settings", icon=ft.Icons.SETTINGS, data="settings", on_click=lambda e: navigate("settings"), height=50)

    sidebar = ft.Container(
        width=250,
        bgcolor="#4dffffff",
        blur=BG_BLUR,
        padding=20,
        content=ft.Column([
            ft.Row([
                ft.Image(src="logo.ico", width=40, height=40, fit=ft.BoxFit.CONTAIN) if os.path.exists("logo.ico") else ft.Icon(ft.Icons.CLOUD_DOWNLOAD, color=ACTION_COLOR, size=30),
                ft.Text("Infinite Project", size=18, weight="bold", color=ft.Colors.BLACK_87)
            ], alignment=ft.MainAxisAlignment.START),
            ft.Divider(height=40, color=ft.Colors.TRANSPARENT),
            btn_home,
            btn_dl,
            btn_sett
        ])
    )

    # Main Layout
    main_layout = ft.Container(
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=["#e0c3fc", "#8ec5fc"] # MacOS-like soft gradient background
        ),
        content=ft.Row([
            sidebar,
            ft.Stack([
                home_view,
                dl_view,
                sett_view
            ], expand=True)
        ], spacing=0)
    )
    
    page.add(main_layout)
    navigate("home")

    # --- Worker Engine ---
    def queue_worker():
        global is_paused, download_process, current_url, current_file_path
        while True:
            if not dl_queue.empty() or is_paused or current_url:
                if is_paused:
                    time.sleep(1)
                    continue
                
                if not current_url:
                    if dl_queue.empty(): continue
                    current_url, quality = dl_queue.get()
                else:
                    quality = "1080p MP4"
                
                log_box.controls.append(ft.Text(f">>> Downloading: {current_url}", color=ACTION_COLOR, weight="bold"))
                page.update()
                
                run_process(current_url, quality)
                
                if is_paused: continue
                current_url = None
                current_file_path = None
                dl_queue.task_done()
                prog_bar.value = 1.0
                prog_lbl.value = "Finished."
                page.update()
            else:
                time.sleep(1)

    def run_process(url, quality):
        global download_process, current_file_path
        if "Audio" in quality:
            format_str = "bestaudio[ext=m4a]"
        else:
            q = quality.replace("p MP4", "")
            format_str = f"bestvideo[height<={q}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={q}]+bestaudio/best[height<={q}]"
            
        cmd = [yt_dlp_path, url, "--output", os.path.join(save_dir, "%(title)s.%(ext)s"),
               "--ffmpeg-location", ffmpeg_path, "--newline", "--progress", "--continue",
               "-f", format_str, "--merge-output-format", "mp4"]
        
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            download_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, 
                                 encoding='utf-8', startupinfo=startupinfo)
            for line in download_process.stdout:
                line_str = line.strip()
                if not line_str: continue
                
                log_box.controls.append(ft.Text(line_str, size=12, color=ft.Colors.GREY_800))
                if len(log_box.controls) > 80: log_box.controls.pop(0) # Keep log light
                
                if "[download] Destination:" in line:
                    current_file_path = line.split("Destination:")[1].strip()
                elif "has already been downloaded" in line and "[download]" in line:
                    try: current_file_path = line.split("[download]")[1].split("has already")[0].strip()
                    except: pass
                
                if "[download]" in line and "%" in line:
                    m = re.search(r"(\d+\.\d+)%", line)
                    if m:
                        val = float(m.group(1)) / 100
                        prog_bar.value = val
                        prog_lbl.value = f"Progress: {m.group(1)}%"
                page.update()
            download_process.wait()
        except Exception as e: 
            log_box.controls.append(ft.Text(f"Error: {e}", color=ft.Colors.RED_500))
            page.update()

    threading.Thread(target=queue_worker, daemon=True).start()
    threading.Thread(target=check_yt_dlp, daemon=True).start()

if __name__ == "__main__":
    ft.app(target=main, assets_dir=".")