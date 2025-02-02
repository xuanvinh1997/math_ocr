import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageGrab
from pynput import keyboard
import time
import datetime
import math
from db import Session, ScreenShot
from ocr import OCR  # Ensure your db.py defines these

# Create a new SQLAlchemy session
session = Session()
ocr_model = None
# --- Pagination Variables and Functions for Screenshot History ---
current_page = 0  # Zero-indexed page number
per_page = 10     # Number of records per page

def load_screenshot_history(page):
    """Load a specific page of screenshot records into the Treeview."""
    global current_page
    current_page = page

    # Clear existing items in the Treeview
    for item in tree.get_children():
        tree.delete(item)
    
    # Calculate offset and fetch page data
    offset_val = page * per_page
    screenshots = (session.query(ScreenShot)
                   .order_by(ScreenShot.id)
                   .limit(per_page)
                   .offset(offset_val)
                   .all())
    
    # Insert each record into the Treeview
    for ss in screenshots:
        created_at_str = ss.created_at.strftime("%Y-%m-%d %H:%M:%S") if ss.created_at else ""
        tree.insert("", "end", values=(ss.id, created_at_str, ss.stored_at, ss.text))
    
    # Update pagination controls
    total_records = session.query(ScreenShot).count()
    total_pages = math.ceil(total_records / per_page)
    page_label.config(text=f"Page {current_page + 1} of {total_pages}")
    
    prev_button.config(state="disabled" if current_page <= 0 else "normal")
    next_button.config(state="disabled" if current_page >= total_pages - 1 else "normal")

def next_page():
    load_screenshot_history(current_page + 1)

def prev_page():
    load_screenshot_history(current_page - 1)

# --- Screenshot Capture Functions ---
def start_screenshot():
    """
    Creates an overlay window that covers the entire screen.
    The user can click and drag to select an area for a screenshot.
    """
    # Create an overlay window
    overlay = tk.Toplevel(root)
    overlay.overrideredirect(True)
    screen_width = overlay.winfo_screenwidth()
    screen_height = overlay.winfo_screenheight()
    overlay.geometry(f"{screen_width}x{screen_height}+0+0")
    overlay.attributes("-topmost", True)
    overlay.attributes("-alpha", 0.3)
    overlay.config(bg="black")
    
    # Canvas for capturing mouse events
    canvas = tk.Canvas(overlay, cursor="cross", bg="black")
    canvas.pack(fill=tk.BOTH, expand=True)
    
    start_x = None
    start_y = None
    rect = None

    def on_button_press(event):
        nonlocal start_x, start_y, rect
        start_x, start_y = event.x, event.y
        rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="red", width=2)

    def on_mouse_drag(event):
        if rect:
            canvas.coords(rect, start_x, start_y, event.x, event.y)

    def on_button_release(event):
        nonlocal start_x, start_y, rect
        end_x, end_y = event.x, event.y
        overlay.destroy()  # Remove the overlay
        
        # Determine the bounding box for the selected area
        x1 = min(start_x, end_x)
        y1 = min(start_y, end_y)
        x2 = max(start_x, end_x)
        y2 = max(start_y, end_y)
        # Pause briefly to ensure overlay is gone
        time.sleep(0.2)
        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        filename = f"screenshot_{int(time.time())}.png"
        screenshot.save(filename)
        print(f"Screenshot saved as {filename}")
        
        # Insert a new record into the database
        new_ss = ScreenShot(stored_at=filename, text="")  # Optionally add extracted text here
        session.add(new_ss)
        session.commit()
        
        # Refresh the screenshot history table
        load_screenshot_history(current_page)
    
    # Bind mouse events to the canvas
    canvas.bind("<ButtonPress-1>", on_button_press)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_button_release)

def on_activate():
    """
    Called when the global hotkey is pressed.
    Schedules the screenshot overlay on the main Tkinter thread.
    """
    root.after(0, start_screenshot)

# --- Gemini API Key Handling in Tab B ---
def save_gemini_api_key():
    key = gemini_api_key_entry.get().strip()
    if key:
        # Here you could store the key in a configuration file or secure storage.
        print("Gemini API Key saved:", key)
        # write to a file .env
        with open(".env", "w") as f:
            f.write(f"GEMINI_API_KEY={key}")
        messagebox.showinfo("Success", "Gemini API Key saved successfully!")
        # reload the ocr model
        global ocr_model
        ocr_model = OCR(api_key=key)
    else:
        messagebox.showwarning("Input Error", "Please enter a valid Gemini API Key.")

# --- Main Application Window Setup ---
root = tk.Tk()
root.title("Screenshot Application")
root.geometry("800x600")

# Create a Notebook widget with two tabs
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# Tab A: Screenshot History with Pagination
tab_a = ttk.Frame(notebook)
notebook.add(tab_a, text="Screenshot History")

# Tab B: Gemini API Key Input
tab_b = ttk.Frame(notebook)
notebook.add(tab_b, text="Gemini API Key")

# --- Tab A Content: Treeview for Screenshot History ---
columns = ("ID", "Created At", "Stored At", "Extracted Text")
tree = ttk.Treeview(tab_a, columns=columns, show="headings")
tree.pack(expand=True, fill="both", side="top")

tree.heading("ID", text="ID")
tree.heading("Created At", text="Created At")
tree.heading("Stored At", text="Stored At")
tree.heading("Extracted Text", text="Extracted Text")
tree.column("ID", width=50, anchor="center")
tree.column("Created At", width=150, anchor="center")
tree.column("Stored At", width=150, anchor="center")
tree.column("Extracted Text", width=250, anchor="w")

# Add a vertical scrollbar to the Treeview
scrollbar = ttk.Scrollbar(tab_a, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")

# Pagination controls (Previous, Next buttons and page label)
pagination_frame = ttk.Frame(tab_a)
pagination_frame.pack(side="bottom", fill="x", pady=10)

prev_button = ttk.Button(pagination_frame, text="Previous", command=prev_page)
prev_button.pack(side="left", padx=10)
page_label = ttk.Label(pagination_frame, text="Page 1")
page_label.pack(side="left", padx=10)
next_button = ttk.Button(pagination_frame, text="Next", command=next_page)
next_button.pack(side="left", padx=10)

# Load the first page of screenshot history
load_screenshot_history(current_page)

# --- Tab B Content: Gemini API Key Input ---
input_frame = ttk.Frame(tab_b)
input_frame.pack(padx=20, pady=20, fill="x")

gemini_label = ttk.Label(input_frame, text="Gemini API Key:")
gemini_label.pack(side="left", padx=(0, 10))
# load the api key from the .env file
try:
    with open(".env", "r") as f:
        for line in f:
            if "GEMINI_API_KEY" in line:
                gemini_api_key = line.split("=")[1]
                break
except Exception as e:
    gemini_api_key = ""
gemini_api_key_entry = ttk.Entry(input_frame, width=40)
gemini_api_key_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
gemini_api_key_entry.insert(0, gemini_api_key)

save_button = ttk.Button(input_frame, text="Save", command=save_gemini_api_key)
save_button.pack(side="left")

# load ocr model
ocr_model = OCR(api_key=gemini_api_key)
# --- Global Hotkey Listener Setup ---
# Press Ctrl+M anywhere to trigger the screenshot overlay.
hotkey = keyboard.GlobalHotKeys({
    '<ctrl>+m': on_activate
})
hotkey.start()

# Start the Tkinter event loop
root.mainloop()
