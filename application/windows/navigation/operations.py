import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
from datetime import datetime
import os

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    HAS_PDF_LIB = True
except ImportError:
    HAS_PDF_LIB = False

class OperationsView:
    def __init__(self, parent):
        self.parent = parent
        self.API_URL = "http://127.0.0.1:8000"
        self.transaction_items = [] 
        
        self.frame = tk.Frame(parent, bg="#f3f4f6")
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.setup_header()
        self.setup_operation_hub()
        self.setup_receipts_hub()
        self.setup_recent_activity()
        
        self.load_recent_activity()

    def setup_header(self):
        header_frame = tk.Frame(self.frame, bg="#f3f4f6")
        header_frame.pack(fill="x", pady=(0, 20))
        tk.Label(header_frame, text="Operations Hub", font=("Helvetica", 20, "bold"), fg="#111827", bg="#f3f4f6").pack(side="left")

    def setup_operation_hub(self):
        hub_frame = tk.Frame(self.frame, bg="#f3f4f6")
        hub_frame.pack(fill="x", pady=(0, 20))
        
        # INBOUND
        frame_in = tk.Frame(hub_frame, bg="white", padx=20, pady=20, relief="flat")
        frame_in.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(frame_in, text="↓ INBOUND", font=("Helvetica", 12, "bold"), fg="#166534", bg="white").pack(anchor="w")
        tk.Label(frame_in, text="Receive Goods / Purchases", font=("Helvetica", 10), fg="#6b7280", bg="white").pack(anchor="w", pady=(5, 15))
        
        btn_in = tk.Button(frame_in, text="+ Add New Incoming Stock", font=("Helvetica", 11, "bold"), bg="#166534", fg="white", relief="flat", cursor="hand2", pady=10, command=lambda: self.open_transaction_modal("IN"))
        btn_in.pack(fill="x", pady=(0, 10))
        btn_view_in = tk.Button(frame_in, text="View All Inbound Logs", font=("Helvetica", 10), bg="#dcfce7", fg="#166534", relief="flat", cursor="hand2", pady=5, command=lambda: self.open_history_modal("IN"))
        btn_view_in.pack(fill="x")

        # OUTBOUND
        frame_out = tk.Frame(hub_frame, bg="white", padx=20, pady=20, relief="flat")
        frame_out.pack(side="left", fill="both", expand=True, padx=(10, 0))
        tk.Label(frame_out, text="↑ OUTBOUND", font=("Helvetica", 12, "bold"), fg="#991b1b", bg="white").pack(anchor="w")
        tk.Label(frame_out, text="Dispatch Goods / Sales", font=("Helvetica", 10), fg="#6b7280", bg="white").pack(anchor="w", pady=(5, 15))
        
        btn_out = tk.Button(frame_out, text="- Add New Outgoing Stock", font=("Helvetica", 11, "bold"), bg="#991b1b", fg="white", relief="flat", cursor="hand2", pady=10, command=lambda: self.open_transaction_modal("OUT"))
        btn_out.pack(fill="x", pady=(0, 10))
        btn_view_out = tk.Button(frame_out, text="View All Outbound Logs", font=("Helvetica", 10), bg="#fee2e2", fg="#991b1b", relief="flat", cursor="hand2", pady=5, command=lambda: self.open_history_modal("OUT"))
        btn_view_out.pack(fill="x")

    def setup_receipts_hub(self):
        receipt_frame = tk.Frame(self.frame, bg="white", padx=20, pady=20)
        receipt_frame.pack(fill="x", pady=(0, 30))
        tk.Label(receipt_frame, text="📄 RECEIPTS & LOGS", font=("Helvetica", 12, "bold"), fg="#2563eb", bg="white").pack(anchor="w")
        tk.Label(receipt_frame, text="View transaction history, generate invoices, and print receipts.", font=("Helvetica", 10), fg="#6b7280", bg="white").pack(anchor="w", pady=(5, 15))
        
        # Updated Command
        btn_receipts = tk.Button(receipt_frame, text="Manage Receipts", font=("Helvetica", 11, "bold"), 
                                 bg="#2563eb", fg="white", activebackground="#1d4ed8", activeforeground="white",
                                 relief="flat", cursor="hand2", pady=10,
                                 command=self.open_receipts)
        btn_receipts.pack(fill="x")

    def setup_recent_activity(self):
        section_frame = tk.Frame(self.frame, bg="#f3f4f6")
        section_frame.pack(fill="both", expand=True)
        tk.Label(section_frame, text="Recent Activity (All)", font=("Helvetica", 14, "bold"), fg="#111827", bg="#f3f4f6").pack(anchor="w", pady=(0, 10))

        table_frame = tk.Frame(section_frame, bg="white")
        table_frame.pack(fill="both", expand=True)

        columns = ("date", "sku", "name", "type", "qty")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=5)
        self.tree.heading("date", text="Time"); self.tree.column("date", width=150)
        self.tree.heading("sku", text="SKU"); self.tree.column("sku", width=100)
        self.tree.heading("name", text="Product"); self.tree.column("name", width=250)
        self.tree.heading("type", text="Type"); self.tree.column("type", width=80, anchor="center")
        self.tree.heading("qty", text="Qty"); self.tree.column("qty", width=80, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.tag_configure("IN", foreground="#166534"); self.tree.tag_configure("OUT", foreground="#991b1b")

    def load_recent_activity(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        try:
            res = requests.get(f"{self.API_URL}/stock-moves")
            if res.status_code == 200:
                moves = res.json()
                for m in moves[:5]:
                    tag = "IN" if m['move_type'] == "IN" else "OUT"
                    clean_date = m['created_at'][:16].replace("T", " ")
                    self.tree.insert("", "end", values=(clean_date, m['sku'], m['product_name'], m['move_type'], m['quantity']), tags=(tag,))
        except: pass

    # --- NEW: RECEIPT MANAGER LOGIC ---
    def open_receipts(self):
        self.receipt_win = tk.Toplevel(self.frame)
        self.receipt_win.title("Receipt Manager")
        self.receipt_win.geometry("900x600")
        self.receipt_win.configure(bg="#f3f4f6")

        # Split Layout: Left (List) | Right (Details & Actions)
        paned = tk.PanedWindow(self.receipt_win, orient=tk.HORIZONTAL, bg="#f3f4f6")
        paned.pack(fill="both", expand=True, padx=10, pady=10)

        # --- LEFT PANE (List) ---
        left_frame = tk.Frame(paned, bg="white", width=400)
        paned.add(left_frame)
        
        tk.Label(left_frame, text="Transaction List", font=("Helvetica", 12, "bold"), bg="white", pady=10).pack(fill="x")
        
        # Treeview for List
        columns = ("id", "date", "type", "name")
        self.rec_tree = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="browse")
        self.rec_tree.heading("id", text="#"); self.rec_tree.column("id", width=40)
        self.rec_tree.heading("date", text="Date"); self.rec_tree.column("date", width=120)
        self.rec_tree.heading("type", text="Type"); self.rec_tree.column("type", width=60)
        self.rec_tree.heading("name", text="Product"); self.rec_tree.column("name", width=150)
        
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.rec_tree.yview)
        self.rec_tree.configure(yscrollcommand=scrollbar.set)
        
        self.rec_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.rec_tree.bind("<<TreeviewSelect>>", self.on_receipt_select)

        self.right_frame = tk.Frame(paned, bg="white", width=500, padx=30, pady=30)
        paned.add(self.right_frame)
        
        tk.Label(self.right_frame, text="Transaction Details", font=("Helvetica", 16, "bold"), bg="white", fg="#1f2937").pack(anchor="w", pady=(0, 20))
        
        self.lbl_r_id = tk.Label(self.right_frame, text="Select a transaction...", font=("Helvetica", 10), bg="white", fg="#6b7280", anchor="w")
        self.lbl_r_id.pack(fill="x", pady=2)
        
        self.lbl_r_prod = tk.Label(self.right_frame, text="", font=("Helvetica", 12, "bold"), bg="white", fg="#111827", anchor="w")
        self.lbl_r_prod.pack(fill="x", pady=(10, 2))
        
        self.lbl_r_meta = tk.Label(self.right_frame, text="", font=("Helvetica", 10), bg="white", anchor="w")
        self.lbl_r_meta.pack(fill="x", pady=2)
        
        self.lbl_r_price = tk.Label(self.right_frame, text="", font=("Helvetica", 10), bg="white", anchor="w")
        self.lbl_r_price.pack(fill="x", pady=2)
        
        self.lbl_r_total = tk.Label(self.right_frame, text="", font=("Helvetica", 18, "bold"), bg="white", fg="#166534", anchor="w")
        self.lbl_r_total.pack(fill="x", pady=(20, 30))
        
        self.btn_frame = tk.Frame(self.right_frame, bg="white")
        self.btn_frame.pack(fill="x")
        
        self.btn_view = tk.Button(self.btn_frame, text="👁 View Receipt", font=("Helvetica", 11), bg="#f3f4f6", fg="#1f2937", relief="flat", padx=20, pady=10, state="disabled",
                                  command=self.view_receipt_popup)
        self.btn_view.pack(side="left", padx=(0, 10))
        
        self.btn_dl = tk.Button(self.btn_frame, text="⬇ Download PDF", font=("Helvetica", 11, "bold"), bg="black", fg="white", relief="flat", padx=20, pady=10, state="disabled",
                                command=self.download_receipt_pdf)
        self.btn_dl.pack(side="left")

        self.load_receipts_list()

    def load_receipts_list(self):
        try:
            res = requests.get(f"{self.API_URL}/stock-moves")
            if res.status_code == 200:
                self.moves_data = res.json() # Store for details lookup
                for m in self.moves_data:
                    clean_date = m['created_at'][:10]
                    self.rec_tree.insert("", "end", iid=m['id'], values=(m['id'], clean_date, m['move_type'], m['product_name']))
        except: pass

    def on_receipt_select(self, event):
        selected = self.rec_tree.selection()
        if not selected: return
        
        # Find data
        move_id = int(selected[0])
        move = next((m for m in self.moves_data if m['id'] == move_id), None)
        
        if move:
            self.selected_move = move
            self.lbl_r_id.config(text=f"Transaction ID: #{move['id']}  |  Date: {move['created_at'][:16].replace('T', ' ')}")
            self.lbl_r_prod.config(text=f"{move['product_name']} ({move['sku']})")
            
            type_color = "green" if move['move_type'] == "IN" else "red"
            self.lbl_r_meta.config(text=f"Type: {move['move_type']}   |   Location: {move['location'] or 'N/A'}", fg=type_color)
            
            self.lbl_r_price.config(text=f"Quantity: {move['quantity']}  x  Unit Price: ₹{move['unit_price']}")
            self.lbl_r_total.config(text=f"Total Value: ₹{move['total_value']}")
            
            # Enable Buttons
            self.btn_view.config(state="normal")
            self.btn_dl.config(state="normal")

    def view_receipt_popup(self):
        m = self.selected_move
        info = f"""
        STOCK MASTER RECEIPT
        --------------------
        Tx ID:    #{m['id']}
        Date:     {m['created_at'][:16].replace("T", " ")}
        Type:     {m['move_type']}
        
        Product:  {m['product_name']}
        SKU:      {m['sku']}
        Location: {m['location']}
        
        Qty:      {m['quantity']}
        Price:    ₹{m['unit_price']}
        --------------------
        TOTAL:    ₹{m['total_value']}
        """
        messagebox.showinfo(f"Receipt #{m['id']}", info)

    def download_receipt_pdf(self):
        if not HAS_PDF_LIB:
            messagebox.showerror("Error", "ReportLab library is missing.\nPlease run: pip install reportlab")
            return

        m = self.selected_move
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"Receipt_{m['id']}_{m['sku']}.pdf")
        
        if file_path:
            try:
                c = canvas.Canvas(file_path, pagesize=letter)
                width, height = letter
                
                # Header
                c.setFont("Helvetica-Bold", 20)
                c.drawString(50, height - 50, "STOCK MASTER")
                c.setFont("Helvetica", 10)
                c.drawString(50, height - 65, "Official Transaction Receipt")
                
                c.line(50, height - 80, width - 50, height - 80)
                
                # Content
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, height - 120, f"Transaction ID: #{m['id']}")
                c.drawString(400, height - 120, f"Date: {m['created_at'][:10]}")
                
                y = height - 160
                c.setFont("Helvetica", 12)
                c.drawString(50, y, f"Type: {m['move_type']}")
                c.drawString(200, y, f"Location: {m['location'] or 'N/A'}")
                
                y -= 40
                c.drawString(50, y, f"Product: {m['product_name']}")
                c.drawString(400, y, f"SKU: {m['sku']}")
                
                # Table Box
                y -= 60
                c.rect(50, y-10, width-100, 40, fill=0)
                c.setFont("Helvetica-Bold", 12)
                c.drawString(60, y+5, "Description")
                c.drawString(300, y+5, "Qty")
                c.drawString(400, y+5, "Price")
                c.drawString(500, y+5, "Total")
                
                y -= 30
                c.setFont("Helvetica", 12)
                c.drawString(60, y, m['product_name'])
                c.drawString(300, y, str(m['quantity']))
                c.drawString(400, y, str(m['unit_price']))
                c.drawString(500, y, str(m['total_value']))
                
                # Total
                y -= 50
                c.setFont("Helvetica-Bold", 16)
                c.drawString(350, y, "GRAND TOTAL:")
                c.drawString(500, y, f"Rs. {m['total_value']}")
                
                # Footer
                c.setFont("Helvetica-Oblique", 10)
                c.drawString(50, 50, "Generated by Stock Master System")
                
                c.save()
                messagebox.showinfo("Success", "PDF Downloaded Successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save PDF: {e}")

    def open_transaction_modal(self, default_type="IN"):
       
        pass
    
    def update_location_label(self, event):
        val = self.combo_type.get(); self.lbl_location.config(text="From:" if val=="IN" else "To:")
    
    def open_history_modal(self, move_type):
        pass
    
    def open_transaction_modal(self, default_type="IN"):
         messagebox.showinfo("Info", "Please check Step 16 code for the full transaction modal implementation.")