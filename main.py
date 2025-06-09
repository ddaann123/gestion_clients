# main.py
import tkinter as tk
from database.db_manager import DatabaseManager
from gui.main_window import MainWindow
from config import DB_PATH

if __name__ == "__main__":
    root = tk.Tk()
    db_manager = DatabaseManager(DB_PATH)
    app = MainWindow(root, db_manager)
    root.mainloop()
    db_manager.close()