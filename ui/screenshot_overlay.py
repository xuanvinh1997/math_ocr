import time
import tkinter as tk

class ScreenshotOverlay:
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        self.start_x = None
        self.start_y = None
        self.rect = None
        
    def show(self):
        """Display the screenshot selection overlay."""
        self.overlay = tk.Toplevel(self.parent)
        self.overlay.overrideredirect(True)
        screen_width = self.overlay.winfo_screenwidth()
        screen_height = self.overlay.winfo_screenheight()
        self.overlay.geometry(f"{screen_width}x{screen_height}+0+0")
        self.overlay.attributes("-topmost", True)
        self.overlay.attributes("-alpha", 0.3)
        self.overlay.config(bg="black")
        
        self.canvas = tk.Canvas(self.overlay, cursor="cross", bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        
        self.parent.withdraw()

    def on_button_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="red", width=2
        )

    def on_mouse_drag(self, event):
        if self.rect:
            self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        bbox = (
            min(self.start_x, event.x),
            min(self.start_y, event.y),
            max(self.start_x, event.x),
            max(self.start_y, event.y)
        )
        self.overlay.destroy()
        time.sleep(0.2)  # Ensure overlay is gone
        self.parent.deiconify()
        self.callback(bbox)