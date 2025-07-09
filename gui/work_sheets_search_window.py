import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import json
import re
from datetime import datetime
import tkinter as tk
import logging

from gui.cost_calculator import CostCalculatorWindow

# Configurer le logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class WorkSheetsSearchWindow:
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.window = ttkb.Toplevel(parent)
        self.window.title("Recherche des feuilles de travail")
        self.window.geometry("1000x900")

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
        }

        row = 0
        for label, key in [
            ("Numéro soumission:", 'soumission_reel'),
            ("Client:", 'client_reel'),
            ("Adresse:", 'adresse_reel'),
            ("Date travaux (AAAA-MM-JJ):", 'date_travaux'),
        ]:
            ttkb.Label(search_frame, text=label).grid(row=row, column=0, sticky="e", padx=5, pady=3)
            ttkb.Entry(search_frame, textvariable=self.vars[key], width=30).grid(row=row, column=1, sticky="w", padx=5)
            row += 1

        ttkb.Button(search_frame, text="Rechercher", command=self.rechercher, bootstyle=PRIMARY).grid(row=row, column=0, columnspan=2, pady=10)

        self.tree = ttkb.Treeview(
            self.window,
            columns=("soumission_reel", "client_reel", "adresse_reel", "date_travaux", "est_calcule"),
            show="headings",
            bootstyle="dark"
        )

        for col, label in zip(self.tree["columns"], [
            "Soumission", "Client", "Adresse", "Date travaux", "Coûts Calculés"]):
            self.tree.heading(col, text=label, anchor="w")
            self.tree.column(col, width=150 if col != "est_calcule" else 100)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", self.ouvrir_feuille)

        ttkb.Button(self.window, text="Supprimer la feuille sélectionnée", command=self.supprimer_feuille, bootstyle=DANGER).pack(pady=(0, 10))

    def load_recent_work_sheets(self):
        """Charge les 25 dernières feuilles de travail."""
        try:
            resultats = self.db_manager.search_work_sheets(limit=25)
            logging.debug(f"Résultats bruts dans load_recent_work_sheets : {resultats}")
            
            self.tree.delete(*self.tree.get_children())
            seen = set()  # Pour éviter les doublons dans l'affichage
            for row in resultats:
                key = (row[0], row[3])  # soumission_reel, date_travaux
                if key not in seen:
                    seen.add(key)
                    est_calcule = row[4]
                    est_calcule_display = "✔" if est_calcule and int(est_calcule) == 1 else ""
                    self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], est_calcule_display))
                    logging.debug(f"Affichage de la feuille : {row}")
            logging.debug(f"Fin de load_recent_work_sheets, {len(seen)} feuilles affichées")
        except Exception as e:
            logging.error(f"Erreur lors du chargement des feuilles : {str(e)}")
            Messagebox.show_error(f"Erreur lors du chargement des feuilles : {str(e)}")

    def rechercher(self):
        """Recherche les feuilles selon les critères saisis."""
        try:
            criteres = {k: v.get().strip() for k, v in self.vars.items() if v.get().strip() != ""}
            logging.debug(f"Critères de recherche : {criteres}")
            resultats = self.db_manager.search_work_sheets(**criteres)
            logging.debug(f"Résultats bruts dans rechercher : {resultats}")
            
            self.tree.delete(*self.tree.get_children())
            seen = set()  # Pour éviter les doublons dans l'affichage
            for row in resultats:
                key = (row[0], row[3])  # soumission_reel, date_travaux
                if key not in seen:
                    seen.add(key)
                    est_calcule = row[4]
                    est_calcule_display = "✔" if est_calcule and int(est_calcule) == 1 else ""
                    self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], est_calcule_display))
                    logging.debug(f"Affichage de la feuille : {row}")
            logging.debug(f"Fin de rechercher, {len(seen)} feuilles affichées")
        except Exception as e:
            logging.error(f"Erreur lors de la recherche : {str(e)}")
            Messagebox.show_error(f"Erreur lors de la recherche : {str(e)}")

    def supprimer_feuille(self):
        """Supprime la feuille de travail sélectionnée."""
        item = self.tree.focus()
        if not item:
            Messagebox.show_warning("Veuillez sélectionner une feuille à supprimer.")
            return

        values = self.tree.item(item)["values"]
        soumission_reel = values[0]
        date_travaux = values[3]  # Date travaux est à l'index 3
        message = (
            f"⚠️ Cette action est irréversible.\n\n"
            f"Voulez-vous VRAIMENT supprimer définitivement la feuille de travail :\n\n"
            f"{soumission_reel} ({date_travaux}) ?"
        )

        confirmation = Messagebox.yesno("Confirmation de suppression", message)
        if confirmation:
            try:
                self.db_manager.delete_work_sheet(soumission_reel, date_travaux)
                Messagebox.show_info(f"La feuille de travail {soumission_reel} ({date_travaux}) a été supprimée.")
                self.load_recent_work_sheets()
            except Exception as e:
                logging.error(f"Erreur lors de la suppression de soumission_reel={soumission_reel}, date_travaux={date_travaux} : {str(e)}")
                Messagebox.show_error(f"Erreur lors de la suppression : {str(e)}")

    def ouvrir_feuille(self, event):
        """Ouvre les détails de la feuille sélectionnée."""
        item = self.tree.focus()
        if not item:
            return
        soumission_reel = self.tree.item(item)['values'][0]
        date_travaux = self.tree.item(item)['values'][3]
        
        try:
            data = self.db_manager.charger_feuille(soumission_reel, date_travaux)
            logging.debug(f"Chargement de la feuille : soumission_reel={soumission_reel}, date_travaux={date_travaux}, data={data}")
            
            if data:
                WorkSheetDetailsWindow(self.window, data, self.db_manager)
            else:
                Messagebox.show_error(f"Feuille introuvable pour {soumission_reel}, {date_travaux}")
        except Exception as e:
            logging.error(f"Erreur lors de l'ouverture de soumission_reel={soumission_reel}, date_travaux={date_travaux} : {str(e)}")
            Messagebox.show_error(f"Erreur lors de l'ouverture : {str(e)}")

class WorkSheetDetailsWindow:
    def __init__(self, parent, data, db_manager):
        self.data = data
        self.db_manager = db_manager
        self.window = ttkb.Toplevel(parent)
        self.window.title(f"Détails de la feuille - {data['soumission_reel']} ({data['date_travaux']})")
        self.window.geometry("1200x900")

        # Canvas avec scrollbar
        canvas = ttkb.Canvas(self.window)
        scrollbar = ttkb.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttkb.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        def _on_mousewheel(event):
            if self.window.winfo_exists():
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Titre principal
        tk.Label(self.scrollable_frame, text="FEUILLE DE TRAVAIL - DÉTAILS", font=("Arial", 16, "bold")).pack(pady=10)

        # Conteneur principal
        main_frame = ttkb.Frame(self.scrollable_frame)
        main_frame.pack(padx=20, pady=20)

        # Section supérieure : Champs automatiques
        upper_frame = ttkb.Frame(main_frame)
        upper_frame.pack(fill="x", pady=10)

        self.widgets = {}
        self.form_html = self.generate_form_html()
        self.parse_html(upper_frame, self.form_html)

        # Section tableau des heures
        hours_frame = tk.LabelFrame(main_frame, text="Heures chantier", font=("Arial", 12, "bold"))
        hours_frame.pack(fill="both", expand=True, pady=10, padx=10)

        self.create_hours_table(hours_frame)

        # Bouton pour calculer les coûts
        ttkb.Button(
            self.scrollable_frame,
            text="Calculer prix coûtant",
            command=lambda: CostCalculatorWindow(self.window, self.data, self.db_manager),
            bootstyle="primary"
        ).pack(pady=10)

        # Bouton de fermeture
        ttkb.Button(self.scrollable_frame, text="Fermer", command=self._on_closing, bootstyle=DANGER).pack(pady=20)

    def _on_closing(self):
        """Nettoie la liaison de l'événement MouseWheel avant de fermer la fenêtre."""
        self.window.unbind_all("<MouseWheel>")
        self.window.destroy()

    def generate_form_html(self):
        """Génère un HTML simplifié basé sur les données pour afficher les champs."""
        donnees = self.data
        heures_chantier = json.loads(donnees.get("donnees_json", "{}")).get("heures_chantier", {})
        employes = list(heures_chantier.keys()) + [""] * (11 - len(heures_chantier))

        rows_html = ""
        for i, employe in enumerate(employes, start=1):
            details = heures_chantier.get(employe, {})
            presence = "Oui" if details.get("presence") == "on" else ""
            rows_html += f"""
            <tr>
                <td>{employe}</td>
                <td>{presence}</td>
                <td>{details.get('vehicule', '')}</td>
                <td>{'Oui' if details.get('chauffeur_aller') == 'on' else ''}</td>
                <td>{'Oui' if details.get('chauffeur_retour') == 'on' else ''}</td>
                <td>{details.get('heure_debut', '')}</td>
                <td>{details.get('heure_fin', '')}</td>
                <td>{details.get('temps_transport', '')}</td>
                <td>{details.get('heures_entrepot', '')}</td>
            </tr>
            """

        return f"""
        <html>
        <body>
            <div class="form-row">
                <div class="form-group">
                    <label>Soumission</label>
                    <input name="soumission" value="{donnees.get('soumission_reel', '')}">
                </div>
                <div class="form-group">
                    <label>Client</label>
                    <input name="client" value="{donnees.get('client_reel', '')}">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Date des travaux</label>
                    <input name="date_travaux" value="{donnees.get('date_travaux', '')}">
                </div>
            </div>
            <label>Adresse</label>
            <input name="adresse_reel" value="{donnees.get('adresse_reel', '')}">
            <div class="form-row">
                <div class="form-group">
                    <label>Produit</label>
                    <input name="produit" value="{donnees.get('produit_reel', '')}">
                </div>
                <div class="form-group">
                    <label>Produit utilisé si différent</label>
                    <select name="produit_diff"><option value="{donnees.get('produit_diff', '')}">{donnees.get('produit_diff', '')}</option></select>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Superficie (pi²)</label>
                    <input name="superficie" value="{donnees.get('superficie_reel', '')}">
                </div>
                <div class="form-group">
                    <label>Épaisseur moyenne</label>
                    <input name="thickness" value="{donnees.get('thickness', '')}">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Sacs prévus</label>
                    <input name="nb_sacs_prevus" value="{donnees.get('nb_sacs_prevus', '')}">
                </div>
                <div class="form-group">
                    <label>Sacs utilisés</label>
                    <input name="sacs_utilises" value="{donnees.get('sacs_utilises_reel', '')}">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Quantité de sable théorique</label>
                    <input name="sable_total" value="{donnees.get('sable_total_reel', '')}">
                </div>
                <div class="form-group">
                    <label>Transporteur</label>
                    <input name="sable_transporter" value="{donnees.get('sable_transporter_reel', '')}">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Sable commandé (tm)</label>
                    <input name="sable_commande" value="{donnees.get('sable_commande_reel', '')}">
                </div>
                <div class="form-group">
                    <label>Surplus de sable (tm)</label>
                    <input name="sable_utilise" value="{donnees.get('sable_utilise_reel', '')}">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Type de membrane</label>
                    <input name="type_membrane" value="{donnees.get('type_membrane', '')}">
                </div>
                <div class="form-group">
                    <label>Nombre de rouleaux installés</label>
                    <input name="nb_rouleaux_installes" value="{donnees.get('nb_rouleaux_installes_reel', '')}">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>Installation membrane</label>
                    <select name="membrane_posee"><option value="{donnees.get('membrane_posee_reel', '')}">{donnees.get('membrane_posee_reel', '')}</option></select>
                </div>
                <div class="form-group">
                    <label>Marches</label>
                    <input name="marches_reel" value="{donnees.get('marches_reel', '')}">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group" style="width: 100%;">
                    <label>Notes bureau</label>
                    <textarea name="notes_bureau" rows="3">{donnees.get('notes_bureau', '')}</textarea>
                </div>
            </div>
            <div class="form-row">
                <div class="form-group" style="width: 100%;">
                    <label>Notes chantier</label>
                    <textarea name="notes_chantier" rows="4">{donnees.get('notes_reel', '')}</textarea>
                </div>
            </div>
            <h3>Heures chantier</h3>
            <table>
                {rows_html}
            </table>
        </body>
        </html>
        """

    def parse_html(self, parent, html):
        lines = html.split("\n")
        row = 0
        col = 0
        max_cols = 2
        in_table = False

        # Define field mappings from HTML names to data dictionary keys
        field_mappings = {
            'soumission': 'soumission_reel',
            'client': 'client_reel',
            'adresse_reel': 'adresse_reel',
            'date_travaux': 'date_travaux',
            'produit': 'produit_reel',
            'produit_diff': 'produit_diff',
            'superficie': 'superficie_reel',
            'thickness': 'thickness',
            'nb_sacs_prevus': 'nb_sacs_prevus',
            'sacs_utilises': 'sacs_utilises_reel',
            'sable_total': 'sable_total_reel',
            'sable_transporter': 'sable_transporter_reel',
            'sable_commande': 'sable_commande_reel',
            'sable_utilise': 'sable_utilise_reel',
            'type_membrane': 'type_membrane',
            'nb_rouleaux_installes': 'nb_rouleaux_installes_reel',
            'membrane_posee': 'membrane_posee_reel',
            'marches_reel': 'marches_reel',
            'notes_bureau': 'notes_bureau',
            'notes_chantier': 'notes_reel'
        }

        for line in lines:
            line = line.strip()
            if '<table' in line:
                in_table = True
                continue
            if in_table:
                continue  # Skip all lines after <table>

            if '<div class="form-row">' in line:
                col = 0
                row += 1
            elif '<label>' in line and '</label>' in line:
                label = re.search(r'<label>(.*?)</label>', line).group(1)
                tk.Label(parent, text=label, font=("Arial", 10)).grid(row=row, column=col * 2, sticky="e", padx=5, pady=5)
                col += 1
            elif '<input' in line:
                name = re.search(r'name="([^"]*)"', line).group(1)
                data_key = field_mappings.get(name, name)
                value = self.data.get(data_key, "")
                var = tk.StringVar(value=str(value))
                entry = tk.Entry(parent, textvariable=var, state="readonly", width=40)
                entry.grid(row=row, column=(col * 2) + 1, sticky="w", padx=5, pady=5)
                self.widgets[name] = var
                
                if col >= max_cols - 1:
                    row += 1
                    col = 0
                else:
                    col += 1
            elif '<select' in line:
                name = re.search(r'name="([^"]*)"', line).group(1)
                data_key = field_mappings.get(name, name)
                value = self.data.get(data_key, "")
                tk.Label(parent, text=value, font=("Arial", 10)).grid(row=row, column=(col * 2) + 1, sticky="w", padx=5, pady=5)
                self.widgets[name] = tk.StringVar(value=str(value))
                
                if col >= max_cols - 1:
                    row += 1
                    col = 0
                else:
                    col += 1
            elif '<textarea' in line:
                name = re.search(r'name="([^"]*)"', line).group(1)
                data_key = field_mappings.get(name, name)
                value = self.data.get(data_key, "")
                var = tk.Text(parent, height=3 if "rows=3" in line else 4, width=50)
                var.insert("1.0", value)
                var.configure(state="disabled")
                var.grid(row=row, column=1, columnspan=3, sticky="w", padx=5, pady=5)
                self.widgets[name] = var
                
                row += 1
                col = 0
            elif '<h3>' in line:
                header = re.search(r'<h3>(.*?)</h3>', line).group(1)
                tk.Label(parent, text=header, font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=4, pady=(10, 5))
                row += 1
                col = 0

    def create_hours_table(self, parent):
        heures_chantier = json.loads(self.data.get("donnees_json", "{}")).get("heures_chantier", {})
        employes = list(heures_chantier.keys()) + [""] * (11 - len(heures_chantier))
        
        headers = ["Employé", "Présence", "Véhicule", "Chauffeur Aller", "Chauffeur Retour", "Heure Début", "Heure Fin", "Total Heures", "Temps Transport", "Heures Entrepôt"]
        for col, header in enumerate(headers):
            tk.Label(parent, text=header, font=("Arial", 10, "bold"), borderwidth=1, relief="solid").grid(row=0, column=col, padx=2, pady=2, sticky="nsew")

        for i, employe in enumerate(employes, start=1):
            details = heures_chantier.get(employe, {})
            
            presence = "Oui" if details.get("presence") == "on" else ""
            vehicule = details.get("vehicule", "")
            chauffeur_aller = "Oui" if details.get("chauffeur_aller") == "on" else ""
            chauffeur_retour = "Oui" if details.get("chauffeur_retour") == "on" else ""
            heure_debut = details.get("heure_debut", "")
            heure_fin = details.get("heure_fin", "")
            temps_transport = details.get("temps_transport", "")
            heures_entrepot = details.get("heures_entrepot", "")

            # Calculer total heures
            total_heures = "-"
            if heure_debut and heure_fin:
                try:
                    fmt = "%H:%M"
                    d = datetime.strptime(heure_debut, fmt)
                    f = datetime.strptime(heure_fin, fmt)
                    diff = (f - d).seconds / 3600
                    total_heures = f"{diff:.2f}"
                except:
                    total_heures = "?"

            values = [
                employe,
                presence,
                vehicule,
                chauffeur_aller,
                chauffeur_retour,
                heure_debut,
                heure_fin,
                total_heures,
                temps_transport,
                heures_entrepot
            ]
            
            for col, value in enumerate(values):
                tk.Label(parent, text=value, borderwidth=1, relief="solid").grid(row=i, column=col, padx=2, pady=2, sticky="nsew")

        for col in range(10):
            parent.grid_columnconfigure(col, weight=1)