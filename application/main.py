import tkinter as tk
# Import the classes from the windows folder
from windows.splash import SplashScreen
from windows.login import LoginScreen

class StockMasterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.withdraw()
        
        SplashScreen(self, self.show_login)

    def show_login(self):
        """Callback to show login screen after splash finishes"""
        self.deiconify()
        LoginScreen(self)

if __name__ == "__main__":
    app = StockMasterApp()
    app.mainloop()