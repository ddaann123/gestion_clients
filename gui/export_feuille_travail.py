import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import json
import math
import xlwings as xw
from datetime import datetime
import re

from gui.manual_work_sheet_entry import ManualWorkSheetEntry
from gui.utils import check_date_on_save, validate_date, validate_date_on_focusout

class ExportFeuilleTravailWindow:
    def __init__(self, parent, submission_data, db_manager):
        self.submission_data = submission_data
        self.db_manager = db_manager

        self.window = tk.Toplevel(parent)
        self.window.title("Feuille de travail")
        self.window.geometry("700x700")

        frame = tk.Frame(self.window)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        row = 0
        tk.Label(frame, text="Feuille de travail", font=("Arial", 14, "bold")).grid(row=row, column=0, columnspan=2, pady=(0, 20))

        def add_field(label, var, editable=True):
            nonlocal row
            row += 1
            tk.Label(frame, text=label).grid(row=row, column=0, sticky="e", padx=5, pady=5)
            entry = tk.Entry(frame, textvariable=var, width=40, state="normal" if editable else "readonly")
            entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)
            if label.startswith("Date des travaux"):
                entry.configure(validate="key", validatecommand=(self.window.register(validate_date), "%P"))
                entry.bind("<FocusOut>", lambda event: validate_date_on_focusout(var, "Erreur de date des travaux"))
            return entry

        self.no_soumission_var = tk.StringVar(value=submission_data.get("submission_number", ""))
        self.nom_client_var = tk.StringVar(value=submission_data.get("client_name", ""))
        self.nom_contact_var = tk.StringVar(value=submission_data.get("contact", ""))
        self.ville_var = tk.StringVar(value=submission_data.get("ville", ""))
        self.subfloor_var = tk.StringVar(value=submission_data.get("subfloor", ""))
        self.sable_prevu_var = tk.StringVar(value=submission_data.get("sable_total", ""))
        self.sable_commande_var = tk.StringVar(value="")
        self.membrane_var = tk.StringVar(value=submission_data.get("membrane", ""))
        self.pose_membrane_var = tk.StringVar(value=submission_data.get("pose_membrane", "OUI"))
        self.notes_var = tk.StringVar(value="")
        self.cheque_var = tk.BooleanVar()
        self.type_projet_var = tk.StringVar(value="Résidentiel")
        self.marches_var = tk.StringVar(value="")
        self.total_sacs_var = tk.StringVar(value=submission_data.get("total_sacs", ""))

        # Convertir la date de YYYY-MM-DD à JJ-MM-AAAA si elle existe
        date_travaux = submission_data.get("date_travaux", "")
        if date_travaux:
            try:
                date_obj = datetime.strptime(date_travaux, "%Y-%m-%d")
                date_travaux = date_obj.strftime("%d-%m-%Y")
            except ValueError:
                date_travaux = ""
        self.date_travaux_var = tk.StringVar(value=date_travaux)

        add_field("No. Soumission :", self.no_soumission_var, editable=False)
        add_field("Compagnie :", self.nom_client_var, editable=False)
        add_field("Nom du contact :", self.nom_contact_var, editable=False)

        contact_nom = submission_data.get("contact", "")
        contacts = db_manager.get_all_contacts_with_clients()
        tel_contact = next((c["telephone"] for c in contacts if c["nom"] == contact_nom), "")
        self.telephone_contact_var = tk.StringVar(value=tel_contact)
        add_field("Téléphone du contact :", self.telephone_contact_var)

        add_field("Adresse :", self.ville_var, editable=False)
        add_field("Date des travaux (JJ-MM-AAAA) :", self.date_travaux_var)

        row += 1
        tk.Label(frame, text="Type de projet :").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        ttk.OptionMenu(frame, self.type_projet_var, self.type_projet_var.get(), "Résidentiel", "Commercial", "Institutionnel").grid(row=row, column=1, sticky="w", padx=5, pady=5)

        add_field("Type de sous-plancher :", self.subfloor_var, editable=False)

        row += 1
        tk.Label(frame, text="Chèque à ramasser :").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        tk.Checkbutton(frame, variable=self.cheque_var).grid(row=row, column=1, sticky="w", padx=5, pady=5)

        add_field("Qté sable prévue :", self.sable_prevu_var, editable=False)
        add_field("Qté sable commandée :", self.sable_commande_var)
        add_field("Membrane prévue :", self.membrane_var, editable=False)

        row += 1
        tk.Label(frame, text="Pose membrane :").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        pose_options = ["OUI AVEC DIVISIONS", "OUI SANS DIVISIONS", "OUI", "OUI POSE MIXTE", "PAR CLIENT"]
        ttk.OptionMenu(frame, self.pose_membrane_var, self.pose_membrane_var.get(), *pose_options).grid(row=row, column=1, sticky="w", padx=5, pady=5)

        row += 1
        tk.Label(frame, text="Marches d'escalier :").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(frame, textvariable=self.marches_var, width=40).grid(row=row, column=1, sticky="w", padx=5, pady=5)

        row += 1
        tk.Label(frame, text="Notes :").grid(row=row, column=0, sticky="ne", padx=5, pady=5)
        self.notes_text = tk.Text(frame, height=5, width=50)
        self.notes_text.grid(row=row, column=1, sticky="w", padx=5, pady=5)

        row += 1
        button_frame = tk.Frame(frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)

        export_btn = tk.Button(button_frame, text="Exporter feuille travail vers Excel", command=self.exporter_feuille_travail)
        export_btn.grid(row=0, column=0, padx=10)

        btn_formulaire = tk.Button(button_frame, text="Générer formulaire web", command=self.generer_formulaire_web)
        btn_formulaire.grid(row=0, column=1, padx=10)

        btn_manual_entry = tk.Button(button_frame, text="Entrer feuille travail manuellement", command=self.open_manual_work_sheet_entry)
        btn_manual_entry.grid(row=0, column=2, padx=10)

    def open_manual_work_sheet_entry(self):
        import logging
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        
        date_travaux = check_date_on_save(self.date_travaux_var.get(), "date des travaux")
        if date_travaux is None:
            logging.error("Date des travaux invalide")
            return
        
        donnees = self.submission_data.copy()
        donnees["date_travaux"] = date_travaux
        donnees["telephone"] = self.telephone_contact_var.get()
        donnees["sable_commande"] = self.sable_commande_var.get()
        donnees["type_projet"] = self.type_projet_var.get()
        donnees["cheque"] = "OUI" if self.cheque_var.get() else "NON"
        donnees["pose_membrane"] = self.pose_membrane_var.get()
        donnees["marches"] = self.marches_var.get()
        donnees["notes"] = self.notes_text.get("1.0", "end").strip()
        
        logging.debug(f"Données passées à ManualWorkSheetEntry : {donnees}")
        logging.debug(f"date_travaux : {date_travaux}")
        
        form_html = self.generer_formulaire_web_content(donnees)
        if not form_html:
            logging.error("Échec de la génération du formulaire HTML")
            messagebox.showerror("Erreur", "Impossible de générer le formulaire HTML")
            return
        
        ManualWorkSheetEntry(self.window, form_html, donnees, self.db_manager, self.pose_membrane_var.get())


    def generer_formulaire_web(self):
        date_travaux = check_date_on_save(self.date_travaux_var.get(), "date des travaux")
        if date_travaux is None:
            return

        donnees = self.submission_data.copy()
        donnees["date_travaux"] = date_travaux
        donnees["telephone"] = self.telephone_contact_var.get()
        donnees["sable_commande"] = self.sable_commande_var.get()
        donnees["type_projet"] = self.type_projet_var.get()
        donnees["cheque"] = "OUI" if self.cheque_var.get() else "NON"
        donnees["pose_membrane"] = self.pose_membrane_var.get()
        donnees["marches"] = self.marches_var.get()
        donnees["notes"] = self.notes_text.get("1.0", "end").strip()

        rouleaux = self.calculer_rouleaux_membrane(
            donnees.get('area', ''),
            donnees.get('membrane', '')
        )

        employes = [
            "KASSIM GOSSELIN", "ALEX VALOIS", "KARL", "ANTHONY ALLAIRE",
            "MARC POTHIER", "NATHAN", "ANTHONY LABBÉ", "JONATHAN GRENIER"
        ]

        rows_html = ""
        for i, nom in enumerate(employes, start=1):
            rows_html += f"""
            <tr>
                <td>{nom}</td>
                <td class="checkbox-cell"><input type="checkbox" name="presence_{i}"></td>
                <td>
                    <select name="vehicule_{i}">
                        <option value="">--</option>
                        <option value="West">West</option>
                        <option value="Inter">Inter</option>
                        <option value="Hino">Hino</option>
                        <option value="Duramax 3500">Duramax 3500</option>
                        <option value="Duramax 2500">Duramax 2500</option>
                    </select>
                </td>
                <td class="checkbox-cell"><input type="checkbox" name="chauffeur_aller_{i}"></td>
                <td class="checkbox-cell"><input type="checkbox" name="chauffeur_retour_{i}"></td>
                <td><select name="heure_debut_{i}" class="heure-select"></select></td>
                <td><select name="heure_fin_{i}" class="heure-select"></select></td>
                <td><select name="temps_transport_{i}" class="transport-select"></select></td>
                <td><select name="heures_entrepot_{i}" class="transport-select"></select></td>
            </tr>
            """
        for j in range(1, 4):
            idx = len(employes) + j
            rows_html += f"""
            <tr>
                <td><input type="text" name="nom_custom_{idx}" placeholder="Nom employé {idx}" style="width: 100px;"></td>
                <td class="checkbox-cell"><input type="checkbox" name="presence_{idx}"></td>
                <td>
                    <select name="vehicule_{idx}">
                        <option value="">--</option>
                        <option value="West">West</option>
                        <option value="Inter">Inter</option>
                        <option value="Hino">Hino</option>
                        <option value="Duramax 3500">Duramax 3500</option>
                        <option value="Duramax 2500">Duramax 2500</option>
                    </select>
                </td>
                <td class="checkbox-cell"><input type="checkbox" name="chauffeur_aller_{idx}"></td>
                <td class="checkbox-cell"><input type="checkbox" name="chauffeur_retour_{idx}"></td>
                <td><select name="heure_debut_{i}" class="heure-select"></select></td>
                <td><select name="heure_fin_{i}" class="heure-select"></select></td>
                <td><select name="temps_transport_{i}" class="transport-select"></select></td>
                <td><select name="heures_entrepot_{i}" class="transport-select"></select></td>
            </tr>
            """

        form_html = f"""
        <html>
        <head>
            <style>
                .form-row {{ display: flex; gap: 20px; margin-bottom: 10px; }}
                .form-group {{ flex: 1; }}
                .form-group label {{ display: block; margin-bottom: 5px; }}
                .form-group input, .form-group select, .form-group textarea {{ width: 100%; padding: 5px; }}
                .form-group input[readonly] {{ background-color: #f0f0f0; }}
                .heure-select, .transport-select {{ width: 72px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                textarea {{ resize: vertical; }}
            </style>
        </head>
        <body>
            <form action="/submit" method="POST">
                <div class="form-row">
                    <div class="form-group">
                        <label>Soumission</label>
                        <input name="soumission" value="{donnees['submission_number']}" readonly>
                    </div>
                    <div class="form-group">
                        <label>Client</label>
                        <input name="client" value="{donnees['client_name']}" readonly>
                    </div>
                </div>
                <label>Adresse</label>
                <input name="adresse_reel" value="{donnees['ville']}" readonly>
                <br>
                <a href="https://www.google.com/maps/dir/?api=1&destination={donnees['ville'].replace(' ', '+')}" 
                target="_blank" 
                style="display: inline-block; margin-top: 5px; padding: 6px 12px; background-color: #3498db; color: white; text-decoration: none; border-radius: 4px;">
                🗺️ Itinéraire Google Maps
                </a>
                <div class="form-row">
                    <div class="form-group">
                        <label>Contact</label>
                        <input name="contact" value="{donnees['contact']}" readonly>
                    </div>
                    <div class="form-group">
                        <label>Téléphone</label>
                        <input name="telephone" value="{donnees['telephone']}" readonly>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Chèque à ramasser</label>
                        <input name="cheque" value="{donnees['cheque']}" readonly>
                    </div>
                    <div class="form-group">
                        <label>Type de projet</label>
                        <input name="type_projet" value="{donnees['type_projet']}" readonly>
                    </div>
                </div>
                <label>Produit</label>
                <input name="produit" value="{donnees['product']}" readonly>
                <div class="form-row">
                    <div class="form-group">
                        <label>Produit utilisé si différent</label>
                        <select name="produit_diff">
                            <option value="">--</option>
                            <option value="Maxcrete complete">Maxcrete complete</option>
                            <option value="Surface Gyp">Surface Gyp</option>
                            <option value="Autre">Autre</option>
                        </select>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Superficie (pi²)</label>
                        <input name="superficie" value="{donnees['area']}" readonly>
                    </div>
                    <div class="form-group">
                        <label>Épaisseur moyenne</label>
                        <input name="thickness" value="{donnees['thickness']}" readonly>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Sacs prévus</label>
                        <input name="nb_sacs_prevus" value="{donnees['total_sacs']}" readonly>
                    </div>
                    <div class="form-group">
                        <label>Sacs utilisés *</label>
                        <input name="sacs_utilises" required style="background-color: #fff3b0;">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Quantité de sable théorique</label>
                        <input name="sable_total" value="{donnees['sable_total']}" readonly>
                    </div>
                    <div class="form-group">
                        <label>Transporteur</label>
                        <input name="sable_transporter" value="{donnees['sable_transporter']}" readonly>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Sable commandé (tm)</label>
                        <input name="sable_commande" value="{donnees['sable_commande']}">
                    </div>
                    <div class="form-group">
                        <label>Surplus de sable (tm)</label>
                        <input name="sable_utilise" required style="background-color: #fff3b0;">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Type de membrane</label>
                        <input name="type_membrane" value="{donnees['membrane']}" readonly>
                    </div>
                    <div class="form-group">
                        <label>Nombre de rouleaux prévus</label>
                        <input name="nb_rouleaux" value="{rouleaux}" readonly>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Installation membrane</label>
                        <select name="membrane_posee" style="background-color: #fff3b0;">
                            <option value="">-- Choisir --</option>
                            <option value="OUI">OUI</option>
                            <option value="NON">NON</option>
                            <option value="OUI AVEC DIVISIONS">OUI AVEC DIVISIONS</option>
                            <option value="OUI SANS DIVISIONS">OUI SANS DIVISIONS</option>
                            <option value="OUI POSE MIXTE">OUI POSE MIXTE</option>
                            <option value="PAR CLIENT">PAR CLIENT</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Nombre de rouleaux installés</label>
                        <input name="nb_rouleaux_installes" style="background-color: #fff3b0;">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Marche à remplir théorique</label>
                        <input name="marches_theorique" value="{donnees['marches']}" readonly>
                    </div>
                    <div class="form-group">
                        <label>Marche à remplir réel</label>
                        <input name="marches_reel" style="background-color: #fff3b0;">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group" style="width: 100%;">
                        <label>Notes bureau</label>
                        <textarea name="notes_bureau" rows="3" readonly>{donnees['notes']}</textarea>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group" style="width: 100%;">
                        <label>Notes chantier</label>
                        <textarea name="notes_chantier" rows="4" placeholder="Entrez les notes du chantier ici..."></textarea>
                    </div>
                </div>
                <h3>Heures chantier</h3>
                <table class="heure-chantier" border="1" cellspacing="0" cellpadding="4" style="width: 100%; table-layout: fixed;">
                    <tr>
                        <th style="width: 150px;">Employé</th>
                        <th>Prés.</th>
                        <th>Véhicule</th>
                        <th>Chauff. aller</th>
                        <th>Chauff. retour</th>
                        <th>Heure début</th>
                        <th>Heure fin</th>
                        <th>Temps transport</th>
                        <th>Heures entrepôt</th>
                    </tr>
                    {rows_html}
                </table>
                <input type="submit" value="Soumettre" class="btn btn-primary mt-3">
            </form>
        </body>
        </html>
        """

        output_path = os.path.join("static", "formulaires.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            if os.path.exists(output_path):
                with open(output_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = []

            data = [f for f in data if f["date_travaux"] != date_travaux]
            formulaire = {
                "date_travaux": date_travaux,
                "html": form_html
            }
            data.append(formulaire)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            messagebox.showinfo("Succès", f"Formulaire web généré avec succès pour {self.date_travaux_var.get()}")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération du formulaire web : {str(e)}")

    def generer_formulaire_web_content(self, donnees):
        import logging
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        
        try:
            rouleaux = self.calculer_rouleaux_membrane(
                donnees.get('area', ''),
                donnees.get('membrane', '')
            )

            employes = [
                "KASSIM GOSSELIN", "ALEX VALOIS", "KARL", "ANTHONY ALLAIRE",
                "MARC POTHIER", "NATHAN", "ANTHONY LABBÉ", "JONATHAN GRENIER"
            ]

            rows_html = ""
            for i, nom in enumerate(employes, start=1):
                rows_html += f"""
                <tr>
                    <td>{nom}</td>
                    <td><input type="checkbox" name="presence_{i}"></td>
                    <td>
                        <select name="vehicule_{i}">
                            <option value="">--</option>
                            <option value="West">West</option>
                            <option value="Inter">Inter</option>
                            <option value="Hino">Hino</option>
                            <option value="Duramax 3500">Duramax 3500</option>
                            <option value="Duramax 2500">Duramax 2500</option>
                        </select>
                    </td>
                    <td><input type="checkbox" name="chauffeur_aller_{i}"></td>
                    <td><input type="checkbox" name="chauffeur_retour_{i}"></td>
                    <td><select name="heure_debut_{i}" class="heure-select"></select></td>
                    <td><select name="heure_fin_{i}" class="heure-select"></select></td>
                    <td><select name="temps_transport_{i}" class="transport-select"></select></td>
                    <td><select name="heures_entrepot_{i}" class="transport-select"></select></td>
                </tr>
                """
            for j in range(1, 4):
                idx = len(employes) + j
                rows_html += f"""
                <tr>
                    <td><input type="text" name="nom_custom_{idx}" placeholder="Nom employé {idx}" style="width: 100px;"></td>
                    <td><input type="checkbox" name="presence_{idx}"></td>
                    <td>
                        <select name="vehicule_{idx}">
                            <option value="">--</option>
                            <option value="West">West</option>
                            <option value="Inter">Inter</option>
                            <option value="Hino">Hino</option>
                            <option value="Duramax 3500">Duramax 3500</option>
                            <option value="Duramax 2500">Duramax 2500</option>
                        </select>
                    </td>
                    <td><input type="checkbox" name="chauffeur_aller_{idx}"></td>
                    <td><input type="checkbox" name="chauffeur_retour_{idx}"></td>
                    <td><select name="heure_debut_{idx}" class="heure-select"></select></td>
                    <td><select name="heure_fin_{idx}" class="heure-select"></select></td>
                    <td><select name="temps_transport_{idx}" class="transport-select"></select></td>
                    <td><select name="heures_entrepot_{idx}" class="transport-select"></select></td>
                </tr>
                """

            html = f"""
            <html>
            <head>
                <style>
                    .form-row {{ display: flex; gap: 20px; margin-bottom: 10px; }}
                    .form-group {{ flex: 1; }}
                    .form-group label {{ display: block; margin-bottom: 5px; }}
                    .form-group input, .form-group select, .form-group textarea {{ width: 100%; padding: 5px; }}
                    .form-group input[readonly] {{ background-color: #f0f0f0; }}
                    .heure-select, .transport-select {{ width: 72px; }}
                    table {{ width: 100%; border-collapse: collapse; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    textarea {{ resize: vertical; }}
                </style>
            </head>
            <body>
                <div class="form-row">
                    <div class="form-group">
                        <label>Soumission</label>
                        <input name="soumission" value="{donnees.get('submission_number', '')}" readonly>
                    </div>
                    <div class="form-group">
                        <label>Client</label>
                        <input name="client" value="{donnees.get('client_name', '')}" readonly>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Date des travaux</label>
                        <input name="date_travaux" value="{donnees.get('date_travaux', '')}" readonly>
                    </div>
                </div>
                <label>Adresse</label>
                <input name="adresse_reel" value="{donnees.get('ville', '')}" readonly>
                <br>
                <a href="https://www.google.com/maps/dir/?api=1&destination={donnees.get('ville', '').replace(' ', '+')}" 
                target="_blank" 
                style="display: inline-block; margin-top: 5px; padding: 6px 12px; background-color: #3498db; color: white; text-decoration: none; border-radius: 4px;">
                🗺️ Itinéraire Google Maps
                </a>
                <div class="form-row">
                    <div class="form-group">
                        <label>Contact</label>
                        <input name="contact" value="{donnees.get('contact', '')}" readonly>
                    </div>
                    <div class="form-group">
                        <label>Téléphone</label>
                        <input name="telephone" value="{donnees.get('telephone', '')}" readonly>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Chèque à ramasser</label>
                        <input name="cheque" value="{donnees.get('cheque', '')}" readonly>
                    </div>
                    <div class="form-group">
                        <label>Type de projet</label>
                        <input name="type_projet" value="{donnees.get('type_projet', '')}" readonly>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Produit</label>
                        <input name="produit" value="{donnees.get('product', '')}" readonly>
                    </div>
                    <div class="form-group">
                        <label>Produit utilisé si différent</label>
                        <select name="produit_diff">
                            <option value="">--</option>
                            <option value="Maxcrete complete">Maxcrete complete</option>
                            <option value="Surface Gyp">Surface Gyp</option>
                            <option value="Autre">Autre</option>
                        </select>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Superficie (pi²)</label>
                        <input name="superficie" value="{donnees.get('area', '')}" readonly>
                    </div>
                    <div class="form-group">
                        <label>Épaisseur moyenne</label>
                        <input name="thickness" value="{donnees.get('thickness', '')}" readonly>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Sacs prévus</label>
                        <input name="nb_sacs_prevus" value="{donnees.get('total_sacs', '')}" readonly>
                    </div>
                    <div class="form-group">
                        <label>Sacs utilisés *</label>
                        <input name="sacs_utilises" required style="background-color: #fff3b0;">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Quantité de sable théorique</label>
                        <input name="sable_total" value="{donnees.get('sable_total', '')}" readonly>
                    </div>
                    <div class="form-group">
                        <label>Transporteur</label>
                        <input name="sable_transporter" value="{donnees.get('sable_transporter', '')}" readonly>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Sable commandé (tm)</label>
                        <input name="sable_commande" value="{donnees.get('sable_commande', '')}">
                    </div>
                    <div class="form-group">
                        <label>Surplus de sable (tm)</label>
                        <input name="sable_utilise" required style="background-color: #fff3b0;">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Type de membrane</label>
                        <input name="type_membrane" value="{donnees.get('membrane', '')}" readonly>
                    </div>
                    <div class="form-group">
                        <label>Nombre de rouleaux prévus</label>
                        <input name="nb_rouleaux" value="{rouleaux}" readonly>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Installation membrane</label>
                        <select name="membrane_posee" style="background-color: #fff3b0;">
                            <option value="">-- Choisir --</option>
                            <option value="OUI">OUI</option>
                            <option value="NON">NON</option>
                            <option value="OUI AVEC DIVISIONS">OUI AVEC DIVISIONS</option>
                            <option value="OUI SANS DIVISIONS">OUI SANS DIVISIONS</option>
                            <option value="OUI POSE MIXTE">OUI POSE MIXTE</option>
                            <option value="PAR CLIENT">PAR CLIENT</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Nombre de rouleaux installés</label>
                        <input name="nb_rouleaux_installes" style="background-color: #fff3b0;">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>Marche à remplir théorique</label>
                        <input name="marches_theorique" value="{donnees.get('marches', '')}" readonly>
                    </div>
                    <div class="form-group">
                        <label>Marche à remplir réel</label>
                        <input name="marches_reel" style="background-color: #fff3b0;">
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group" style="width: 100%;">
                        <label>Notes bureau</label>
                        <textarea name="notes_bureau" rows="3" readonly>{donnees.get('notes', '')}</textarea>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group" style="width: 100%;">
                        <label>Notes chantier</label>
                        <textarea name="notes_chantier" rows="4" placeholder="Entrez les notes du chantier ici..."></textarea>
                    </div>
                </div>
                <h3>Heures chantier</h3>
                <table border="1" cellspacing="0" cellpadding="4" style="width: 100%; table-layout: fixed;">
                    <tr>
                        <th style="width: 150px;">Employé</th>
                        <th>Prés.</th>
                        <th>Véhicule</th>
                        <th>Chauff. aller</th>
                        <th>Chauff. retour</th>
                        <th>Heure début</th>
                        <th>Heure fin</th>
                        <th>Temps transport</th>
                        <th>Heures entrepôt</th>
                    </tr>
                    {rows_html}
                </table>
            </body>
            </html>
            """
            logging.debug(f"HTML généré : {html[:200]}...")
            logging.debug(f"date_travaux dans donnees : {donnees.get('date_travaux')}")
            return html
        except Exception as e:
            logging.error(f"Erreur dans generer_formulaire_web_content : {str(e)}")
            return ""

    def exporter_feuille_travail(self):
        date_travaux = check_date_on_save(self.date_travaux_var.get(), "date des travaux")
        if date_travaux is None:
            return

        donnees = self.submission_data.copy()
        donnees["date_travaux"] = date_travaux
        donnees["telephone"] = self.telephone_contact_var.get()
        donnees["sable_commande"] = self.sable_commande_var.get()
        donnees["type_projet"] = self.type_projet_var.get()
        donnees["cheque"] = "OUI" if self.cheque_var.get() else "NON"
        donnees["pose_membrane"] = self.pose_membrane_var.get()
        donnees["marches"] = self.marches_var.get()
        donnees["notes"] = self.notes_text.get("1.0", "end").strip()

        date_formattee = datetime.strptime(date_travaux, "%Y-%m-%d").strftime("%d-%m-%Y")

        def safe_filename(text):
            return re.sub(r'[\\/*?:"<>|]', "", text).strip()

        client_safe = safe_filename(donnees["client_name"])
        date_safe = safe_filename(date_formattee)

        nom_fichier = f"Feuille travail - {client_safe} - {date_safe}.xlsx"
        export_dir = "G:/Mon disque/FEUILLE DE TRAVAIL"
        os.makedirs(export_dir, exist_ok=True)
        output_path = os.path.join(export_dir, nom_fichier)

        try:
            template_path = "C:/gestion_clients/models/Feuille_travail.xlsx"
            wb = xw.Book(template_path)
            ws = wb.sheets[0]

            ws["A3"].value = donnees["submission_number"].upper()
            ws["F3"].value = date_formattee.upper()
            ws["A6"].value = donnees["client_name"].upper()
            ws["F6"].value = donnees["contact"].upper()
            ws["F8"].value = donnees["telephone"].upper()
            ws["A10"].value = donnees["ville"].upper()
            ws["A13"].value = donnees["product"].upper()
            ws["C13"].value = donnees["area"].upper()
            ws["I13"].value = donnees["thickness"].upper()
            ws["F14"].value = donnees["subfloor"].upper()
            ws["F15"].value = donnees["type_projet"].upper()
            ws["C16"].value = donnees["cheque"].upper()
            ws["I16"].value = donnees["distance"].upper()
            ws["A18"].value = donnees["total_sacs"].upper()
            ws["I18"].value = donnees["sable_total"].upper()
            ws["I19"].value = donnees["sable_commande"].upper()
            ws["I21"].value = donnees["sable_transporter"].upper()
            ws["C24"].value = donnees["membrane"].upper()
            ws["C25"].value = donnees["pose_membrane"].upper()
            ws["A33"].value = donnees["marches"].upper()
            ws["A35"].value = donnees["notes"].upper()
            rouleaux = self.calculer_rouleaux_membrane(donnees.get("area", ""), donnees.get("membrane", ""))
            ws["J24"].value = rouleaux

            wb.save(output_path)
            wb.close()
            messagebox.showinfo("Succès", f"Feuille de travail exportée avec succès : {nom_fichier}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'exportation vers Excel : {str(e)}")

    def calculer_rouleaux_membrane(self, surface_str, membrane_nom):
        try:
            surface = float(surface_str.replace(",", "").strip())
        except ValueError:
            surface = 0

        couverture_pi2 = None
        for m in self.db_manager.get_membranes():
            if m[1].strip().lower() == membrane_nom.strip().lower():
                couverture_pi2 = m[2]
                break

        if couverture_pi2 and surface > 0:
            try:
                couverture_float = float(couverture_pi2)
                return math.ceil(surface / couverture_float)
            except Exception:
                return ""
        return ""