# ui/main_window.py (updated version)
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import math
from ocr import OCR
from ui.ocr_viewer import OCRViewer

class MainWindow:
    def __init__(self, config, screenshot_manager):
        self.config = config
        self.screenshot_manager = screenshot_manager
        self.current_page = 0
        self.per_page = 10
        
        self.root = tk.Tk()
        self.root.title("Screenshot Application")
        self.root.geometry("800x600")
        
        self.setup_notebook()
        self.setup_screenshot_history()
        self.setup_api_key_tab()
        
    def setup_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")
        
        self.tab_a = ttk.Frame(self.notebook)
        self.tab_b = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_a, text="Screenshot History")
        self.notebook.add(self.tab_b, text="Gemini API Key")

    def setup_screenshot_history(self):
        columns = ("ID", "Created At", "Stored At", "Extracted Text")
        self.tree = ttk.Treeview(self.tab_a, columns=columns, show="headings")
        # Create container frame
        self.history_frame = ttk.Frame(self.tab_a)
        self.history_frame.pack(fill="both", expand=True)
        # Set up columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Created At", text="Created At")
        self.tree.heading("Stored At", text="Stored At")
        self.tree.heading("Extracted Text", text="Extracted Text")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Created At", width=150, anchor="center")
        self.tree.column("Stored At", width=150, anchor="center")
        self.tree.column("Extracted Text", width=250, anchor="w")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.tab_a, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        # Pack widgets
        self.tree.pack(expand=True, fill="both", side="left")
        scrollbar.pack(side="right", fill="y")
        
        # Bind double-click event
        self.tree.bind("<Double-1>", self.on_item_double_click)
        
        self.setup_pagination()
        self.load_screenshot_history()
        # Load initial data
        self.refresh_table()

    def setup_api_key_tab(self):
        """Setup the Gemini API key configuration tab."""
        # Create main container frame
        main_frame = ttk.Frame(self.tab_b, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Header section
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        header_label = ttk.Label(
            header_frame,
            text="Gemini API Configuration",
            font=("", 12, "bold")
        )
        header_label.pack(anchor="w")
        
        description_label = ttk.Label(
            header_frame,
            text="Enter your Gemini API key to enable OCR functionality. "
                "The key will be stored securely in your .env file.",
            wraplength=500
        )
        description_label.pack(anchor="w", pady=(5, 0))
        
        # API Key input section
        input_frame = ttk.LabelFrame(main_frame, text="API Key", padding="10")
        input_frame.pack(fill="x", pady=(0, 20))
        
        # Create a frame for the API key input and buttons
        key_frame = ttk.Frame(input_frame)
        key_frame.pack(fill="x")
        
        # API Key entry
        self.api_key_entry = ttk.Entry(key_frame, width=50, show="●")  # Use dots to mask the key
        self.api_key_entry.pack(side="left", padx=(0, 10))
        
        # If there's an existing API key, populate it
        if self.config.gemini_api_key:
            self.api_key_entry.insert(0, self.config.gemini_api_key)
        
        # Toggle visibility button
        self.show_key = tk.BooleanVar(value=False)
        
        def toggle_key_visibility():
            """Toggle between showing and hiding the API key."""
            if self.show_key.get():
                self.api_key_entry.config(show="")
                show_button.config(text="Hide Key")
            else:
                self.api_key_entry.config(show="●")
                show_button.config(text="Show Key")
        
        show_button = ttk.Button(
            key_frame,
            text="Show Key",
            command=lambda: [self.show_key.set(not self.show_key.get()), toggle_key_visibility()]
        )
        show_button.pack(side="left", padx=5)
        
        # Save button
        save_button = ttk.Button(
            key_frame,
            text="Save Key",
            command=self.save_api_key,
            style="Accent.TButton"
        )
        save_button.pack(side="left", padx=5)
        
        # Status section
        self.status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        self.status_frame.pack(fill="x")
        
        self.status_label = ttk.Label(
            self.status_frame,
            text="✓ API Key is configured and working" if self.config.gemini_api_key else "⚠ No API key configured",
            foreground="green" if self.config.gemini_api_key else "orange"
        )
        self.status_label.pack(anchor="w")
        
        # Test section
        test_frame = ttk.LabelFrame(main_frame, text="Test Configuration", padding="10")
        test_frame.pack(fill="x", pady=(20, 0))
        
        def test_api_key():
            """Test the current API key configuration."""
            if not self.config.gemini_api_key:
                messagebox.showwarning(
                    "No API Key",
                    "Please save an API key before testing."
                )
                return
            
            try:
                # Attempt to initialize OCR with current key
                ocr = OCR(api_key=self.config.gemini_api_key)
                # Try a simple test (you'll need to implement this in your OCR class)
                test_result = ocr.test_connection()
                
                if test_result:
                    messagebox.showinfo(
                        "Success",
                        "API key is valid and working correctly!"
                    )
                    self.status_label.config(
                        text="✓ API Key is configured and working",
                        foreground="green"
                    )
                else:
                    raise Exception("API test failed")
                    
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Failed to validate API key: {str(e)}"
                )
                self.status_label.config(
                    text="⚠ API key validation failed",
                    foreground="red"
                )
        
        test_button = ttk.Button(
            test_frame,
            text="Test API Key",
            command=test_api_key
        )
        test_button.pack(anchor="w", pady=5)
        
        # Help section
        help_frame = ttk.LabelFrame(main_frame, text="Help", padding="10")
        help_frame.pack(fill="x", pady=(20, 0))
        
        help_text = (
            "To get a Gemini API key:\n"
            "1. Go to Google Cloud Console\n"
            "2. Create or select a project\n"
            "3. Enable the Gemini API\n"
            "4. Create credentials (API key)\n"
            "5. Copy and paste the key above"
        )
        
        help_label = ttk.Label(
            help_frame,
            text=help_text,
            justify="left",
            wraplength=500
        )
        help_label.pack(anchor="w")
        
        def open_help_url():
            """Open the Gemini API documentation in default browser."""
            import webbrowser
            webbrowser.open("https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/api-quickstart")
        
        help_link = ttk.Label(
            help_frame,
            text="View Documentation →",
            foreground="blue",
            cursor="hand2"
        )
        help_link.pack(anchor="w", pady=(5, 0))
        help_link.bind("<Button-1>", lambda e: open_help_url())

    def save_api_key(self):
        """Save the API key and update the configuration."""
        key = self.api_key_entry.get().strip()
        if not key:
            messagebox.showwarning(
                "Input Error",
                "Please enter a valid API key."
            )
            return
        
        try:
            self.config.save_gemini_api_key(key)
            messagebox.showinfo(
                "Success",
                "API key saved successfully!"
            )
            self.status_label.config(
                text="✓ API Key is configured and working",
                foreground="green"
            )
            
            # Reinitialize OCR model with new key
            self.screenshot_manager.ocr_model = OCR(api_key=key)
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to save API key: {str(e)}"
            )
    def on_item_double_click(self, event):
        """Handle double-click on screenshot history item."""
        item = self.tree.selection()[0]
        values = self.tree.item(item)['values']
        if values:
            image_path = values[2]  # Stored At column
            ocr_text = values[3]    # Extracted Text column
            
            viewer = OCRViewer(self.root)
            viewer.show(image_path, ocr_text)

    def setup_pagination(self):
        """Setup pagination controls."""
        pagination_frame = ttk.Frame(self.history_frame)
        pagination_frame.pack(fill="x", padx=5, pady=5)
        
        # Add refresh button
        self.refresh_btn = ttk.Button(
            pagination_frame,
            text="↻ Refresh",
            command=self.refresh_table,
            width=10
        )
        self.refresh_btn.pack(side="left", padx=5)
        
        # Add pagination controls
        self.prev_button = ttk.Button(
            pagination_frame,
            text="← Previous",
            command=self.prev_page,
            width=10
        )
        self.prev_button.pack(side="left", padx=5)
        
        self.page_label = ttk.Label(pagination_frame, text="Page 1")
        self.page_label.pack(side="left", padx=10)
        
        self.next_button = ttk.Button(
            pagination_frame,
            text="Next →",
            command=self.next_page,
            width=10
        )
        self.next_button.pack(side="left", padx=5)
        
        # Add page size selector
        ttk.Label(pagination_frame, text="Items per page:").pack(side="left", padx=5)
        self.page_size_var = tk.StringVar(value=str(self.per_page))
        page_size_combo = ttk.Combobox(
            pagination_frame,
            textvariable=self.page_size_var,
            values=["5", "10", "20", "50"],
            width=5,
            state="readonly"
        )
        page_size_combo.pack(side="left", padx=5)
        page_size_combo.bind("<<ComboboxSelected>>", self.on_page_size_change)

    def load_screenshot_history(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load new items
        screenshots = self.screenshot_manager.get_screenshots(self.current_page, self.per_page)
        
        for ss in screenshots:
            created_at_str = ss.created_at.strftime("%Y-%m-%d %H:%M:%S") if ss.created_at else ""
            self.tree.insert("", "end", values=(ss.id, created_at_str, ss.stored_at, ss.text))
        
        # Update pagination
        total_records = self.screenshot_manager.get_total_screenshots()
        total_pages = math.ceil(total_records / self.per_page)
        self.page_label.config(text=f"Page {self.current_page + 1} of {total_pages}")
        
        self.prev_button.config(state="disabled" if self.current_page <= 0 else "normal")
        self.next_button.config(state="disabled" if self.current_page >= total_pages - 1 else "normal")

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_screenshot_history()

    def next_page(self):
        total_records = self.screenshot_manager.get_total_screenshots()
        total_pages = math.ceil(total_records / self.per_page)
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.load_screenshot_history()
    
    def refresh_table(self):
        """Refresh the table data."""
        # Save selected item if any
        selected_items = self.tree.selection()
        selected_id = None
        if selected_items:
            selected_id = self.tree.item(selected_items[0])['values'][0]
        
        # Clear existing items
        self.tree.delete(*self.tree.get_children())
        
        # Load new items
        screenshots = self.screenshot_manager.get_screenshots(self.current_page, self.per_page)
        
        # Insert new items
        for ss in screenshots:
            created_at_str = ss.created_at.strftime("%Y-%m-%d %H:%M:%S") if ss.created_at else ""
            item_id = self.tree.insert("", "end", values=(ss.id, created_at_str, ss.stored_at, ss.text))
            
            # Reselect previously selected item if it exists
            if selected_id and ss.id == selected_id:
                self.tree.selection_set(item_id)
                self.tree.see(item_id)
        
        # Update pagination controls
        total_records = self.screenshot_manager.get_total_screenshots()
        total_pages = math.ceil(total_records / self.per_page)
        self.page_label.config(text=f"Page {self.current_page + 1} of {total_pages}")
        
        # Update button states
        self.prev_button.config(state="disabled" if self.current_page <= 0 else "normal")
        self.next_button.config(state="disabled" if self.current_page >= total_pages - 1 else "normal")

    def sort_column(self, column, reverse):
        """Sort table by a column."""
        column_index = self.tree["columns"].index(column)
        items = [(self.tree.set(k, column), k) for k in self.tree.get_children("")]
        
        # Convert values for proper sorting
        if column == "ID":
            items.sort(key=lambda x: int(x[0]), reverse=reverse)
        elif column == "Created At":
            items.sort(key=lambda x: datetime.strptime(x[0], "%Y-%m-%d %H:%M:%S") if x[0] else datetime.min, reverse=reverse)
        else:
            items.sort(reverse=reverse)
        
        # Rearrange items
        for index, (_, k) in enumerate(items):
            self.tree.move(k, "", index)
        
        # Reverse sort next time
        self.tree.heading(column, command=lambda: self.sort_column(column, not reverse))

    def on_page_size_change(self, event):
        """Handle page size change."""
        self.per_page = int(self.page_size_var.get())
        self.current_page = 0  # Reset to first page
        self.refresh_table()

    def start(self):
        self.root.mainloop()