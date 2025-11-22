import tkinter as tk
from tkinter import ttk, messagebox
import requests

class ProductsView:
    def __init__(self, parent):
        self.parent = parent
        self.API_URL = "http://127.0.0.1:8000"
        
        # Store all data here to filter locally
        self.all_products = [] 
        
        self.frame = tk.Frame(parent, bg="#f3f4f6")
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.setup_header()
        self.setup_search_and_filter()
        self.setup_table()
        
        self.load_products()

    def setup_header(self):
        header_frame = tk.Frame(self.frame, bg="#f3f4f6")
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(header_frame, text="Product Inventory", font=("Helvetica", 20, "bold"), fg="#111827", bg="#f3f4f6").pack(side="left")
        
        btn_add = tk.Button(header_frame, text="+ Add Product", font=("Helvetica", 10, "bold"), 
                            bg="#000000", fg="white", activebackground="#333333", activeforeground="white",
                            relief="flat", cursor="hand2", padx=15, pady=8,
                            command=self.open_add_product_window)
        btn_add.pack(side="right")

    def setup_search_and_filter(self):
        bar_frame = tk.Frame(self.frame, bg="white", padx=15, pady=15)
        bar_frame.pack(fill="x", pady=(0, 20))
        
        # 1. Search Input
        tk.Label(bar_frame, text="Search:", font=("Helvetica", 10, "bold"), bg="white", fg="#374151").pack(side="left", padx=(0, 5))
        self.entry_search = tk.Entry(bar_frame, font=("Helvetica", 10), width=30, relief="solid", bd=1)
        self.entry_search.pack(side="left", ipady=4)
        self.entry_search.bind("<Return>", lambda e: self.perform_search())

        # 2. Category Filter
        tk.Label(bar_frame, text="Category:", font=("Helvetica", 10, "bold"), bg="white", fg="#374151").pack(side="left", padx=(20, 5))
        self.filter_category = ttk.Combobox(bar_frame, font=("Helvetica", 10), width=20, state="readonly")
        self.filter_category.set("All Categories")
        self.filter_category.pack(side="left", ipady=4)
        self.filter_category.bind("<<ComboboxSelected>>", lambda e: self.perform_search())

        # 3. Action Buttons
        btn_search = tk.Button(bar_frame, text="Apply Filters", font=("Helvetica", 9, "bold"), 
                               bg="#f3f4f6", fg="#374151", relief="flat", cursor="hand2", padx=10,
                               command=self.perform_search)
        btn_search.pack(side="left", padx=15)

        btn_reset = tk.Button(bar_frame, text="Reset", font=("Helvetica", 9), 
                               bg="#ef4444", fg="white", relief="flat", cursor="hand2", padx=10,
                               command=self.reset_filters)
        btn_reset.pack(side="left")

    def setup_table(self):
        table_frame = tk.Frame(self.frame, bg="white")
        table_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Added 'price' to columns
        columns = ("id", "name", "sku", "category", "uom", "price", "stock", "action")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", yscrollcommand=scrollbar.set, selectmode="browse")
        
        scrollbar.config(command=self.tree.yview)
        
        self.tree.heading("id", text="ID", anchor="center")
        self.tree.heading("name", text="Product Name", anchor="w")
        self.tree.heading("sku", text="SKU / Code", anchor="w")
        self.tree.heading("category", text="Category", anchor="center")
        self.tree.heading("uom", text="Unit", anchor="center")
        self.tree.heading("price", text="Price (₹)", anchor="e")
        self.tree.heading("stock", text="Stock", anchor="center")
        self.tree.heading("action", text="Status", anchor="center")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("name", width=200, anchor="w")
        self.tree.column("sku", width=100, anchor="w")
        self.tree.column("category", width=120, anchor="center")
        self.tree.column("uom", width=80, anchor="center")
        self.tree.column("price", width=100, anchor="e")
        self.tree.column("stock", width=80, anchor="center")
        self.tree.column("action", width=100, anchor="center")
        
        self.tree.pack(fill="both", expand=True)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=("Helvetica", 10), rowheight=30, background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"), background="#f3f4f6", foreground="#374151")
        style.map("Treeview", background=[('selected', '#3b82f6')])

    def load_products(self):
        try:
            response = requests.get(f"{self.API_URL}/products")
            if response.status_code == 200:
                self.all_products = response.json()
                self.populate_tree(self.all_products)
                self.update_category_dropdown()
            else:
                print("Failed to fetch products")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Error", "Cannot connect to server.")

    def populate_tree(self, products_list):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for p in products_list:
            status = "Active"
            if p['stock'] == 0: status = "Out of Stock"
            elif p['stock'] < 10: status = "Low Stock"
            
            self.tree.insert("", "end", values=(
                p['id'], p['name'], p['sku'], p['category'], p['uom'], 
                f"₹{p.get('price', 0)}", # Handle price
                p['stock'], status
            ))

    def update_category_dropdown(self):
        categories = set(p['category'] for p in self.all_products)
        sorted_cats = sorted(list(categories))
        self.filter_category['values'] = ["All Categories"] + sorted_cats

    def perform_search(self):
        query = self.entry_search.get().lower().strip()
        selected_cat = self.filter_category.get()
        
        filtered_list = []
        for p in self.all_products:
            text_match = (query in p['name'].lower()) or (query in p['sku'].lower())
            cat_match = (selected_cat == "All Categories") or (p['category'] == selected_cat)
            
            if text_match and cat_match:
                filtered_list.append(p)
        
        self.populate_tree(filtered_list)

    def reset_filters(self):
        self.entry_search.delete(0, tk.END)
        self.filter_category.set("All Categories")
        self.populate_tree(self.all_products)

    def open_add_product_window(self):
        self.modal = tk.Toplevel(self.frame)
        self.modal.title("Add New Product")
        self.modal.geometry("450x600")
        self.modal.resizable(False, False)
        self.modal.configure(bg="white")
        self.modal.grab_set()

        x = self.parent.winfo_rootx() + (self.parent.winfo_width() // 2) - (450 // 2)
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() // 2) - (600 // 2)
        self.modal.geometry(f"+{x}+{y}")

        tk.Label(self.modal, text="New Product Details", font=("Helvetica", 16, "bold"), bg="white", fg="#111827").pack(pady=20)

        form_frame = tk.Frame(self.modal, bg="white", padx=30)
        form_frame.pack(fill="both", expand=True)

        # Form Fields
        tk.Label(form_frame, text="Product Name *", font=("Helvetica", 10, "bold"), bg="white", fg="#374151").pack(anchor="w", pady=(5, 2))
        self.entry_name = tk.Entry(form_frame, font=("Helvetica", 10), relief="solid", bd=1)
        self.entry_name.pack(fill="x", ipady=4, pady=(0, 10))

        tk.Label(form_frame, text="SKU / Code *", font=("Helvetica", 10, "bold"), bg="white", fg="#374151").pack(anchor="w", pady=(5, 2))
        self.entry_sku = tk.Entry(form_frame, font=("Helvetica", 10), relief="solid", bd=1)
        self.entry_sku.pack(fill="x", ipady=4, pady=(0, 10))

        tk.Label(form_frame, text="Category *", font=("Helvetica", 10, "bold"), bg="white", fg="#374151").pack(anchor="w", pady=(5, 2))
        self.combo_category = ttk.Combobox(form_frame, font=("Helvetica", 10), values=["Electronics", "Furniture", "Stationery", "Raw Material", "Groceries"])
        self.combo_category.pack(fill="x", ipady=4, pady=(0, 10))

        tk.Label(form_frame, text="Unit of Measure (UOM) *", font=("Helvetica", 10, "bold"), bg="white", fg="#374151").pack(anchor="w", pady=(5, 2))
        self.combo_uom = ttk.Combobox(form_frame, font=("Helvetica", 10), values=["pcs", "box", "kg", "ltr", "meter", "dozen"])
        self.combo_uom.pack(fill="x", ipady=4, pady=(0, 10))

        # Added Price Field
        tk.Label(form_frame, text="Price per Unit *", font=("Helvetica", 10, "bold"), bg="white", fg="#374151").pack(anchor="w", pady=(5, 2))
        self.entry_price = tk.Entry(form_frame, font=("Helvetica", 10), relief="solid", bd=1)
        self.entry_price.pack(fill="x", ipady=4, pady=(0, 10))

        tk.Label(form_frame, text="Initial Stock *", font=("Helvetica", 10, "bold"), bg="white", fg="#374151").pack(anchor="w", pady=(5, 2))
        self.entry_stock = tk.Entry(form_frame, font=("Helvetica", 10), relief="solid", bd=1)
        self.entry_stock.pack(fill="x", ipady=4, pady=(0, 20))

        btn_save = tk.Button(self.modal, text="Save Product", font=("Helvetica", 11, "bold"), 
                             bg="#000000", fg="white", activebackground="#333333", activeforeground="white",
                             relief="flat", cursor="hand2",
                             command=self.save_product)
        btn_save.pack(fill="x", padx=30, ipady=10, pady=20)

    def save_product(self):
        name = self.entry_name.get().strip()
        sku = self.entry_sku.get().strip()
        category = self.combo_category.get().strip()
        uom = self.combo_uom.get().strip()
        price_str = self.entry_price.get().strip()
        stock_str = self.entry_stock.get().strip()

        if not name or not sku or not category or not uom or not stock_str or not price_str:
            messagebox.showwarning("Missing Info", "Please fill all fields marked with *")
            return
        
        try:
            stock = int(stock_str)
            price = float(price_str)
            if stock < 0 or price < 0: raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Stock must be integer and Price must be number.")
            return

        payload = {"name": name, "sku": sku, "category": category, "uom": uom, "stock": stock, "price": price}

        try:
            response = requests.post(f"{self.API_URL}/products", json=payload)
            if response.status_code == 200:
                messagebox.showinfo("Success", "Product Added Successfully!")
                self.modal.destroy()
                self.load_products()
            else:
                error_msg = response.json().get("detail", "Failed to add product")
                messagebox.showerror("Error", error_msg)
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Cannot connect to server.")