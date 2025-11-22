import tkinter as tk
from tkinter import ttk, messagebox
import requests

class ForgotPasswordScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Reset Password - Stock Master")
        self.API_URL = "http://127.0.0.1:8000"
        
        self.email_storage = ""
        self.otp_storage = ""
        
        self.setup_window()
        self.setup_ui()

    def setup_window(self):
        try:
            self.root.state('zoomed')
        except tk.TclError:
            w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
            self.root.geometry(f"{w}x{h}+0+0")
        self.root.resizable(False, False)

    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        main_container = tk.Frame(self.root)
        main_container.pack(fill="both", expand=True)
        main_container.grid_columnconfigure(0, weight=1, uniform="half_split")
        main_container.grid_columnconfigure(1, weight=1, uniform="half_split")
        main_container.grid_rowconfigure(0, weight=1)

        self.canvas_left = tk.Canvas(main_container, highlightthickness=0)
        self.canvas_left.grid(row=0, column=0, sticky="nsew")
        self.draw_gradient(self.canvas_left, "#ff9966", "#ff5e62")
        
        screen_h = self.root.winfo_screenheight()
        self.canvas_left.create_text(50, 60, text="*", font=("Courier", 70), fill="white", anchor="nw")
        self.canvas_left.create_text(50, screen_h - 270, text="Security First", font=("Helvetica", 14), fill="#FFF1F2", anchor="w")
        self.canvas_left.create_text(50, screen_h - 180, text="Recover access to\nyour dashboard\nsecurely.", font=("Helvetica", 28, "bold"), fill="white", anchor="w", justify="left")

        self.frame_right = tk.Frame(main_container, bg="white")
        self.frame_right.grid(row=0, column=1, sticky="nsew")
        
        self.show_step_1_email()

    def show_step_1_email(self):
        self.clear_right_frame()
        
        card = tk.Frame(self.frame_right, bg="white")
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="*", font=("Courier", 50), fg="black", bg="white").pack(anchor="w")
        tk.Label(card, text="Forgot Password", font=("Helvetica", 26, "bold"), fg="#111827", bg="white").pack(anchor="w")
        tk.Label(card, text="Enter your registered email address.", font=("Helvetica", 10), fg="#6b7280", bg="white").pack(anchor="w", pady=(5, 30))

        tk.Label(card, text="Email Address", font=("Helvetica", 10, "bold"), fg="#111827", bg="white").pack(anchor="w", pady=(0, 5))
        self.entry_email = tk.Entry(card, font=("Helvetica", 11), width=40, bg="#F9FAFB", relief="flat", highlightthickness=1, highlightbackground="#E5E7EB")
        self.entry_email.pack(ipady=8, pady=(0, 30))

        btn_get_otp = tk.Button(card, text="Get OTP", font=("Helvetica", 11, "bold"), bg="black", fg="white", relief="flat", cursor="hand2",
                                command=self.action_get_otp)
        btn_get_otp.pack(fill="x", ipady=10)
        
        self.add_back_button(card)

    def show_step_2_otp(self):
        self.clear_right_frame()
        
        card = tk.Frame(self.frame_right, bg="white")
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="Verify OTP", font=("Helvetica", 26, "bold"), fg="#111827", bg="white").pack(anchor="w")
        tk.Label(card, text=f"Enter the 6-digit code sent to\n{self.email_storage}", font=("Helvetica", 10), fg="#6b7280", bg="white", justify="left").pack(anchor="w", pady=(5, 30))

        self.entry_otp = tk.Entry(card, font=("Helvetica", 14, "bold"), width=20, bg="#F9FAFB", relief="flat", highlightthickness=1, highlightbackground="#E5E7EB", justify="center")
        self.entry_otp.pack(ipady=10, pady=(0, 30))

        btn_verify = tk.Button(card, text="Verify Code", font=("Helvetica", 11, "bold"), bg="black", fg="white", relief="flat", cursor="hand2",
                               command=self.action_verify_otp)
        btn_verify.pack(fill="x", ipady=10)
        
        btn_resend = tk.Button(card, text="Resend Code", font=("Helvetica", 9), bg="white", fg="#2563eb", relief="flat", cursor="hand2", command=self.action_get_otp)
        btn_resend.pack(pady=10)

    def show_step_3_reset(self):
        self.clear_right_frame()
        
        card = tk.Frame(self.frame_right, bg="white")
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(card, text="Set New Password", font=("Helvetica", 26, "bold"), fg="#111827", bg="white").pack(anchor="w")
        tk.Label(card, text="Create a strong password.", font=("Helvetica", 10), fg="#6b7280", bg="white").pack(anchor="w", pady=(5, 30))

        tk.Label(card, text="New Password", font=("Helvetica", 10, "bold"), bg="white").pack(anchor="w", pady=(0, 5))
        self.entry_new = tk.Entry(card, font=("Helvetica", 11), width=40, bg="#F9FAFB", relief="flat", show="*", highlightthickness=1)
        self.entry_new.pack(ipady=8, pady=(0, 15))

        tk.Label(card, text="Re-enter Password", font=("Helvetica", 10, "bold"), bg="white").pack(anchor="w", pady=(0, 5))
        self.entry_conf = tk.Entry(card, font=("Helvetica", 11), width=40, bg="#F9FAFB", relief="flat", show="*", highlightthickness=1)
        self.entry_conf.pack(ipady=8, pady=(0, 30))

        btn_reset = tk.Button(card, text="Reset Password", font=("Helvetica", 11, "bold"), bg="black", fg="white", relief="flat", cursor="hand2",
                              command=self.action_final_reset)
        btn_reset.pack(fill="x", ipady=10)

    def action_get_otp(self):
        email = self.email_storage if self.email_storage else self.entry_email.get().strip()
        if not email:
            messagebox.showwarning("Input", "Please enter your email.")
            return
        
        try:
            res = requests.post(f"{self.API_URL}/forgot-password/request-otp", json={"email": email})
            if res.status_code == 200:
                self.email_storage = email
                messagebox.showinfo("Sent", "OTP sent to your email.")
                self.show_step_2_otp()
            else:
                messagebox.showerror("Error", "Email not found.")
        except:
            messagebox.showerror("Error", "Connection Failed")

    def action_verify_otp(self):
        otp = self.entry_otp.get().strip()
        if len(otp) != 6:
            messagebox.showerror("Error", "Invalid OTP format")
            return

        try:
            payload = {"email": self.email_storage, "otp": otp}
            res = requests.post(f"{self.API_URL}/forgot-password/verify-otp", json=payload)
            
            if res.status_code == 200:
                self.otp_storage = otp
                self.show_step_3_reset()
            else:
                messagebox.showerror("Error", "Invalid OTP.")
        except:
            messagebox.showerror("Error", "Connection Failed")

    def action_final_reset(self):
        new = self.entry_new.get().strip()
        conf = self.entry_conf.get().strip()
        
        if new != conf:
            messagebox.showerror("Error", "Passwords do not match")
            return
        if len(new) < 4:
            messagebox.showerror("Error", "Password too short")
            return

        try:
            payload = {
                "email": self.email_storage,
                "otp": self.otp_storage,
                "new_password": new
            }
            res = requests.post(f"{self.API_URL}/forgot-password/reset", json=payload)
            
            if res.status_code == 200:
                self.show_success_screen()
            else:
                messagebox.showerror("Error", "Reset Failed. OTP might be expired.")
        except:
            messagebox.showerror("Error", "Connection Failed")

    def show_success_screen(self):
        self.clear_right_frame()
        card = tk.Frame(self.frame_right, bg="white")
        card.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(card, text="✔", font=("Arial", 60), fg="#10B981", bg="white").pack(pady=10)
        tk.Label(card, text="Password Reset Successful!", font=("Helvetica", 18, "bold"), bg="white", fg="#111827").pack()
        tk.Label(card, text="Redirecting to login...", font=("Helvetica", 10), bg="white", fg="#6b7280").pack(pady=10)
        
        self.root.after(3000, self.open_login) 

    def clear_right_frame(self):
        for widget in self.frame_right.winfo_children():
            widget.destroy()

    def add_back_button(self, parent):
        footer_frame = tk.Frame(parent, bg="white")
        footer_frame.pack(pady=20)
        btn_back = tk.Button(footer_frame, text="Back to Login", font=("Helvetica", 10, "bold"), fg="black", bg="white", 
                             cursor="hand2", relief="flat", borderwidth=0, command=self.open_login)
        btn_back.pack()

    def open_login(self):
        from windows.login import LoginScreen
        LoginScreen(self.root)

    def draw_gradient(self, canvas, color1, color2):
        width = self.root.winfo_screenwidth() // 2 
        height = self.root.winfo_screenheight()
        canvas.delete("gradient")
        r1, g1, b1 = self.hex_to_rgb(color1)
        r2, g2, b2 = self.hex_to_rgb(color2)
        steps = 100
        for i in range(steps):
            r, g, b = int(r1 + (r2 - r1) * i / steps), int(g1 + (g2 - g1) * i / steps), int(b1 + (b2 - b1) * i / steps)
            color = f'#{r:02x}{g:02x}{b:02x}'
            y0, y1 = i * (height / steps), (i + 1) * (height / steps)
            canvas.create_rectangle(0, y0, width + 200, y1 + 2, fill=color, outline=color, tags="gradient")
        canvas.tag_lower("gradient")

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))