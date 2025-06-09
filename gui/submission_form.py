# gui/submission_form.py
import tkinter as tk
from tkinter import ttk, messagebox
from calculations.submission_calcs import calculer_quantite_sacs
from config import EPAISSEURS

class SubmissionForm:
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.window = tk.Toplevel(parent)
        self.window.title("Calcul Soumission")
        self.window.geometry("500x400")

        frame = ttk.LabelFrame(self.window, text="Paramètres", padding=10)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Superficie
        tk.Label(frame, text="Superficie (pi²)").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.superficie_entry = tk.Entry(frame, width=20)
        self.superficie_entry.grid(row=0, column=1, padx=5, pady=5)

        # Produit
        tk.Label(frame, text="Produit").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.produit_var = tk.StringVar()
        produits = self.db_manager.get_produits()
        self.produit_var.set(produits[0] if produits else "Aucun")
        tk.OptionMenu(frame, self.produit_var, *produits).grid(row=1, column=1, padx=5, pady=5)

        # Épaisseur
        tk.Label(frame, text="Épaisseur").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.epaisseur_var = tk.StringVar(value="1\"")
        tk.OptionMenu(frame, self.epaisseur_var, *EPAISSEURS).grid(row=2, column=1, padx=5, pady=5)

        # Résultats
        tk.Label(frame, text="Nombre de sacs").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.label_sacs = tk.Label(frame, text="-", relief="sunken", width=15)
        self.label_sacs.grid(row=3, column=1, padx=5, pady=5)

        tk.Button(frame, text="Calculer", command=self.calculer).grid(row=4, column=0, columnspan=2, pady=10)

    def calculer(self):
        try:
            superficie = self.superficie_entry.get()
            produit = self.produit_var.get()
            epaisseur = self.epaisseur_var.get()
            sacs, _, _, _, _ = calculer_quantite_sacs(superficie, produit, epaisseur, "1:1", self.db_manager)
            self.label_sacs.config(text=f"{sacs:,}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur de calcul : {e}")
            self.label_sacs.config(text="-")