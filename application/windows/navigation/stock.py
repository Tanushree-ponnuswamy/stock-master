import tkinter as tk
from tkinter import ttk, messagebox
import requests
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class StockView:
    def __init__(self, parent):
        self.parent = parent
        self.API_URL = "http://127.0.0.1:8000"
        self.all_products = []

        self.frame = tk.Frame(parent, bg="#f3f4f6")
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.setup_header()
        self.setup_kpi_cards()
        self.setup_charts_section()
        
        self.load_stock_data()

    def setup_header(self):
        header_frame = tk.Frame(self.frame, bg="#f3f4f6")
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(header_frame, text="Stock Analytics", font=("Helvetica", 20, "bold"), fg="#111827", bg="#f3f4f6").pack(side="left")
        
        btn_remove = tk.Button(header_frame, text="⚠ Remove Stock / Write-off", font=("Helvetica", 10, "bold"), 
                               bg="#ef4444", fg="white", activebackground="#b91c1c", activeforeground="white",
                               relief="flat", cursor="hand2", padx=15, pady=8,
                               command=self.open_remove_stock_modal)
        btn_remove.pack(side="right", padx=(10, 0))

        btn_details = tk.Button(header_frame, text="📋 Removal Details", font=("Helvetica", 10, "bold"), 
                                bg="#374151", fg="white", activebackground="#1f2937", activeforeground="white",
                                relief="flat", cursor="hand2", padx=15, pady=8,
                                command=self.open_removal_log)
        btn_details.pack(side="right")

    def setup_kpi_cards(self):
        kpi_frame = tk.Frame(self.frame, bg="#f3f4f6")
        kpi_frame.pack(fill="x", pady=(0, 20))
        
        self.create_kpi(kpi_frame, "Total Stock Value", "₹0.00", "#2563eb", 0)
        self.create_kpi(kpi_frame, "Low Stock Items", "0", "#f59e0b", 1)
        self.create_kpi(kpi_frame, "Out of Stock", "0", "#ef4444", 2)

    def create_kpi(self, parent, title, value, color, col):
        card = tk.Frame(parent, bg="white", padx=20, pady=15, relief="flat")
        card.grid(row=0, column=col, sticky="ew", padx=10)
        parent.grid_columnconfigure(col, weight=1)
        
        tk.Label(card, text=title, font=("Helvetica", 10, "bold"), fg="#6b7280", bg="white").pack(anchor="w")
        lbl_val = tk.Label(card, text=value, font=("Helvetica", 20, "bold"), fg=color, bg="white")
        lbl_val.pack(anchor="w")
        
        setattr(self, f"lbl_kpi_{col}", lbl_val)

    def setup_charts_section(self):
        chart_frame = tk.Frame(self.frame, bg="#f3f4f6")
        chart_frame.pack(fill="both", expand=True, pady=(0, 20)) # Changed to expand to fill empty space
        
        self.frame_chart_left = tk.Frame(chart_frame, bg="white")
        self.frame_chart_left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.frame_chart_right = tk.Frame(chart_frame, bg="white")
        self.frame_chart_right.pack(side="left", fill="both", expand=True, padx=(10, 0))

    def load_stock_data(self):
        try:
            res = requests.get(f"{self.API_URL}/products")
            if res.status_code == 200:
                self.all_products = res.json()
                self.update_kpis()
                self.update_charts()
            else:
                print("Failed to fetch stock data")
        except:
            pass

    def update_kpis(self):
        total_val = sum(p['stock'] * (p.get('price') or 0) for p in self.all_products)
        low_stock = sum(1 for p in self.all_products if 0 < p['stock'] < 10)
        out_stock = sum(1 for p in self.all_products if p['stock'] == 0)
        
        self.lbl_kpi_0.config(text=f"₹{total_val:,.2f}")
        self.lbl_kpi_1.config(text=f"{low_stock} Items")
        self.lbl_kpi_2.config(text=f"{out_stock} Items")

    def update_charts(self):
        for widget in self.frame_chart_left.winfo_children(): widget.destroy()
        for widget in self.frame_chart_right.winfo_children(): widget.destroy()

        if not self.all_products: return

        cat_counts = {}
        for p in self.all_products:
            cat = p['category']
            cat_counts[cat] = cat_counts.get(cat, 0) + p['stock']
            
        fig1 = Figure(figsize=(4, 4), dpi=100) # Slightly taller
        ax1 = fig1.add_subplot(111)
        ax1.bar(cat_counts.keys(), cat_counts.values(), color='#3b82f6')
        ax1.set_title("Total Stock by Category", fontsize=10)
        ax1.tick_params(axis='x', rotation=45, labelsize=8)
        
        canvas1 = FigureCanvasTkAgg(fig1, self.frame_chart_left)
        canvas1.get_tk_widget().pack(fill="both", expand=True)

        low = sum(1 for p in self.all_products if 0 < p['stock'] < 10)
        out = sum(1 for p in self.all_products if p['stock'] == 0)
        ok = len(self.all_products) - low - out
        
        if len(self.all_products) > 0:
            fig2 = Figure(figsize=(4, 4), dpi=100) # Slightly taller
            ax2 = fig2.add_subplot(111)
            labels = ['Active', 'Low', 'Out']
            sizes = [ok, low, out]
            colors = ['#10b981', '#f59e0b', '#ef4444']
            
            final_labels = [l for l, s in zip(labels, sizes) if s > 0]
            final_sizes = [s for s in sizes if s > 0]
            final_colors = [c for c, s in zip(colors, sizes) if s > 0]

            if final_sizes:
                ax2.pie(final_sizes, labels=final_labels, colors=final_colors, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 8})
                ax2.set_title("Stock Health", fontsize=10)
            
            canvas2 = FigureCanvasTkAgg(fig2, self.frame_chart_right)
            canvas2.get_tk_widget().pack(fill="both", expand=True)

    def open_removal_log(self):
        log_win = tk.Toplevel(self.frame)
        log_win.title("Stock Removal / Write-off History")
        log_win.geometry("800x500")
        log_win.configure(bg="white")

        tk.Label(log_win, text="Stock Write-off Log", font=("Helvetica", 16, "bold"), fg="#111827", bg="white").pack(pady=15)

        table_frame = tk.Frame(log_win, bg="white", padx=20, pady=10)
        table_frame.pack(fill="both", expand=True)

        columns = ("date", "sku", "name", "qty", "val", "reason")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        tree.heading("date", text="Date"); tree.column("date", width=120)
        tree.heading("sku", text="SKU"); tree.column("sku", width=80)
        tree.heading("name", text="Product"); tree.column("name", width=200)
        tree.heading("qty", text="Qty Removed"); tree.column("qty", width=100, anchor="center")
        tree.heading("val", text="Loss Value"); tree.column("val", width=100, anchor="e")
        tree.heading("reason", text="Reason"); tree.column("reason", width=150)
        
        tree.pack(fill="both", expand=True)

        try:
            res = requests.get(f"{self.API_URL}/stock-moves")
            if res.status_code == 200:
                moves = res.json()
                # Filter for moves where location contains "Write-off"
                removals = [m for m in moves if m['location'] and "Write-off" in m['location']]
                
                for m in removals:
                    clean_date = m['created_at'][:16].replace("T", " ")
                    reason = m['location'].replace("Write-off: ", "") # Extract reason
                    
                    tree.insert("", "end", values=(
                        clean_date, m['sku'], m['product_name'], 
                        f"-{m['quantity']}", f"₹{m['total_value']}", reason
                    ))
        except:
            messagebox.showerror("Error", "Could not fetch log")


    def open_remove_stock_modal(self):
        self.modal = tk.Toplevel(self.frame)
        self.modal.title("Remove Stock / Write-off")
        self.modal.geometry("500x600")
        self.modal.configure(bg="white")
        self.modal.grab_set()

        tk.Label(self.modal, text="Manual Stock Removal", font=("Helvetica", 16, "bold"), bg="white", fg="#ef4444").pack(pady=20)
        tk.Label(self.modal, text="Use this for damage, expiry, or theft adjustment.", font=("Helvetica", 10), bg="white", fg="#6b7280").pack()

        form_frame = tk.Frame(self.modal, bg="white", padx=40, pady=20)
        form_frame.pack(fill="both", expand=True)

        tk.Label(form_frame, text="SKU Code (Enter to Fetch) *", font=("Helvetica", 10, "bold"), bg="white").pack(anchor="w")
        self.entry_r_sku = tk.Entry(form_frame, font=("Helvetica", 11), bg="#f9fafb", relief="solid", bd=1)
        self.entry_r_sku.pack(fill="x", ipady=5, pady=(5, 15))
        self.entry_r_sku.bind("<Return>", self.fetch_product_for_removal)

        tk.Label(form_frame, text="Product Name", font=("Helvetica", 9), bg="white", fg="#6b7280").pack(anchor="w")
        self.entry_r_name = tk.Entry(form_frame, bg="#f3f4f6", state="disabled")
        self.entry_r_name.pack(fill="x", ipady=5, pady=(0, 10))

        tk.Label(form_frame, text="Current Stock", font=("Helvetica", 9), bg="white", fg="#6b7280").pack(anchor="w")
        self.entry_r_curr = tk.Entry(form_frame, bg="#f3f4f6", state="disabled")
        self.entry_r_curr.pack(fill="x", ipady=5, pady=(0, 15))

        tk.Label(form_frame, text="Quantity to Remove *", font=("Helvetica", 10, "bold"), bg="white").pack(anchor="w")
        self.entry_r_qty = tk.Entry(form_frame, font=("Helvetica", 11), relief="solid", bd=1)
        self.entry_r_qty.pack(fill="x", ipady=5, pady=(5, 15))

        tk.Label(form_frame, text="Reason for Removal *", font=("Helvetica", 10, "bold"), bg="white").pack(anchor="w")
        self.combo_reason = ttk.Combobox(form_frame, values=["Damaged", "Expired", "Lost/Theft", "Internal Use", "Other"])
        self.combo_reason.pack(fill="x", ipady=5, pady=(5, 20))

        btn_submit = tk.Button(self.modal, text="Confirm Removal", font=("Helvetica", 11, "bold"), 
                               bg="#ef4444", fg="white", relief="flat", cursor="hand2", pady=10,
                               command=self.submit_removal)
        btn_submit.pack(fill="x", padx=40, pady=20)

    def fetch_product_for_removal(self, event):
        sku = self.entry_r_sku.get().strip()
        try:
            res = requests.get(f"{self.API_URL}/products/sku/{sku}")
            if res.status_code == 200:
                data = res.json()
                self.set_entry(self.entry_r_name, data['name'])
                self.set_entry(self.entry_r_curr, str(data['stock']))
                self.entry_r_qty.focus()
            else:
                messagebox.showwarning("Not Found", "SKU not found")
        except: pass

    def submit_removal(self):
        sku = self.entry_r_sku.get()
        qty_str = self.entry_r_qty.get()
        reason = self.combo_reason.get()
        
        if not sku or not qty_str or not reason:
            messagebox.showwarning("Error", "Fill all fields")
            return
            
        try:
            qty = int(qty_str)
            current_stock = int(self.entry_r_curr.get())
            if qty > current_stock:
                messagebox.showerror("Error", "Cannot remove more than current stock")
                return
                
            payload = {
                "sku": sku,
                "move_type": "OUT",
                "quantity": qty,
                "location": f"Write-off: {reason}" # Special tag for filtering
            }
            
            res = requests.post(f"{self.API_URL}/stock-moves", json=payload)
            if res.status_code == 200:
                messagebox.showinfo("Success", "Stock Removed Successfully")
                self.modal.destroy()
                self.load_stock_data()
            else:
                messagebox.showerror("Error", "Failed to remove stock")
        except:
            messagebox.showerror("Error", "Invalid input")

    def set_entry(self, entry, text):
        entry.config(state="normal")
        entry.delete(0, tk.END)
        entry.insert(0, text)
        entry.config(state="disabled")