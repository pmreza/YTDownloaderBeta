import os
import sys
import subprocess

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

if __name__ == "__main__":
    install_dependencies()
    
    # Base path is the project root (one level up from src)
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Add base path to sys.path so 'src' can be imported
    if base_path not in sys.path:
        sys.path.insert(0, base_path)
        
    # Import the UI only after dependencies are installed
    from src.ui.app_window import InfiniteDownload
    
    app = InfiniteDownload(base_path)
    app.run_startup_checks()
    app.mainloop()
