import tkinter as tk

class SettingsView:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg="white", padx=20, pady=20)
        self.frame.pack(fill="both", expand=True)
        
        tk.Label(self.frame, text="Settings", font=("Helvetica", 24, "bold"), fg="#111827", bg="white").pack(anchor="w")
        tk.Label(self.frame, text="Configure application preferences.", font=("Helvetica", 12), fg="#6b7280", bg="white").pack(anchor="w", pady=(5, 20))