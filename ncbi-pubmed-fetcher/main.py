import tkinter as tk
from tkinter import messagebox, scrolledtext, font, ttk
import threading 
import datetime
from unified_client import UnifiedSearchManager

class PubMedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultimate Science Fetcher (7 Sources)")
        self.root.geometry("1000x750")
        
        self.client = UnifiedSearchManager()
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready")
        self.is_searching = False
        
        self.source_vars = {}
        self.available_sources = list(self.client.clients.keys())
        for source in self.available_sources:
            self.source_vars[source] = tk.BooleanVar(value=True)

        self._setup_ui()

    def _setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        header_font = font.Font(family="Segoe UI", size=16, weight="bold")
        tk.Label(main_frame, text="Unified Scientific Search Engine", font=header_font, fg="#2c3e50").pack(pady=5)

        search_frame = ttk.LabelFrame(main_frame, text="Search Query", padding=10)
        search_frame.pack(fill=tk.X, pady=5)
        
        entry = ttk.Entry(search_frame, textvariable=self.search_var, font=("Segoe UI", 11))
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        entry.bind('<Return>', lambda e: self.start_search_thread())
        
        self.btn_search = ttk.Button(search_frame, text="Search", command=self.start_search_thread)
        self.btn_search.pack(side=tk.LEFT, padx=5)

        sources_frame = ttk.LabelFrame(main_frame, text="Select Databases", padding=10)
        sources_frame.pack(fill=tk.X, pady=5)
        
        for i, source in enumerate(self.available_sources):
            cb = ttk.Checkbutton(sources_frame, text=source, variable=self.source_vars[source])
            cb.grid(row=0, column=i, padx=10, sticky="w")

        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=5)

        results_frame = ttk.LabelFrame(main_frame, text="Results", padding=5)
        results_frame.pack(fill=tk.BOTH, expand=True)

        self.results_area = scrolledtext.ScrolledText(results_frame, font=("Consolas", 10), state='disabled')
        self.results_area.pack(fill=tk.BOTH, expand=True)
        self.results_area.tag_configure("header", foreground="blue", font=("Consolas", 11, "bold"))
        self.results_area.tag_configure("source", foreground="green", font=("Consolas", 9, "italic"))

        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
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
            messagebox.showwarning("Input Error", "Please enter a search term.")
            return

        self.is_searching = True
        self.btn_search.config(state="disabled")
        self.progress.start(10)
        self.status_var.set("Searching... Please wait.")
        self.results_area.config(state='normal')
        self.results_area.delete(1.0, tk.END)
        self.results_area.config(state='disabled')

        threading.Thread(target=self.run_search_logic, args=(term,), daemon=True).start()

    def run_search_logic(self, term):
        self._log_search_history(term)
        selected_sources = [name for name, var in self.source_vars.items() if var.get()]
        
        if not selected_sources:
            self.root.after(0, self.finish_search, [], "No sources selected!")
            return

        try:
            results = self.client.search_all(term, active_sources=selected_sources, limit_per_source=3)
            safe_term = "".join(c if c.isalnum() else "_" for c in term)
            filename = f"results_{safe_term}.txt"
            self.client.save_data(results, filename)
            
            msg = f"Found {len(results)} items. Saved to {filename}"
            self.root.after(0, self.finish_search, results, msg)
        except Exception as e:
            self.root.after(0, self.finish_search, [], f"Error: {str(e)}")

    def finish_search(self, results, status_msg):
        self.progress.stop()
        self.is_searching = False
        self.btn_search.config(state="normal")
        self.status_var.set(status_msg)

        self.results_area.config(state='normal')
        if not results and "Error" not in status_msg:
            self.results_area.insert(tk.END, "No results found.")
        else:
            for i, item in enumerate(results, 1):
                self.results_area.insert(tk.END, f"#{i} ", "header")
                self.results_area.insert(tk.END, f"[{item.get('source')}]\n", "source")
                self.results_area.insert(tk.END, f"Title: {item.get('title')}\n")
                self.results_area.insert(tk.END, f"Journal: {item.get('journal')} ({item.get('year')})\n")
                self.results_area.insert(tk.END, f"Authors: {item.get('authors')}\n")
                self.results_area.insert(tk.END, "-"*60 + "\n\n")
        
        self.results_area.config(state='disabled')
        if "Saved" in status_msg:
            messagebox.showinfo("Search Complete", status_msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = PubMedApp(root)
    root.mainloop()