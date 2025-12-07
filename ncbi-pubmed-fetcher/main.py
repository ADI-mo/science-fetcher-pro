import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk, filedialog
import threading 
import webbrowser
from unified_client import UnifiedSearchManager

COLORS = {
    "bg_main": "#f4f6f9",       
    "bg_header": "#2c3e50",     
    "text_header": "#ecf0f1",   
    "accent": "#3498db",        
    "accent_hover": "#2980b9",  
    "success": "#27ae60",
    "frame_bg": "#ffffff"       
}

class PubMedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Science Fetcher Pro - CSV Edition")
        self.root.geometry("1100x850")
        self.root.configure(bg=COLORS["bg_main"])
        
        self.client = UnifiedSearchManager()
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready.")
        self.free_only_var = tk.BooleanVar(value=False) # New Filter
        
        self.is_searching = False
        self.last_results = []
        
        self.source_vars = {}
        self.available_sources = list(self.client.clients.keys())
        for source in self.available_sources:
            self.source_vars[source] = tk.BooleanVar(value=True)

        self._setup_styles()
        self._setup_ui()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Card.TFrame", background=COLORS["frame_bg"], relief="flat")
        style.configure("Main.TFrame", background=COLORS["bg_main"])
        style.configure("Action.TButton", background=COLORS["accent"], foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("Action.TButton", background=[('active', COLORS["accent_hover"])])
        
    def _setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg=COLORS["bg_header"], height=70)
        header.pack(fill=tk.X)
        tk.Label(header, text="🔬 Scientific Search Engine", bg=COLORS["bg_header"], fg="white", font=("Segoe UI", 20, "bold")).pack(pady=15)

        main_container = ttk.Frame(self.root, style="Main.TFrame", padding=20)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Controls
        controls_card = ttk.Frame(main_container, style="Card.TFrame", padding=15)
        controls_card.pack(fill=tk.X, pady=(0, 10))

        # Search Bar
        input_frame = ttk.Frame(controls_card, style="Card.TFrame")
        input_frame.pack(fill=tk.X, pady=5)
        
        # תיקון העתק-הדבק: שימוש ב-Entry רגיל עם תמיכה מובנית טובה יותר
        self.entry = ttk.Entry(input_frame, textvariable=self.search_var, font=("Segoe UI", 12))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry.bind('<Return>', lambda e: self.start_search())
        
        # אפשרות ללחיצה ימנית להדבקה
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Paste", command=lambda: self.entry.event_generate("<<Paste>>"))
        self.entry.bind("<Button-3>", self.show_context_menu)

        self.btn_search = ttk.Button(input_frame, text="SEARCH", style="Action.TButton", command=self.start_search)
        self.btn_search.pack(side=tk.LEFT, padx=5)

        # CSV Button
        self.btn_csv = ttk.Button(input_frame, text="EXPORT CSV", style="Action.TButton", command=self.export_csv, state="disabled")
        self.btn_csv.pack(side=tk.LEFT, padx=5)

        # Filters Frame
        filters_frame = ttk.Frame(controls_card, style="Card.TFrame")
        filters_frame.pack(fill=tk.X, pady=10)
        
        # Free Text Checkbox
        ttk.Checkbutton(filters_frame, text="Free Full Text Only (PDF)", variable=self.free_only_var).pack(side=tk.LEFT, padx=10)
        
        tk.Label(filters_frame, text="| Sources:", bg="white", fg="gray").pack(side=tk.LEFT, padx=10)

        for src in self.available_sources:
            ttk.Checkbutton(filters_frame, text=src, variable=self.source_vars[src]).pack(side=tk.LEFT, padx=5)

        # Progress
        self.progress = ttk.Progressbar(main_container, mode='indeterminate')
        
        # Results
        results_card = ttk.Frame(main_container, style="Card.TFrame", padding=2)
        results_card.pack(fill=tk.BOTH, expand=True)
        self.results_area = scrolledtext.ScrolledText(results_card, font=("Consolas", 11), state='disabled', padx=10, pady=10)
        self.results_area.pack(fill=tk.BOTH, expand=True)

        # Styling tags
        self.results_area.tag_configure("title", foreground="#2980b9", font=("Segoe UI", 14, "bold"))
        self.results_area.tag_configure("meta", foreground="#7f8c8d", font=("Segoe UI", 10))
        self.results_area.tag_configure("impact", foreground="#e74c3c", font=("Segoe UI", 10, "bold"))
        self.results_area.tag_configure("source", background="#27ae60", foreground="white", font=("Consolas", 9, "bold"))
        self.results_area.tag_configure("link", foreground="blue", underline=True)
        self.results_area.tag_bind("link", "<Button-1>", lambda e: self.open_link(e))

        # Status
        self.status_lbl = tk.Label(self.root, textvariable=self.status_var, bg="#dfe6e9", anchor="w")
        self.status_lbl.pack(fill=tk.X, side=tk.BOTTOM)

    def show_context_menu(self, event):
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def start_search(self):
        term = self.search_var.get().strip()
        if not term: return
        
        self.is_searching = True
        self.btn_search.config(state="disabled")
        self.btn_csv.config(state="disabled")
        self.progress.pack(fill=tk.X, pady=(0, 10), in_=self.results_area.master.master)
        self.progress.start(10)
        
        self.results_area.config(state='normal')
        self.results_area.delete(1.0, tk.END)
        self.results_area.config(state='disabled')
        self.status_var.set("Searching... (Fetching Impacts & PDFs)")
        
        threading.Thread(target=self.run_logic, args=(term,), daemon=True).start()

    def run_logic(self, term):
        selected = [k for k,v in self.source_vars.items() if v.get()]
        only_free = self.free_only_var.get()
        
        try:
            # מעביר את הפילטר only_free למנוע החיפוש
            results = self.client.search_all(term, active_sources=selected, limit_per_source=5, only_free=only_free)
            self.last_results = results
            self.root.after(0, self.finish, results, f"Found {len(results)} items.")
        except Exception as e:
            self.root.after(0, self.finish, [], f"Error: {e}")

    def finish(self, results, msg):
        self.progress.stop()
        self.progress.pack_forget()
        self.is_searching = False
        self.btn_search.config(state="normal")
        if results: self.btn_csv.config(state="normal")
        self.status_var.set(msg)
        
        self.results_area.config(state='normal')
        if not results:
            self.results_area.insert(tk.END, "No results found.\nTry broadening your search or unchecking 'Free Full Text'.")
        else:
            for i, item in enumerate(results, 1):
                url = item.get('url', 'N/A')
                pdf = item.get('pdf_url', 'N/A')
                citations = item.get('citations', 0)
                
                self.results_area.insert(tk.END, f" {item.get('source')} ", "source")
                self.results_area.insert(tk.END, f" #{i}  ", "meta")
                self.results_area.insert(tk.END, f"Impact: {citations} citations\n", "impact")
                
                self.results_area.insert(tk.END, f"{item.get('title')}\n", "title")
                
                if url != "N/A":
                    self.results_area.insert(tk.END, "🔗 Link to Article   ", ("link", url))
                if pdf != "N/A" and pdf != "Check Link":
                    self.results_area.insert(tk.END, "📄 Download PDF", ("link", pdf))
                
                self.results_area.insert(tk.END, f"\n{item.get('journal')} ({item.get('year')}) | Authors: {item.get('authors')}\n", "meta")
                self.results_area.insert(tk.END, f"{item.get('abstract')}\n", "text")
                self.results_area.insert(tk.END, "_"*60 + "\n\n")

        self.results_area.config(state='disabled')

    def open_link(self, event):
        try:
            index = self.results_area.index(f"@{event.x},{event.y}")
            tags = self.results_area.tag_names(index)
            for tag in tags:
                if tag.startswith("http"):
                    webbrowser.open(tag)
                    return
        except: pass

    def export_csv(self):
        if not self.last_results: return
        f = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if f:
            if self.client.save_to_csv(self.last_results, f):
                messagebox.showinfo("Export", "CSV saved successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = PubMedApp(root)
    root.mainloop()