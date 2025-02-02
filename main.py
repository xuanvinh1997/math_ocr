import tkinter as tk
from PIL import ImageGrab
from pynput import keyboard
import time

def start_screenshot():
    """
    Creates an overlay window that covers the entire screen without going into
    macOS fullscreen mode. The user can click and drag to select an area to
    capture as a screenshot.
    """
    # Create a new top-level window.
    overlay = tk.Toplevel(root)
    
    # Remove window decorations (borders, title bar, etc.).
    overlay.overrideredirect(True)
    
    # Get screen dimensions and set geometry to cover the screen.
    screen_width = overlay.winfo_screenwidth()
    screen_height = overlay.winfo_screenheight()
    overlay.geometry(f"{screen_width}x{screen_height}+0+0")
    
    # Keep the overlay on top and set transparency.
    overlay.attributes("-topmost", True)
    overlay.attributes("-alpha", 0.3)
    overlay.config(bg="black")
    
    # Create a canvas to capture mouse events.
    canvas = tk.Canvas(overlay, cursor="cross", bg="black")
    canvas.pack(fill=tk.BOTH, expand=True)
    
    # Variables to hold starting coordinates and the drawn rectangle.
    start_x = None
    start_y = None
    rect = None

    def on_button_press(event):
        nonlocal start_x, start_y, rect
        start_x, start_y = event.x, event.y
        # Create a rectangle that starts as a point.
        rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="red", width=2)

    def on_mouse_drag(event):
        # Update the rectangle as the mouse is dragged.
        if rect:
            canvas.coords(rect, start_x, start_y, event.x, event.y)

    def on_button_release(event):
        nonlocal start_x, start_y, rect
        end_x, end_y = event.x, event.y
        # Remove the overlay.
        overlay.destroy()
        # Calculate the bounding box of the selected area.
        x1 = min(start_x, end_x)
        y1 = min(start_y, end_y)
        x2 = max(start_x, end_x)
        y2 = max(start_y, end_y)
        # Pause briefly to ensure the overlay is gone before capturing.
        time.sleep(0.2)
        # Capture the selected area.
        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        filename = f"screenshot_{int(time.time())}.png"
        screenshot.save(filename)
        print(f"Screenshot saved as {filename}")

    # Bind the mouse events to the canvas.
    canvas.bind("<ButtonPress-1>", on_button_press)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_button_release)

def on_activate():
    """
    This function is called when the hotkey is pressed.
    It schedules the screenshot overlay to be created on the main Tkinter thread.
    """
    root.after(0, start_screenshot)

# --- Main Application Setup --- #

# Create a hidden root Tkinter window.
root = tk.Tk()
root.withdraw()

# Set up the global hotkey listener (Ctrl+Alt+M).
hotkey = keyboard.GlobalHotKeys({
    '<ctrl>+m': on_activate
})
hotkey.start()

# Start the Tkinter event loop.
root.mainloop()
