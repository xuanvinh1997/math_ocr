import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class OCRViewer:
    def __init__(self, parent):
        self.popup = tk.Toplevel(parent)
        self.popup.title("OCR Result Viewer")
        self.popup.geometry("800x600")
        
        # Create main container
        self.main_frame = ttk.Frame(self.popup)
        self.main_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create paned window to split image and text
        self.paned = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned.pack(expand=True, fill="both")
        
        # Left side - Image
        self.image_frame = ttk.Frame(self.paned)
        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack(expand=True, fill="both")
        
        # Right side - Text
        self.text_frame = ttk.Frame(self.paned)
        self.text_area = tk.Text(self.text_frame, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill="both")
        
        # Add frames to paned window
        self.paned.add(self.image_frame)
        self.paned.add(self.text_frame)
        
    def show(self, image_path, ocr_text):
        """Display the image and OCR text."""
        # Load and display image
        image = Image.open(image_path)
        # Resize image to fit the window while maintaining aspect ratio
        display_size = (400, 400)
        image.thumbnail(display_size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.image_label.configure(image=photo)
        self.image_label.image = photo  # Keep a reference
        
        # Display OCR text
        self.text_area.delete('1.0', tk.END)
        self.text_area.insert('1.0', ocr_text)
        
        # Center the window on screen
        self.popup.update_idletasks()
        width = self.popup.winfo_width()
        height = self.popup.winfo_height()
        x = (self.popup.winfo_screenwidth() // 2) - (width // 2)
        y = (self.popup.winfo_screenheight() // 2) - (height // 2)
        self.popup.geometry(f'{width}x{height}+{x}+{y}')