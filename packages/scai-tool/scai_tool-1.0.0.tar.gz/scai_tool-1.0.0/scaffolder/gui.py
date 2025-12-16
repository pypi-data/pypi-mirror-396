import tkinter as tk
from tkinter import messagebox, filedialog
import os
from .core import parse_tree, execute_actions

class ScaffoldApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Scaffolder")
        self.root.geometry("900x600")
        
        # Grid config
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)

        # Instructions
        tk.Label(root, text="Paste AI Tree Output below, then generate.", font=("Arial", 10)).grid(row=0, column=0, columnspan=2, pady=5)

        # Input
        self.input_frame = tk.Frame(root)
        self.input_frame.grid(row=1, column=0, sticky="nsew", padx=5)
        tk.Label(self.input_frame, text="Input Tree:").pack(anchor="w")
        self.txt_input = tk.Text(self.input_frame, height=20, width=40)
        self.txt_input.pack(fill="both", expand=True)

        # Output
        self.output_frame = tk.Frame(root)
        self.output_frame.grid(row=1, column=1, sticky="nsew", padx=5)
        tk.Label(self.output_frame, text="Log:").pack(anchor="w")
        self.txt_log = tk.Text(self.output_frame, height=20, width=40, bg="#f0f0f0")
        self.txt_log.pack(fill="both", expand=True)

        # Controls
        ctrl_frame = tk.Frame(root, pady=10)
        ctrl_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

        # Path
        tk.Label(ctrl_frame, text="Target:").pack(side="left", padx=5)
        self.var_path = tk.StringVar(value=os.getcwd())
        tk.Entry(ctrl_frame, textvariable=self.var_path, width=40).pack(side="left", padx=5)
        tk.Button(ctrl_frame, text="Browse", command=self.browse).pack(side="left")

        # Buttons
        tk.Button(ctrl_frame, text="Generate", bg="#4caf50", fg="white", command=self.run_gen).pack(side="right", padx=10)
        tk.Button(ctrl_frame, text="Preview", command=self.run_preview).pack(side="right", padx=5)
        tk.Button(ctrl_frame, text="Clear Log", command=self.clear_log).pack(side="right", padx=5)

    def browse(self):
        d = filedialog.askdirectory()
        if d: self.var_path.set(d)

    def log(self, msg):
        self.txt_log.insert(tk.END, msg + "\n")
        self.txt_log.see(tk.END)
        
    def clear_log(self):
        self.txt_log.delete("1.0", tk.END)

    def run_preview(self):
        self.clear_log()
        text = self.txt_input.get("1.0", tk.END)
        actions = parse_tree(text, self.var_path.get())
        if not actions:
            self.log("No structure found.")
            return
        
        self.log(f"--- PREVIEW ({len(actions)} items) ---")
        for msg in execute_actions(actions, dry_run=True):
            self.log(msg)

    def run_gen(self):
        self.clear_log()
        text = self.txt_input.get("1.0", tk.END)
        actions = parse_tree(text, self.var_path.get())
        if not actions:
            messagebox.showerror("Error", "No structure found")
            return
        
        self.log("--- GENERATING ---")
        for msg in execute_actions(actions, dry_run=False):
            self.log(msg)
        messagebox.showinfo("Done", "Generation Complete")

def run_gui():
    root = tk.Tk()
    app = ScaffoldApp(root)
    root.mainloop()