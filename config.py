# config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "clients.db")
EPAISSEURS = ["1/8\"", "1/4\"", "1/2\"", "1\"", "1-1/2\"", "2\"", "3\""]
TAUX_CHANGE_DEFAULT = 1.4