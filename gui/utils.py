# c:\gestion_clients\gui\utils.py
import re
from datetime import datetime
from tkinter import messagebox

def validate_date(input_text):
    """Valide les entrées partielles pour une date au format JJ-MM-AAAA pendant la saisie."""
    if not input_text:
        return True
    pattern = r"^\d{0,2}(-\d{0,2}(-\d{0,4})?)?$"
    return bool(re.match(pattern, input_text))

def validate_date_on_focusout(var, error_title="Erreur"):
    """Valide la date complète au format JJ-MM-AAAA lorsque le champ perd le focus."""
    date_text = var.get()
    if not date_text:
        return
    pattern = r"^\d{2}-\d{2}-\d{4}$"
    if not re.match(pattern, date_text):
        messagebox.showerror(error_title, "Format de date invalide. Utilisez JJ-MM-AAAA (ex. 05-07-2025).")
        var.set("")
        return
    try:
        datetime.strptime(date_text, "%d-%m-%Y")
    except ValueError:
        messagebox.showerror(error_title, "Date invalide. Vérifiez que la date est correcte (ex. 05-07-2025).")
        var.set("")

def check_date_on_save(date_text, field_name="date"):
    """Valide une date complète au format JJ-MM-AAAA et la convertit en YYYY-MM-DD pour la sauvegarde."""
    if not date_text:
        messagebox.showerror("Erreur", f"La {field_name} est requise.")
        return None
    pattern = r"^\d{2}-\d{2}-\d{4}$"
    if not re.match(pattern, date_text):
        messagebox.showerror("Erreur", f"Format de date invalide. Utilisez JJ-MM-AAAA (ex. 05-07-2025).")
        return None
    try:
        date_obj = datetime.strptime(date_text, "%d-%m-%Y")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Erreur", f"Date invalide. Vérifiez que la date est correcte (ex. 05-07-2025).")
        return None