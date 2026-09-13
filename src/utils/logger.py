import tkinter.messagebox as messagebox

class AppLogger:
    def __init__(self, log_box_widget=None):
        self.log_box = log_box_widget
        
    def set_log_box(self, log_box_widget):
        self.log_box = log_box_widget

    def log(self, message: str, level: str = "info"):
        """Write logs to the UI log box."""
        if not self.log_box:
            print(f"[{level.upper()}] {message}")
            return
            
        formatted_message = f"{message}\n"
        self.log_box.insert("end", formatted_message)
        self.log_box.see("end")

    def handle_error(self, error: Exception, context: str = ""):
        """Centralized error handler for the application."""
        error_msg = str(error)
        
        # Friendly translations for known errors
        if "HTTP Error 429" in error_msg:
            friendly_msg = "YouTube is temporarily blocking your IP (Error 429 - Too Many Requests).\nPlease try using a VPN, change your IP, or wait a few hours."
            self.log(f"CRITICAL ERROR: {friendly_msg}", level="error")
            messagebox.showwarning("IP Blocked (429)", friendly_msg)
            
        elif "Sign in to confirm you" in error_msg or "PO Token" in error_msg:
            friendly_msg = "YouTube is requesting bot verification.\nIf you are already using deno, your IP might be heavily flagged.\nYou may need to use browser cookies."
            self.log(f"VERIFICATION ERROR: {friendly_msg}", level="error")
            messagebox.showerror("Bot Verification Required", friendly_msg)
            
        elif "ffprobe and ffmpeg not found" in error_msg:
            friendly_msg = "FFmpeg is missing! Please restart the application to download it automatically."
            self.log(f"DEPENDENCY ERROR: {friendly_msg}", level="error")
            messagebox.showerror("Missing FFmpeg", friendly_msg)
            
        else:
            self.log(f"Error [{context}]: {error_msg}", level="error")

