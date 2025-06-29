import ttkbootstrap as ttkb
import json
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

class WorkSheetsSearchWindow:
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.window = ttkb.Toplevel(parent)
        self.window.title("Recherche des feuilles de travail")
        self.window.geometry("1100x900")

        self.create_widgets()
        self.load_recent_work_sheets()

    def create_widgets(self):
        search_frame = ttkb.Frame(self.window)
        search_frame.pack(fill="x", padx=10, pady=10)

        # Champs de recherche
        self.vars = {
            'soumission_reel': ttkb.StringVar(),
            'client_reel': ttkb.StringVar(),
            'adresse_reel': ttkb.StringVar(),
            'date_travaux': ttkb.StringVar(),
            'date_soumission': ttkb.StringVar(),
        }

        row = 0
        for label, key in [
            ("Numéro soumission:", 'soumission_reel'),
            ("Client:", 'client_reel'),
            ("Adresse:", 'adresse_reel'),
            ("Date travaux (AAAA-MM-JJ):", 'date_travaux'),
            ("Date soumission (AAAA-MM-JJ):", 'date_soumission'),
        ]:
            ttkb.Label(search_frame, text=label).grid(row=row, column=0, sticky="e", padx=5, pady=3)
            ttkb.Entry(search_frame, textvariable=self.vars[key], width=30).grid(row=row, column=1, sticky="w", padx=5)
            row += 1

        ttkb.Button(search_frame, text="Rechercher", command=self.rechercher, bootstyle=PRIMARY).grid(row=row, column=0, columnspan=2, pady=10)

        self.tree = ttkb.Treeview(
            self.window,
            columns=("soumission_reel", "client_reel", "adresse_reel", "date_travaux", "date_soumission"),
            show="headings",
            bootstyle="dark"
        )

        for col, label in zip(self.tree["columns"], [
            "Soumission", "Client", "Adresse", "Date travaux", "Date soumission"]):
            self.tree.heading(col, text=label, anchor="w")
            self.tree.column(col, width=150)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", self.ouvrir_feuille)

        ttkb.Button(self.window, text="Supprimer la feuille sélectionnée", command=self.supprimer_feuille, bootstyle=DANGER).pack(pady=(0, 10))

    def load_recent_work_sheets(self):
        """Charge les 25 dernières feuilles de travail."""
        try:
            resultats = self.db_manager.search_work_sheets(limit=25)
            self.tree.delete(*self.tree.get_children())
            for row in resultats:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            Messagebox.show_error(f"Erreur lors du chargement des feuilles : {e}")

    def rechercher(self):
        """Recherche les feuilles selon les critères saisis."""
        criteres = {k: v.get().strip() for k, v in self.vars.items() if v.get().strip() != ""}
        try:
            resultats = self.db_manager.search_work_sheets(criteres)
            self.tree.delete(*self.tree.get_children())
            for row in resultats:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            Messagebox.show_error(f"Erreur lors de la recherche : {e}")

    def supprimer_feuille(self):
        """Supprime la feuille de travail sélectionnée."""
        item = self.tree.focus()
        if not item:
            Messagebox.show_warning("Veuillez sélectionner une feuille à supprimer.")
            return

        soumission_reel = self.tree.item(item)["values"][0]
        message = (
            f"⚠️ Cette action est irréversible.\n\n"
            f"Voulez-vous VRAIMENT supprimer définitivement la feuille de travail :\n\n"
            f"{soumission_reel} ?"
        )

        confirmation = Messagebox.yesno("Confirmation de suppression", message)
        if confirmation:
            try:
                self.db_manager.delete_work_sheet(soumission_reel)
                Messagebox.show_info(f"La feuille de travail {soumission_reel} a été supprimée.")
                self.load_recent_work_sheets()
            except Exception as e:
                Messagebox.show_error(f"Erreur lors de la suppression : {e}")

    def ouvrir_feuille(self, event):
        """Ouvre les détails de la feuille sélectionnée."""
        item = self.tree.focus()
        if not item:
            return
        soumission_reel = self.tree.item(item)['values'][0]
        print(f"[DEBUG] Numéro de feuille sélectionné : {soumission_reel}")
        try:
            data = self.db_manager.charger_feuille(soumission_reel)
            print(f"[DEBUG] Données chargées : {data}")
            if data:
                WorkSheetDetailsWindow(self.window, data)
            else:
                Messagebox.show_error(f"Feuille introuvable")
        except Exception as e:
            Messagebox.show_error(f"Erreur lors de l'ouverture : {e}")

class WorkSheetDetailsWindow:
    def __init__(self, parent, data):
        self.window = ttkb.Toplevel(parent)
        self.window.title(f"Détails de la feuille - {data['soumission_reel']}")
        self.window.geometry("900x800")
        self.data = data

        self.create_widgets()

    def create_widgets(self):
        # Frame principal
        main_frame = ttkb.Frame(self.window, padding="10")
        main_frame.pack(fill="both", expand=True)

        # Section des champs principaux
        ttkb.Label(main_frame, text="Détails de la feuille", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        fields = [
            ("Numéro de soumission", "soumission_reel"),
            ("Date des travaux", "date_travaux"),
            ("Client", "client_reel"),
            ("Adresse", "adresse_reel"),
            ("Produit", "produit_reel"),
            ("Produit différent", "produit_diff"),
            ("Superficie", "superficie_reel"),
            ("Épaisseur moyenne", "thickness"),
            ("Nombre de sacs prévus", "nb_sacs_prevus"),
            ("Sacs utilisés", "sacs_utilises_reel"),
            ("Transporteur de sable", "sable_transporter_reel"),
            ("Sable théorique", "sable_total_reel"),
            ("Sable commandé", "sable_commande_reel"),
            ("Surplus de sable", "sable_utilise_reel"),
            ("Type de membrane", "type_membrane"),
            ("Nombre de rouleaux installés", "nb_rouleaux_installes_reel"),
            ("Installation membrane", "membrane_posee_reel"),
            ("Marches", "marches_reel"),
            ("Notes", "notes_reel"),
            ("Notes bureau", "notes_bureau"),  # Déplacé sous "Notes"
            ("Date de soumission", "date_soumission"),
        ]

        for i, (label, key) in enumerate(fields, start=1):
            value = self.data.get(key, "N/A")
            ttkb.Label(main_frame, text=f"{label} :").grid(row=i, column=0, sticky="e", padx=5, pady=2)
            ttkb.Label(main_frame, text=value, bootstyle="secondary").grid(row=i, column=1, sticky="w", padx=5, pady=2)

        # Section des heures de chantier (extraites de donnees_json)
        heures_chantier = json.loads(self.data.get("donnees_json", "{}")).get("heures_chantier", {})
        if heures_chantier:
            ttkb.Label(main_frame, text="Heures de chantier", font=("Helvetica", 12, "bold")).grid(row=len(fields) + 1, column=0, columnspan=2, pady=10)

            tree = ttkb.Treeview(main_frame, columns=("Employé", "Présence", "Véhicule", "Chauffeur Aller", "Chauffeur Retour", "Heure Début", "Heure Fin", "Temps Transport", "Heures Entrepôt"), show="headings", height=5)
            for col in tree["columns"]:
                tree.heading(col, text=col, anchor="w")
                tree.column(col, width=100, anchor="w")

            row_idx = len(fields) + 2
            for employe, details in heures_chantier.items():
                values = [
                    employe,
                    details.get("presence", "N/A"),
                    details.get("vehicule", "N/A"),
                    details.get("chauffeur_aller", "N/A"),
                    details.get("chauffeur_retour", "N/A"),
                    details.get("heure_debut", "N/A"),
                    details.get("heure_fin", "N/A"),
                    details.get("temps_transport", "N/A"),
                    details.get("heures_entrepot", "N/A")
                ]
                tree.insert("", "end", values=values)

            tree.grid(row=row_idx, column=0, columnspan=2, pady=10, sticky="nsew")
            main_frame.grid_columnconfigure(1, weight=1)

        # Bouton de fermeture
        ttkb.Button(self.window, text="Fermer", command=self.window.destroy, bootstyle="danger").pack(pady=10)