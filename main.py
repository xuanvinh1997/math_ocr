# main.py
from pynput import keyboard
from config import Config
from screenshot_manager import ScreenshotManager
from ui.main_window import MainWindow
from ui.screenshot_overlay import ScreenshotOverlay
from ocr import OCR

def main():
    # Initialize components
    config = Config()
    ocr_model = OCR(api_key=config.gemini_api_key)
    screenshot_manager = ScreenshotManager(ocr_model)
    
    # Create main window
    app = MainWindow(config, screenshot_manager)
    
    # Setup hotkey handler
    def on_activate():
        overlay = ScreenshotOverlay(app.root, screenshot_manager.capture_screenshot)
        app.root.after(0, overlay.show)
    
    # Register global hotkey
    hotkey = keyboard.GlobalHotKeys({'<ctrl>+m': on_activate})
    hotkey.start()
    
    # Start the application
    app.start()

if __name__ == "__main__":
    main()