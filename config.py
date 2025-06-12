# config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database/clients.db")

DEFAULT_USD_CAD_RATE = 1.4

# Liste explicite des épaisseurs de 1/8" à 3" par incréments de 1/8"
THICKNESS_OPTIONS = [
    "1/8\"", "1/4\"", "3/8\"", "1/2\"", "5/8\"", "3/4\"", "7/8\"",
    "1\"", "1-1/8\"", "1-1/4\"", "1-3/8\"", "1-1/2\"", "1-5/8\"", "1-3/4\"", "1-7/8\"",
    "2\"", "2-1/8\"", "2-1/4\"", "2-3/8\"", "2-1/2\"", "2-5/8\"", "2-3/4\"", "2-7/8\"", "3\""
]

SUBFLOOR_OPTIONS = ["Béton", "Contreplaqué", "OSB", "Carton fibre", "Membrane", "Autre"]
DEFAULT_SUBFLOOR = "Contreplaqué"
# Nouvelles constantes pour Pose membrane
POSE_MEMBRANE_OPTIONS = ["A déterminer", "Pose avec divisions", "Pose sans divisions", "Pose mixte", "Fourniture seulement", "Aucune"]