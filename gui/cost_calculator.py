import tkinter as tk
import ttkbootstrap as ttkb
import sqlite3

class CostCalculatorWindow:
    def __init__(self, parent, data):
        self.data = data
        self.window = ttkb.Toplevel(parent)
        self.window.title("Calcul des coûts de contrat")
        self.window.geometry("1000x800")

        # Canvas avec scrollbar
        canvas = ttkb.Canvas(self.window)
        scrollbar = ttkb.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttkb.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Titre principal
        tk.Label(self.scrollable_frame, text="CALCUL DES COÛTS DE CONTRAT", font=("Arial", 16, "bold")).pack(pady=10)

        # Conteneur principal
        main_frame = ttkb.Frame(self.scrollable_frame)
        main_frame.pack(padx=20, pady=20)

        # Dictionnaire pour stocker les widgets des champs
        self.widgets = {}

        # Section 1 : 6 lignes × 2 colonnes
        section1_frame = tk.LabelFrame(main_frame, text="Informations générales", font=("Arial", 12, "bold"))
        section1_frame.pack(fill="x", pady=10)

        section1_labels = [
            "Date des travaux",
            "Soumission",
            "Client",
            "Adresse",
            "",  # Espace vide
            "Taux de change actuel",
            "Surface (pi²)"
        ]

        for row, label in enumerate(section1_labels):
            if label:  # Ignore l'espace vide
                tk.Label(section1_frame, text=label, font=("Arial", 10)).grid(row=row, column=0, sticky="e", padx=5, pady=5)
                var = tk.StringVar()
                entry = tk.Entry(section1_frame, textvariable=var, width=40)
                entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)
                self.widgets[label] = var
                # Pré-remplir les champs disponibles depuis self.data
                if label == "Date des travaux":
                    var.set(self.data.get("date_travaux", ""))
                elif label == "Soumission":
                    var.set(self.data.get("soumission_reel", ""))
                elif label == "Client":
                    var.set(self.data.get("client_reel", ""))
                elif label == "Adresse":
                    var.set(self.data.get("adresse_reel", ""))
                elif label == "Surface (pi²)":
                    var.set(self.data.get("superficie_reel", ""))

        # Section 2 : 19 lignes × 4 colonnes
        section2_frame = tk.LabelFrame(main_frame, text="Détails des coûts", font=("Arial", 12, "bold"))
        section2_frame.pack(fill="both", expand=True, pady=10)

        section2_headers = ["Description", "Total réel", "Total soumission", "Différence"]
        for col, header in enumerate(section2_headers):
            tk.Label(section2_frame, text=header, font=("Arial", 10, "bold"), borderwidth=1, relief="solid").grid(row=0, column=col, padx=2, pady=2, sticky="nsew")

        section2_labels = [
            "Produit",
            "Prix produit",
            "Quantité sable",
            "Fournisseur sable",
            "Type de camion",
            "Nombre de voyages",
            "Secteur",
            "Prix total sable",
            "Apprêts",
            "Prix total apprêts",
            "Type de membrane",
            "Nombre rouleaux",
            "Prix total membrane",
            "Main d'œuvre",
            "Machinerie",
            "Pension",
            "Ajustements",
            "Total"
        ]

        for row, label in enumerate(section2_labels, start=1):
            tk.Label(section2_frame, text=label, font=("Arial", 10), borderwidth=1, relief="solid").grid(row=row, column=0, padx=2, pady=2, sticky="nsew")
            for col in range(1, 4):  # Colonnes Total réel, Total soumission, Différence
                var = tk.StringVar()
                entry = tk.Entry(section2_frame, textvariable=var, width=20)
                entry.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
                self.widgets[f"{label}_{section2_headers[col]}"] = var
                # Pré-remplir les champs disponibles depuis self.data
                if label == "Produit" and col == 1:
                    var.set(self.data.get("produit_reel", ""))
                elif label == "Type de membrane" and col == 1:
                    var.set(self.data.get("type_membrane", ""))
                elif label == "Nombre rouleaux" and col == 1:
                    var.set(self.data.get("nb_rouleaux_installes_reel", ""))
                elif label == "Quantité sable" and col == 1:
                    var.set(self.data.get("sable_utilise_reel", ""))

        for col in range(4):
            section2_frame.grid_columnconfigure(col, weight=1)

        # Section 3 : 3 lignes × 2 colonnes
        section3_frame = tk.LabelFrame(main_frame, text="Résumé", font=("Arial", 12, "bold"))
        section3_frame.pack(fill="x", pady=10)

        section3_labels = [
            "Facture no.",
            "Profit",
            ""  # Espace ou total
        ]

        for row, label in enumerate(section3_labels):
            if label:
                tk.Label(section3_frame, text=label, font=("Arial", 10)).grid(row=row, column=0, sticky="e", padx=5, pady=5)
                var = tk.StringVar()
                entry = tk.Entry(section3_frame, textvariable=var, width=40)
                entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)
                self.widgets[label] = var
                # Le champ Profit sera calculé automatiquement plus tard
                if label == "Profit":
                    entry.configure(state="readonly")  # Lecture seule pour le profit calculé

        # Boutons en bas
        button_frame = ttkb.Frame(self.scrollable_frame)
        button_frame.pack(pady=20)

        ttkb.Button(
            button_frame,
            text="Sauvegarder dans la table",
            command=self.save_to_table,
            bootstyle="success"
        ).pack(side="left", padx=10)

        ttkb.Button(
            button_frame,
            text="Annuler",
            command=self.window.destroy,
            bootstyle="danger"
        ).pack(side="left", padx=10)

    def save_to_table(self):
        # Placeholder pour la sauvegarde des données
        # À implémenter : enregistrer dans la table `costs` et mettre à jour `chantiers_reels`
        pass