import tkinter as tk
from tkinter import messagebox, scrolledtext, font, ttk
import threading 
import datetime
import webbrowser  # <--- הוספנו את זה לתיקון השגיאה
from unified_client import UnifiedSearchManager

# --- COLOR PALETTE ---
COLORS = {
    "bg_main": "#f4f6f9",       
    "bg_header": "#2c3e50",     
    "text_header": "#ecf0f1",   
    "accent": "#3498db",        
    "accent_hover": "#2980b9",  
    "success": "#27ae60",       
    "warning": "#e67e22",       
    "frame_bg": "#ffffff"       
}

class PubMedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultimate Science Fetcher Pro")
        self.root.geometry("1100x800")
        self.root.configure(bg=COLORS["bg_main"])
        
        # Initialize Logic
        self.client = UnifiedSearchManager()
        
        # Variables
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready to search scientific databases.")
        self.is_searching = False
        
        # Source Checkbox Variables
        self.source_vars = {}
        self.available_sources = list(self.client.clients.keys())
        for source in self.available_sources:
            self.source_vars[source] = tk.BooleanVar(value=True)

        self._setup_styles()
        self._setup_ui()

    def _setup_styles(self):
        """Configures custom styles for a modern look."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure Frame styles
        style.configure("Card.TFrame", background=COLORS["frame_bg"], relief="flat")
        style.configure("Main.TFrame", background=COLORS["bg_main"])
        
        # Configure Label styles
        style.configure("Header.TLabel", background=COLORS["bg_header"], foreground=COLORS["text_header"], font=("Segoe UI", 20, "bold"))
        style.configure("SubHeader.TLabel", background=COLORS["frame_bg"], foreground="#34495e", font=("Segoe UI", 12, "bold"))
        style.configure("Status.TLabel", background="#dfe6e9", foreground="#2d3436", font=("Segoe UI", 10))
        
        # Configure Button styles
        style.configure("Action.TButton", background=COLORS["accent"], foreground="white", font=("Segoe UI", 11, "bold"), borderwidth=0, focuscolor="none")
        style.map("Action.TButton", background=[('active', COLORS["accent_hover"])])
        
        # Configure Checkbutton
        style.configure("TCheckbutton", background=COLORS["frame_bg"], font=("Segoe UI", 10), focuscolor="none")

    def _setup_ui(self):
        # --- HEADER SECTION ---
        header_frame = tk.Frame(self.root, bg=COLORS["bg_header"], height=80)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False) 
        
        tk.Label(header_frame, text="🔬 Scientific Paper Explorer", 
                 bg=COLORS["bg_header"], fg=COLORS["text_header"], 
                 font=("Segoe UI", 24, "bold")).pack(pady=15)

        # --- MAIN CONTAINER ---
        main_container = ttk.Frame(self.root, style="Main.TFrame", padding=20)
        main_container.pack(fill=tk.BOTH, expand=True)

        # --- SEARCH & FILTER SECTION (Top Card) ---
        search_card = ttk.Frame(main_container, style="Card.TFrame", padding=15)
        search_card.pack(fill=tk.X, pady=(0, 15)) 

        # Search Bar Row
        ttk.Label(search_card, text="Research Topic:", style="SubHeader.TLabel").pack(anchor="w")
        
        input_frame = ttk.Frame(search_card, style="Card.TFrame")
        input_frame.pack(fill=tk.X, pady=10)
        
        entry = ttk.Entry(input_frame, textvariable=self.search_var, font=("Segoe UI", 12))
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        entry.bind('<Return>', lambda e: self.start_search_thread())
        
        self.btn_search = ttk.Button(input_frame, text="SEARCH DATABASE", style="Action.TButton", cursor="hand2", command=self.start_search_thread)
        self.btn_search.pack(side=tk.LEFT, ipadx=20, ipady=5)

        # Divider
        ttk.Separator(search_card, orient='horizontal').pack(fill=tk.X, pady=15)

        # Sources Row
        ttk.Label(search_card, text="Active Sources:", style="SubHeader.TLabel").pack(anchor="w", pady=(0, 10))
        
        sources_grid = ttk.Frame(search_card, style="Card.TFrame")
        sources_grid.pack(fill=tk.X)
        
        # Create a flexible grid for checkboxes
        for i, source in enumerate(self.available_sources):
            cb = ttk.Checkbutton(sources_grid, text=source, variable=self.source_vars[source])
            cb.grid(row=0, column=i, padx=15, sticky="w")

        # --- PROGRESS BAR ---
        self.progress = ttk.Progressbar(main_container, mode='indeterminate', length=200)
        
        # --- RESULTS SECTION (Bottom Card) ---
        results_card = ttk.Frame(main_container, style="Card.TFrame", padding=2) 
        results_card.pack(fill=tk.BOTH, expand=True)
        
        text_frame = ttk.Frame(results_card, style="Card.TFrame", padding=10)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.results_area = scrolledtext.ScrolledText(text_frame, font=("Consolas", 11), state='disabled', bg="#fcfcfc", relief="flat", padx=10, pady=10)
        self.results_area.pack(fill=tk.BOTH, expand=True)
        
        # Configure Text Tags
        self.results_area.tag_configure("title", foreground="#2980b9", font=("Segoe UI", 14, "bold"))
        self.results_area.tag_configure("meta", foreground="#7f8c8d", font=("Segoe UI", 10, "italic"))
        self.results_area.tag_configure("source_tag", foreground="#ffffff", background="#27ae60", font=("Consolas", 9, "bold"))
        self.results_area.tag_configure("separator", foreground="#bdc3c7")
        # Link styling
        self.results_area.tag_configure("link", foreground="blue", underline=True)
        self.results_area.tag_bind("link", "<Enter>", lambda e: self.results_area.config(cursor="hand2"))
        self.results_area.tag_bind("link", "<Leave>", lambda e: self.results_area.config(cursor=""))

        # --- STATUS BAR ---
        status_bar = ttk.Label(self.root, textvariable=self.status_var, style="Status.TLabel", anchor="w", padding=5)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _log_search_history(self, term):
        try:
            with open("search_history.log", "a", encoding="utf-8") as f:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] Term: {term}\n")
        except: pass

    def start_search_thread(self):
        if self.is_searching: return
        term = self.search_var.get().strip()
        if not term:
            messagebox.showwarning("⚠️ Input Required", "Please enter a search topic.")
            return

        self.is_searching = True
        self.btn_search.config(state="disabled")
        self.progress.pack(fill=tk.X, pady=(0, 10), in_=self.results_area.master.master) 
        self.progress.start(10)
        
        self.status_var.set(f"Searching for '{term}' across 7 databases... This may take a few seconds.")
        self.results_area.config(state='normal')
        self.results_area.delete(1.0, tk.END)
        self.results_area.config(state='disabled')

        threading.Thread(target=self.run_search_logic, args=(term,), daemon=True).start()

    def run_search_logic(self, term):
        self._log_search_history(term)
        selected_sources = [name for name, var in self.source_vars.items() if var.get()]
        
        if not selected_sources:
            self.root.after(0, self.finish_search, [], "⚠️ No databases selected!")
            return

        try:
            results = self.client.search_all(term, active_sources=selected_sources, limit_per_source=3)
            
            # Save File logic