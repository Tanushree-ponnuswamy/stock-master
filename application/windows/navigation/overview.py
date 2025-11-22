import tkinter as tk
from tkinter import ttk
import requests
from datetime import datetime, timedelta
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class OverviewView:
    def __init__(self, parent):
        self.parent = parent
        self.API_URL = "http://127.0.0.1:8000"
        
        self.frame = tk.Frame(parent, bg="#f3f4f6")
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.setup_header()
        self.setup_kpi_row()
        self.setup_analytics_section()
        
        # Load data immediately
        self.refresh_data()

    def setup_header(self):
        header_frame = tk.Frame(self.frame, bg="#f3f4f6")
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(header_frame, text="Dashboard Overview", font=("Helvetica", 24, "bold"), fg="#111827", bg="#f3f4f6").pack(side="left")
        
        current_date = datetime.now().strftime("%A, %d %B %Y")
        tk.Label(header_frame, text=current_date, font=("Helvetica", 11), fg="#6b7280", bg="#f3f4f6").pack(side="right", pady=5)

    def setup_kpi_row(self):
        kpi_frame = tk.Frame(self.frame, bg="#f3f4f6")
        kpi_frame.pack(fill="x", pady=(0, 20))
        
        self.create_kpi_card(kpi_frame, "Total Inventory Value", "₹0.00", "💰", "#2563eb", 0)
        self.create_kpi_card(kpi_frame, "Total Products", "0", "📦", "#10b981", 1)
        self.create_kpi_card(kpi_frame, "Low Stock Alerts", "0", "⚠", "#f59e0b", 2)
        self.create_kpi_card(kpi_frame, "Moves Today", "0", "🚚", "#8b5cf6", 3)

    def create_kpi_card(self, parent, title, value, icon, color, col_index):
        card = tk.Frame(parent, bg="white", padx=20, pady=20, relief="flat")
        card.grid(row=0, column=col_index, sticky="ew", padx=(0, 20))
        parent.grid_columnconfigure(col_index, weight=1)
        
        lbl_icon = tk.Label(card, text=icon, font=("Arial", 20), bg="white", fg=color)
        lbl_icon.pack(anchor="w")
        
        lbl_val = tk.Label(card, text=value, font=("Helvetica", 22, "bold"), bg="white", fg="#111827")
        lbl_val.pack(anchor="w", pady=(5, 0))
        
        lbl_title = tk.Label(card, text=title, font=("Helvetica", 10), bg="white", fg="#6b7280")
        lbl_title.pack(anchor="w")
        
        setattr(self, f"kpi_val_{col_index}", lbl_val)

    def setup_analytics_section(self):
        charts_frame = tk.Frame(self.frame, bg="#f3f4f6")
        charts_frame.pack(fill="both", expand=True)
        
        self.left_chart_frame = tk.Frame(charts_frame, bg="white", padx=10, pady=10)
        self.left_chart_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.right_chart_frame = tk.Frame(charts_frame, bg="white", padx=10, pady=10)
        self.right_chart_frame.pack(side="left", fill="both", expand=True, padx=(10, 0))

    def refresh_data(self):
        """Fetches data, calculates history, and updates UI"""
        try:
            # 1. Fetch Data
            prod_res = requests.get(f"{self.API_URL}/products")
            products = prod_res.json() if prod_res.status_code == 200 else []
            
            move_res = requests.get(f"{self.API_URL}/stock-moves")
            moves = move_res.json() if move_res.status_code == 200 else []
            
            # --- KPI CALCULATIONS ---
            current_total_value = sum(p['stock'] * (p.get('price') or 0) for p in products)
            total_count = len(products)
            low_stock = sum(1 for p in products if 0 < p['stock'] < 10)
            
            today_str = datetime.now().strftime("%Y-%m-%d")
            today_moves = sum(1 for m in moves if m['created_at'].startswith(today_str))
            
            # Update KPI Text
            self.kpi_val_0.config(text=f"₹{current_total_value:,.2f}")
            self.kpi_val_1.config(text=str(total_count))
            self.kpi_val_2.config(text=str(low_stock))
            self.kpi_val_3.config(text=str(today_moves))
            
            # --- DYNAMIC TREND CALCULATION (Retroactive) ---
            # 1. Organize moves by date
            moves_by_date = {}
            for m in moves:
                d_str = m['created_at'][:10] # YYYY-MM-DD
                val = m['total_value']
                if m['move_type'] == "OUT": val = -val # Negative value for outflow
                moves_by_date[d_str] = moves_by_date.get(d_str, 0) + val

            # 2. Calculate last 7 days values working backwards from today
            dates_x = []
            values_y = []
            
            running_value = current_total_value
            
            for i in range(7):
                target_date = datetime.now() - timedelta(days=i)
                date_str = target_date.strftime("%Y-%m-%d")
                display_date = target_date.strftime("%a") # Mon, Tue...
                
                # The value at end of 'date_str' is 'running_value'
                dates_x.insert(0, display_date)
                values_y.insert(0, running_value)
                
                # Calculate previous day's end value
                net_change = moves_by_date.get(date_str, 0)
                running_value = running_value - net_change

            # --- RENDER CHARTS ---
            self.render_line_chart(dates_x, values_y)
            self.render_bar_chart(products)
            
        except Exception as e:
            print(f"Error loading overview: {e}")

    def render_line_chart(self, days, values):
        """Draws Line Chart with a Modern Theme"""
        # Clear previous chart
        for w in self.left_chart_frame.winfo_children(): w.destroy()
        
        tk.Label(self.left_chart_frame, text="Inventory Value Trend (Last 7 Days)", font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w", pady=10)

        # 1. Create Figure with White Background
        fig = Figure(figsize=(5, 4), dpi=100, facecolor='white')
        ax = fig.add_subplot(111)
        ax.set_facecolor('white')
        
        # 2. Plot the Line (Vibrant Indigo)
        ax.plot(days, values, marker='o', markersize=6, markerfacecolor='white', markeredgewidth=2, 
                color='#6366f1', linewidth=2.5)
        
        # 3. Fill Area (Soft Indigo Tint)
        ax.fill_between(days, values, color='#6366f1', alpha=0.1)
        
        # 4. Dynamic Y-Axis scaling
        if values:
            min_val = min(values)
            max_val = max(values)
            margin = (max_val - min_val) * 0.1
            if margin == 0: margin = 100 
            ax.set_ylim(bottom=max(0, min_val - margin), top=max_val + margin)
            
        # 5. Minimalist Styling
        ax.grid(axis='y', linestyle='-', alpha=0.1, color='black')
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#e5e7eb')
        
        ax.tick_params(axis='x', colors='#6b7280', labelsize=8)
        ax.tick_params(axis='y', colors='#6b7280', labelsize=8, length=0)
        
        # 6. Render
        canvas = FigureCanvasTkAgg(fig, self.left_chart_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def render_bar_chart(self, products):
        """Draws Horizontal Bar Chart of Top Categories"""
        for w in self.right_chart_frame.winfo_children(): w.destroy()
        
        tk.Label(self.right_chart_frame, text="Top Categories by Value", font=("Helvetica", 11, "bold"), bg="white").pack(anchor="w", pady=10)

        # Calculate Value per Category
        cat_vals = {}
        for p in products:
            val = p['stock'] * (p.get('price') or 0)
            cat_vals[p['category']] = cat_vals.get(p['category'], 0) + val
            
        # Sort and take top 5
        sorted_cats = sorted(cat_vals.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if not sorted_cats:
            tk.Label(self.right_chart_frame, text="No Inventory Data", bg="white", fg="#999").pack(expand=True)
            return

        cats = [x[0] for x in sorted_cats]
        vals = [x[1] for x in sorted_cats]

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        bars = ax.barh(cats, vals, color='#10b981')
        ax.invert_yaxis()
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        canvas = FigureCanvasTkAgg(fig, self.right_chart_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)