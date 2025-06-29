# Test pour valider le transfert sur GitHub
# main.py


import sys
import os
#test
# Définir le répertoire racine comme point de départ avant les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from database.db_manager import DatabaseManager  # Import relatif
from gui.main_window import MainWindow           # Import relatif
from config import DB_PATH                        # Import relatif

if __name__ == "__main__":
    from ttkbootstrap import Window
    root = Window(themename="flatly")  # ou autre thème : "superhero", "cyborg", "solar", etc.

    db_manager = DatabaseManager(DB_PATH)
    app = MainWindow(root, db_manager)
    root.mainloop()
    db_manager.close()
