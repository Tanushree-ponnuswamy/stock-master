import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime

class HistoryView:
    def __init__(self, parent):
        self.parent = parent
        self.API_URL = "http://127.0.0.1:8000"
        self.all_moves = []
        
        # List to hold items before submitting
        self.transaction_items = [] 

        self.frame = tk.Frame(parent, bg="#f3f4f6")
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.setup_header()
        self.setup_table()
        self.load_history()

    def setup_header(self):
        header_frame = tk.Frame(self.frame, bg="#f3f4f6")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Title
        tk.Label(header_frame, text="Movement History", font=("Helvetica", 20, "bold"), fg="#111827", bg="#f3f4f6").pack(side="left")
        
        # --- THE ADD BUTTON ---
        btn_add = tk.Button(header_frame, text="+ Record Movement", font=("Helvetica", 10, "bold"), 
                            bg="black", fg="white", relief="flat", cursor="hand2", padx=15, pady=8,
                            command=self.open_add_move_window)
        btn_add.pack(side="right")

    def setup_table(self):
        table_frame = tk.Frame(self.frame, bg="white")
        table_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")

        columns = ("date", "sku", "name", "type", "loc", "qty", "total")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse", yscrollcommand=scrollbar.set)
        
        scrollbar.config(command=self.tree.yview)

        self.tree.heading("date", text="Date")
        self.tree.heading("sku", text="SKU")
        self.tree.heading("name", text="Product")
        self.tree.heading("type", text="Type")
        self.tree.heading("loc", text="Location")
        self.tree.heading("qty", text="Qty")
        self.tree.heading("total", text="Total Val")
        
        self.tree.column("date", width=140)
        self.tree.column("sku", width=100)
        self.tree.column("name", width=200)
        self.tree.column("type", width=60, anchor="center")
        self.tree.column("loc", width=100)
        self.tree.column("qty", width=60, anchor="center")
        self.tree.column("total", width=100, anchor="e")

        self.tree.pack(fill="both", expand=True)
        
        # Configure Colors
        self.tree.tag_configure("IN", foreground="#166534")  # Green
        self.tree.tag_configure("OUT", foreground="#991b1b") # Red

    def load_history(self):
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            response = requests.get(f"{self.API_URL}/stock-moves")
            if response.status_code == 200:
                for m in response.json():
                    tag = "IN" if m['move_type'] == "IN" else "OUT"
                    
                    # Format Date
                    clean_date = m['created_at'][:16].replace("T", " ")
                    
                    self.tree.insert("", "end", values=(
                        clean_date,
                        m['sku'],
                        m['product_name'],
                        m['move_type'],
                        m['location'],
                        m['quantity'],
                        f"₹{m['total_value']}"
                    ), tags=(tag,))
        except requests.exceptions.ConnectionError:
            print("Connection Error")

    # --- TRANSACTION MODAL ---
    def open_add_move_window(self):
        self.modal = tk.Toplevel(self.frame)
        self.modal.title("Record Stock Movement")
        self.modal.geometry("900x600")
        self.modal.configure(bg="white")
        self.modal.grab_set()
        
        # Reset transaction list
        self.transaction_items = []

        # 1. Header (Type & Location)
        top_frame = tk.Frame(self.modal, bg="#f9fafb", padx=20, pady=20)
        top_frame.pack(fill="x")

        tk.Label(top_frame, text="Movement Type:", bg="#f9fafb", font=("Helvetica", 10, "bold")).grid(row=0, column=0, padx=5)
        self.combo_type = ttk.Combobox(top_frame, values=["IN", "OUT"], state="readonly", width=10)
        self.combo_type.grid(row=0, column=1, padx=5)
        self.combo_type.set("IN")
        self.combo_type.bind("<<ComboboxSelected>>", self.update_location_label)

        self.lbl_location = tk.Label(top_frame, text="From Location:", bg="#f9fafb", font=("Helvetica", 10, "bold"))
        self.lbl_location.grid(row=0, column=2, padx=(20, 5))
        self.entry_location = tk.Entry(top_frame, width=30, relief="solid", bd=1)
        self.entry_location.grid(row=0, column=3, padx=5)

        # 2. Item Entry Area
        entry_frame = tk.Frame(self.modal, bg="white", padx=20, pady=10)
        entry_frame.pack(fill="x")

        # SKU Input
        tk.Label(entry_frame, text="SKU (Hit Enter):", bg="white", font=("Helvetica", 9)).grid(row=0, column=0, sticky="w")
        self.entry_sku = tk.Entry(entry_frame, width=15, bg="#eff6ff", relief="solid", bd=1)
        self.entry_sku.grid(row=1, column=0, padx=5, pady=5)
        self.entry_sku.bind("<Return>", self.fetch_product_details)

        # Auto-Filled Name
        tk.Label(entry_frame, text="Product Name:", bg="white", font=("Helvetica", 9)).grid(row=0, column=1, sticky="w")
        self.lbl_prod_name = tk.Entry(entry_frame, width=25, bg="#f3f4f6", state="disabled", disabledforeground="black")
        self.lbl_prod_name.grid(row=1, column=1, padx=5)

        # Auto-Filled Price
        tk.Label(entry_frame, text="Price:", bg="white", font=("Helvetica", 9)).grid(row=0, column=2, sticky="w")
        self.lbl_prod_price = tk.Entry(entry_frame, width=10, bg="#f3f4f6", state="disabled", disabledforeground="black")
        self.lbl_prod_price.grid(row=1, column=2, padx=5)

        # Qty Input
        tk.Label(entry_frame, text="Quantity:", bg="white", font=("Helvetica", 9)).grid(row=0, column=3, sticky="w")
        self.entry_qty = tk.Entry(entry_frame, width=10, relief="solid", bd=1)
        self.entry_qty.grid(row=1, column=3, padx=5)
        self.entry_qty.bind("<KeyRelease>", self.calc_line_total)

        # Calculated Total
        tk.Label(entry_frame, text="Total:", bg="white", font=("Helvetica", 9)).grid(row=0, column=4, sticky="w")
        self.lbl_line_total = tk.Entry(entry_frame, width=12, bg="#f3f4f6", state="disabled", disabledforeground="black")
        self.lbl_line_total.grid(row=1, column=4, padx=5)

        # Add Button
        btn_add_line = tk.Button(entry_frame, text="Add to List", bg="black", fg="white", command=self.add_item_to_list)
        btn_add_line.grid(row=1, column=5, padx=15)

        # 3. List of Items (Treeview)
        list_frame = tk.Frame(self.modal, bg="white", padx=20)
        list_frame.pack(fill="both", expand=True)
        
        cols = ("sku", "name", "price", "qty", "total")
        self.move_tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=8)
        self.move_tree.heading("sku", text="SKU"); self.move_tree.column("sku", width=80)
        self.move_tree.heading("name", text="Name"); self.move_tree.column("name", width=200)
        self.move_tree.heading("price", text="Price"); self.move_tree.column("price", width=80)
        self.move_tree.heading("qty", text="Qty"); self.move_tree.column("qty", width=60)
        self.move_tree.heading("total", text="Total"); self.move_tree.column("total", width=80)
        self.move_tree.pack(fill="both", expand=True)

        # 4. Footer (Submit)
        footer_frame = tk.Frame(self.modal, bg="#f9fafb", height=60)
        footer_frame.pack(fill="x", side="bottom")
        
        btn_submit = tk.Button(footer_frame, text="Submit Transaction", bg="#166534", fg="white", font=("Helvetica", 12, "bold"), 
                               padx=20, pady=10, command=self.submit_transaction)
        btn_submit.pack(pady=10)

    def update_location_label(self, event):
        val = self.combo_type.get()
        if val == "IN": self.lbl_location.config(text="From Location (Supplier):")
        else: self.lbl_location.config(text="To Location (Customer):")

    def fetch_product_details(self, event):
        sku = self.entry_sku.get().strip()
        if not sku: return
        try:
            res = requests.get(f"{self.API_URL}/products/sku/{sku}")
            if res.status_code == 200:
                data = res.json()
                self.set_entry(self.lbl_prod_name, data['name'])
                self.set_entry(self.lbl_prod_price, str(data['price']))
                self.entry_qty.focus()
            else:
                messagebox.showwarning("Not Found", "SKU not found")
                self.set_entry(self.lbl_prod_name, "")
                self.set_entry(self.lbl_prod_price, "")
        except: pass

    def calc_line_total(self, event):
        try:
            p = float(self.lbl_prod_price.get())
            q = int(self.entry_qty.get())
            self.set_entry(self.lbl_line_total, f"{p*q:.2f}")
        except:
            self.set_entry(self.lbl_line_total, "0.00")

    def add_item_to_list(self):
        sku = self.entry_sku.get()
        name = self.lbl_prod_name.get()
        qty = self.entry_qty.get()
        
        if not name or not qty: return

        # Add to internal list
        self.transaction_items.append({
            "sku": sku,
            "quantity": int(qty)
        })
        
        # Add to UI Tree
        total = self.lbl_line_total.get()
        price = self.lbl_prod_price.get()
        self.move_tree.insert("", "end", values=(sku, name, price, qty, total))
        
        # Clear inputs
        self.entry_sku.delete(0, tk.END)
        self.set_entry(self.lbl_prod_name, "")
        self.set_entry(self.lbl_prod_price, "")
        self.entry_qty.delete(0, tk.END)
        self.set_entry(self.lbl_line_total, "")
        self.entry_sku.focus()

    def submit_transaction(self):
        if not self.transaction_items:
            messagebox.showwarning("Empty", "No items in list")
            return

        move_type = self.combo_type.get()
        location = self.entry_location.get()

        success_count = 0
        for item in self.transaction_items:
            payload = {
                "sku": item['sku'],
                "move_type": move_type,
                "quantity": item['quantity'],
                "location": location
            }
            try:
                res = requests.post(f"{self.API_URL}/stock-moves", json=payload)
                if res.status_code == 200: success_count += 1
            except: pass
        
        if success_count == len(self.transaction_items):
            messagebox.showinfo("Success", "Transaction Saved!")
            self.modal.destroy()
            self.load_history()
        else:
            messagebox.showerror("Error", f"Only {success_count} items saved.")

    def set_entry(self, entry, text):
        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, text)
        entry.config(state="disabled")