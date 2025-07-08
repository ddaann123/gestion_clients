import tkinter as tk
import ttkbootstrap as ttkb
import math
import re
import json
from datetime import datetime
import logging
import sqlite3
from ttkbootstrap.constants import *

# Configurer le logging
logging.basicConfig(level=logging.DEBUG)

class CostCalculatorWindow:
    def __init__(self, parent, data, db_manager):
        self.data = data
        self.db_manager = db_manager
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
            if self.window.winfo_exists():
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)

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

        # Récupérer les valeurs depuis la table submissions
        submission_details = self.db_manager.get_submission_details(self.data.get("soumission_reel", ""))
        logging.debug(f"submission_details: {submission_details}")
        submission_product = submission_details.get("product", "")
        submission_prix_par_sac = self.clean_monetary_string(submission_details.get("prix_par_sac", "0.0"))
        submission_sable_transporter = submission_details.get("sable_transporter", "")
        submission_truck_tonnage = submission_details.get("truck_tonnage", "")
        submission_transport_sector = submission_details.get("transport_sector", "")
        submission_sealant = submission_details.get("sealant", "")
        submission_prix_heures = (self.clean_monetary_string(submission_details.get("prix_total_heures_chantier", "0.0")) +
                                 self.clean_monetary_string(submission_details.get("prix_total_heures_transport", "0.0")))
        submission_prix_machinerie = self.clean_monetary_string(submission_details.get("prix_total_machinerie", "0.0"))
        submission_prix_pension = self.clean_monetary_string(submission_details.get("prix_total_pension", "0.0"))
        submission_type_main = submission_details.get("type_main", "Cimentier/journalier")
        submission_type_machinerie = submission_details.get("type_machinerie", "Materiel roulant job std")
        logging.debug(f"type_main: {submission_type_main}, type_machinerie: {submission_type_machinerie}")

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
                if label == "Date des travaux":
                    var.set(self.data.get("date_travaux", ""))
                elif label == "Soumission":
                    var.set(self.data.get("soumission_reel", ""))
                elif label == "Client":
                    var.set(self.data.get("client_reel", ""))
                elif label == "Adresse":
                    var.set(self.data.get("adresse_reel", ""))
                elif label == "Taux de change actuel":
                    var.set("1.40")
                    entry.bind("<KeyRelease>", lambda event: self.update_all_calculations())
                elif label == "Surface (pi²)":
                    var.set(self.data.get("superficie_reel", ""))
                    entry.bind("<KeyRelease>", lambda event: self.update_all_calculations())

        # Section 2 : 21 lignes × 4 colonnes (20 labels + 1 en-tête)
        section2_frame = tk.LabelFrame(main_frame, text="Détails des coûts", font=("Arial", 12, "bold"))
        section2_frame.pack(fill="both", expand=True, pady=10)

        section2_headers = ["Description", "Réel", "Soumission", "Différence"]
        for col, header in enumerate(section2_headers):
            tk.Label(section2_frame, text=header, font=("Arial", 10, "bold"), borderwidth=1, relief="solid").grid(row=0, column=col, padx=2, pady=2, sticky="nsew")

        section2_labels = [
            "Produit",
            "Quantité de sacs",
            "Prix produit",
            "Prix total produits",
            "Qté sable commandée",
            "Surplus de sable",
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

        # Champs à inclure dans le calcul du total et des différences
        self.total_fields = [
            "Prix total produits",
            "Prix total sable",
            "Prix total apprêts",
            "Prix total membrane",
            "Main d'œuvre",
            "Machinerie",
            "Pension",
            "Ajustements",
            "Total"
        ]

        # Récupérer les camions et secteurs pour le transporteur initial
        initial_transporteur = self.data.get("sable_transporter_reel", "")
        camions = self.get_camions_for_transporteur(initial_transporteur)
        secteurs = self.get_secteurs_for_transporteur(initial_transporteur)
        default_secteur = submission_transport_sector if initial_transporteur == submission_sable_transporter and submission_transport_sector in secteurs else (secteurs[0] if secteurs else "Aucun secteur disponible")

        for row, label in enumerate(section2_labels, start=1):
            tk.Label(section2_frame, text=label, font=("Arial", 10), borderwidth=1, relief="solid").grid(row=row, column=0, padx=2, pady=2, sticky="nsew")
            for col in range(1, 4):  # Colonnes Réel, Soumission, Différence
                if label == "Type de camion" and col == 1:
                    var = tk.StringVar()
                    combobox = ttkb.Combobox(section2_frame, textvariable=var, values=camions, width=18, state="normal")
                    combobox.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
                    self.widgets[f"{label}_{section2_headers[col]}"] = var
                    if camions:
                        var.set(camions[0])
                    combobox.bind("<<ComboboxSelected>>", lambda event: self.update_all_calculations())
                elif label == "Secteur" and col == 1:
                    var = tk.StringVar()
                    combobox = ttkb.Combobox(section2_frame, textvariable=var, values=secteurs, width=18, state="normal")
                    combobox.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
                    self.widgets[f"{label}_{section2_headers[col]}"] = var
                    var.set(default_secteur)
                    combobox.bind("<<ComboboxSelected>>", lambda event: self.update_all_calculations())
                else:
                    var = tk.StringVar()
                    entry = tk.Entry(section2_frame, textvariable=var, width=20)
                    entry.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
                    self.widgets[f"{label}_{section2_headers[col]}"] = var
                    if label in self.total_fields and col == 3:
                        entry.configure(state="readonly")  # Différence en lecture seule
                    elif label == "Total" and col in (1, 2):
                        entry.configure(state="readonly")  # Total en lecture seule
                    elif label == "Ajustements" and col in (1, 2):
                        entry.bind("<KeyRelease>", lambda event: self.update_all_calculations())
                    elif label == "Fournisseur sable" and col == 1:
                        entry.bind("<KeyRelease>", lambda event: self.update_all_calculations())
                    elif label == "Quantité de sacs" and col in (1, 2):
                        entry.bind("<KeyRelease>", lambda event: self.update_all_calculations())

                # Pré-remplir les champs disponibles
                if label == "Produit" and col == 1:
                    var.set(self.data.get("produit_reel", ""))
                elif label == "Produit" and col == 2:
                    var.set(submission_product)
                elif label == "Quantité de sacs" and col == 1:
                    var.set(self.data.get("sacs_utilises_reel", ""))
                elif label == "Quantité de sacs" and col == 2:
                    var.set(self.data.get("nb_sacs_prevus", ""))
                elif label == "Prix produit" and col == 1:
                    taux_change = self.widgets["Taux de change actuel"].get()
                    try:
                        taux_change = float(taux_change)
                    except ValueError:
                        taux_change = 1.40
                    product_name = self.data.get("produit_reel", "")
                    prix_produit_reel = self.calculate_prix_par_sac(product_name, taux_change, self.db_manager)
                    var.set(prix_produit_reel)
                elif label == "Prix produit" and col == 2:
                    var.set(f"{submission_prix_par_sac:.2f}")
                elif label == "Prix total produits" and col == 1:
                    qte_sacs = self.data.get("sacs_utilises_reel", "")
                    prix_produit = self.widgets["Prix produit_Réel"].get()
                    prix_total_produits = self.calculate_prix_total_produits(qte_sacs, prix_produit)
                    var.set(prix_total_produits)
                elif label == "Prix total produits" and col == 2:
                    qte_sacs = self.data.get("nb_sacs_prevus", "")
                    prix_produit = submission_prix_par_sac
                    prix_total_produits = self.calculate_prix_total_produits(qte_sacs, prix_produit)
                    var.set(prix_total_produits)
                elif label == "Qté sable commandée" and col == 1:
                    var.set(self.data.get("sable_commande_reel", ""))
                elif label == "Qté sable commandée" and col == 2:
                    var.set(self.data.get("sable_commande_reel", ""))
                elif label == "Surplus de sable" and col == 1:
                    var.set(self.data.get("sable_utilise_reel", ""))
                elif label == "Fournisseur sable" and col == 1:
                    var.set(self.data.get("sable_transporter_reel", ""))
                elif label == "Fournisseur sable" and col == 2:
                    var.set(submission_sable_transporter)
                elif label == "Type de camion" and col == 2:
                    var.set(submission_truck_tonnage)
                elif label == "Nombre de voyages" and col == 1:
                    transporteur = self.widgets["Fournisseur sable_Réel"].get()
                    if not transporteur or transporteur.lower() == "none":
                        var.set("0")
                    else:
                        qte_sable = self.data.get("sable_commande_reel", "")
                        camion = self.widgets["Type de camion_Réel"].get()
                        nombre_voyages = self.calculate_nombre_voyages(qte_sable, camion)
                        var.set(nombre_voyages)
                elif label == "Nombre de voyages" and col == 2:
                    if not submission_sable_transporter or submission_sable_transporter.lower() == "none":
                        var.set("0")
                    else:
                        qte_sable = self.data.get("sable_commande_reel", "")
                        camion = submission_truck_tonnage
                        nombre_voyages = self.calculate_nombre_voyages(qte_sable, camion)
                        var.set(nombre_voyages)
                elif label == "Secteur" and col == 2:
                    var.set(submission_transport_sector)
                elif label == "Prix total sable" and col == 1:
                    transporteur = self.widgets["Fournisseur sable_Réel"].get()
                    secteur = self.widgets["Secteur_Réel"].get()
                    qte_sable = self.data.get("sable_commande_reel", "")
                    nombre_voyages = self.widgets["Nombre de voyages_Réel"].get()
                    prix_total_sable = self.calculate_prix_total_sable(transporteur, secteur, qte_sable, nombre_voyages)
                    var.set(prix_total_sable)
                elif label == "Prix total sable" and col == 2:
                    transporteur = submission_sable_transporter
                    secteur = submission_transport_sector
                    qte_sable = self.data.get("sable_commande_reel", "")
                    nombre_voyages = self.widgets["Nombre de voyages_Soumission"].get()
                    prix_total_sable = self.calculate_prix_total_sable(transporteur, secteur, qte_sable, nombre_voyages)
                    var.set(prix_total_sable)
                elif label == "Apprêts" and col in (1, 2):
                    var.set(submission_sealant)
                elif label == "Prix total apprêts" and col in (1, 2):
                    surface = self.widgets["Surface (pi²)"].get()
                    appret = submission_sealant
                    prix_total_apprets = self.calculate_prix_total_apprets(surface, appret)
                    var.set(prix_total_apprets)
                elif label == "Type de membrane" and col in (1, 2):
                    var.set(self.data.get("type_membrane", ""))
                elif label == "Nombre rouleaux" and col == 1:
                    var.set(self.data.get("nb_rouleaux_installes_reel", ""))
                elif label == "Nombre rouleaux" and col == 2:
                    membrane = self.data.get("type_membrane", "")
                    if membrane.lower() == "aucune":
                        var.set("0")
                    else:
                        surface = self.widgets["Surface (pi²)"].get()
                        nombre_rouleaux = self.calculate_nombre_rouleaux_soumission(surface, membrane)
                        var.set(nombre_rouleaux)
                elif label == "Prix total membrane" and col == 1:
                    membrane = self.data.get("type_membrane", "")
                    nombre_rouleaux = self.data.get("nb_rouleaux_installes_reel", "")
                    prix_total_membrane = self.calculate_prix_total_membrane(membrane, nombre_rouleaux)
                    var.set(prix_total_membrane)
                elif label == "Prix total membrane" and col == 2:
                    membrane = self.data.get("type_membrane", "")
                    nombre_rouleaux = self.widgets["Nombre rouleaux_Soumission"].get()
                    prix_total_membrane = self.calculate_prix_total_membrane(membrane, nombre_rouleaux)
                    var.set(prix_total_membrane)
                elif label == "Main d'œuvre" and col == 1:
                    prix_main_doeuvre_reel = self.calculate_main_doeuvre_reel(submission_type_main)
                    var.set(f"{prix_main_doeuvre_reel:.2f}")
                elif label == "Main d'œuvre" and col == 2:
                    var.set(f"{submission_prix_heures:.2f}")
                elif label == "Machinerie" and col == 1:
                    prix_machinerie_reel = self.calculate_machinerie_reel(submission_type_machinerie)
                    var.set(f"{prix_machinerie_reel:.2f}")
                elif label == "Machinerie" and col == 2:
                    var.set(f"{submission_prix_machinerie:.2f}")
                elif label == "Pension" and col in (1, 2):
                    var.set(f"{submission_prix_pension:.2f}")

        for col in range(4):
            section2_frame.grid_columnconfigure(col, weight=1)

        # Calculer les différences initiales
        self.calculate_totals()

        # Section 3 : 4 lignes × 2 colonnes (3 labels + 1 espace)
        section3_frame = tk.LabelFrame(main_frame, text="Résumé", font=("Arial", 12, "bold"))
        section3_frame.pack(fill="x", pady=10)

        section3_labels = [
            "Facture no.",
            "Montant facturé av.tx",
            "Profit",
            "Ratio de mélange réel"
            ""  # Espace
        ]

        for row, label in enumerate(section3_labels):
            if label:
                tk.Label(section3_frame, text=label, font=("Arial", 10)).grid(row=row, column=0, sticky="e", padx=5, pady=5)
                var = tk.StringVar()
                entry = tk.Entry(section3_frame, textvariable=var, width=40)
                entry.grid(row=row, column=1, sticky="w", padx=5, pady=5)
                self.widgets[label] = var
                if label == "Profit" or label == "Ratio de mélange réel":
                    entry.configure(state="readonly")
                elif label == "Montant facturé av.tx":
                    entry.bind("<KeyRelease>", lambda event: self.update_all_calculations())

        # Calculer le profit initial
        self.update_profit()

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
            text="Recalcul",
            command=self.update_all_calculations,
            bootstyle="primary"
        ).pack(side="left", padx=10)

        ttkb.Button(
            button_frame,
            text="Annuler",
            command=self.window.destroy,
            bootstyle="danger"
        ).pack(side="left", padx=10)


    def calculate_ratio_reel(self):
        """Calcule le ratio réel : (((Qté sable commandée - Surplus de sable) * 2205) / 110) / Quantité de sacs."""
        try:
            qte_sable = self.widgets["Qté sable commandée_Réel"].get()
            surplus_sable = self.widgets["Surplus de sable_Réel"].get()
            qte_sacs = self.widgets["Quantité de sacs_Réel"].get()
            
            qte_sable = float(qte_sable) if qte_sable else 0.0
            surplus_sable = float(surplus_sable) if surplus_sable else 0.0
            qte_sacs = float(qte_sacs) if qte_sacs else 1.0  # Éviter division par zéro
            
            ratio = (((qte_sable - surplus_sable) * 2205) / 110) / qte_sacs
            return f"{ratio:.1f}"  # Arrondi au dixième
        except Exception as e:
            logging.error(f"Erreur dans calculate_ratio_reel: {e}")
            return "Erreur"



    def clean_monetary_string(self, value):
        """Nettoie une chaîne monétaire (ex. '2520.00 $') et la convertit en float."""
        try:
            cleaned = re.sub(r'[^\d.]', '', str(value))
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0

    def parse_heures_chantier(self):
        """Parse le JSON heures_chantier et calcule les heures et temps de transport."""
        try:
            donnees_json = self.data.get("donnees_json", "{}")
            donnees = json.loads(donnees_json)
            heures_chantier = donnees.get("heures_chantier", {})
            total_heures = 0.0
            total_heures_transport = 0.0
            employee_count = 0

            for employe, details in heures_chantier.items():
                if details.get("presence") != "on":
                    continue
                employee_count += 1

                # Calculer les heures de chantier (heure_fin - heure_debut)
                heure_debut = details.get("heure_debut", "")
                heure_fin = details.get("heure_fin", "")
                if heure_debut and heure_fin:
                    try:
                        debut = datetime.strptime(heure_debut, "%H:%M")
                        fin = datetime.strptime(heure_fin, "%H:%M")
                        delta = fin - debut
                        heures = delta.total_seconds() / 3600.0  # Convertir en heures décimales
                        total_heures += heures
                        logging.debug(f"Employé {employe}: heures = {heures:.2f} (de {heure_debut} à {heure_fin})")
                    except ValueError as e:
                        logging.error(f"Erreur de parsing pour {employe}: {heure_debut} - {heure_fin}, erreur: {e}")
                        continue

                # Récupérer temps_transport
                temps_transport = details.get("temps_transport", "0:00")
                try:
                    hours, minutes = map(int, temps_transport.split(":"))
                    heures_transport = hours + (minutes / 60.0)
                    total_heures_transport += heures_transport
                    logging.debug(f"Employé {employe}: temps_transport = {heures_transport:.2f}")
                except ValueError as e:
                    logging.error(f"Erreur de parsing temps_transport pour {employe}: {temps_transport}, erreur: {e}")
                    continue

            # Calculer les moyennes si des employés sont présents
            avg_heures = total_heures / employee_count if employee_count > 0 else 0.0
            avg_heures_transport = total_heures_transport / employee_count if employee_count > 0 else 0.0

            logging.debug(f"Total heures: {total_heures:.2f}, Total heures transport: {total_heures_transport:.2f}, Employés: {employee_count}, Moyenne heures: {avg_heures:.2f}, Moyenne transport: {avg_heures_transport:.2f}")
            return {
                "total_heures": total_heures,
                "total_heures_transport": total_heures_transport,
                "avg_heures": avg_heures,
                "avg_heures_transport": avg_heures_transport
            }
        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"Erreur lors du parsing du JSON heures_chantier: {e}")
            return {
                "total_heures": 0.0,
                "total_heures_transport": 0.0,
                "avg_heures": 0.0,
                "avg_heures_transport": 0.0
            }

    def calculate_main_doeuvre_reel(self, metier):
        """Calcule le coût de main d'œuvre (Réel) : (somme heures * taux_horaire_chantier) + (somme heures_transport * taux_horaire_transport)."""
        try:
            # Récupérer les heures depuis le JSON
            heures_data = self.parse_heures_chantier()
            total_heures = heures_data["total_heures"]
            total_heures_transport = heures_data["total_heures_transport"]

            # Récupérer les taux horaires depuis main_doeuvre
            main_doeuvre_details = self.db_manager.get_main_doeuvre_details(metier)
            taux_horaire_chantier = float(main_doeuvre_details.get("taux_horaire_chantier", 30.0))  # Default 30.0
            taux_horaire_transport = float(main_doeuvre_details.get("taux_horaire_transport", 20.0))  # Default 20.0
            logging.debug(f"Main d'oeuvre: metier={metier}, taux_horaire_chantier={taux_horaire_chantier}, taux_horaire_transport={taux_horaire_transport}")

            if not metier:
                logging.warning("metier est vide, utilisant taux horaires par défaut")
            if taux_horaire_chantier == 0.0 or taux_horaire_transport == 0.0:
                logging.warning(f"Aucun taux horaire trouvé pour metier={metier}, utilisant taux par défaut")

            # Calculer le coût total
            total = (total_heures * taux_horaire_chantier) + (total_heures_transport * taux_horaire_transport)
            logging.debug(f"Main d'oeuvre: total_heures={total_heures:.2f}, total_heures_transport={total_heures_transport:.2f}, coût={total:.2f}")
            return total
        except Exception as e:
            logging.error(f"Erreur dans calculate_main_doeuvre_reel: {e}")
            return 0.0

    def calculate_machinerie_reel(self, type_machinerie):
        """Calcule le coût de machinerie (Réel) : (moyenne heures + moyenne temps_transport) * taux_horaire."""
        try:
            # Récupérer les heures et temps de transport moyens depuis le JSON
            heures_data = self.parse_heures_chantier()
            avg_heures = heures_data["avg_heures"]
            avg_heures_transport = heures_data["avg_heures_transport"]
            total_heures_machinerie = avg_heures + avg_heures_transport

            # Récupérer le taux horaire depuis machinerie
            machinerie_details = self.db_manager.get_machinerie_details(type_machinerie)
            taux_horaire = float(machinerie_details.get("taux_horaire", 50.0))  # Default 50.0
            if taux_horaire == 0.0:
                taux_horaire = 50.0  # Forcer le taux par défaut si 0.0
                logging.warning(f"Aucun taux horaire trouvé pour type_machinerie={type_machinerie}, utilisant taux par défaut 50.0")
            logging.debug(f"Machinerie: type_machinerie={type_machinerie}, taux_horaire={taux_horaire}")

            if not type_machinerie:
                logging.warning("type_machinerie est vide, utilisant taux horaire par défaut")

            # Calculer le coût total
            total = total_heures_machinerie * taux_horaire
            logging.debug(f"Machinerie: avg_heures={avg_heures:.2f}, avg_heures_transport={avg_heures_transport:.2f}, total_heures_machinerie={total_heures_machinerie:.2f}, coût={total:.2f}")
            return total
        except Exception as e:
            logging.error(f"Erreur dans calculate_machinerie_reel: {e}")
            return 0.0

    def calculate_totals(self):
        """Calcule les totaux pour les colonnes Réel et Soumission, les différences, et met à jour les champs."""
        try:
            total_reel = 0.0
            total_soumission = 0.0

            for field in self.total_fields[:-1]:  # Exclure "Total" pour le calcul
                reel_value = self.widgets[f"{field}_Réel"].get()
                soumission_value = self.widgets[f"{field}_Soumission"].get()

                try:
                    reel_float = float(reel_value) if reel_value and reel_value != "Erreur" else 0.0
                    soumission_float = float(soumission_value) if soumission_value and soumission_value != "Erreur" else 0.0
                    total_reel += reel_float
                    total_soumission += soumission_float

                    # Calculer et mettre à jour la différence
                    difference = soumission_float - reel_float
                    self.widgets[f"{field}_Différence"].set(f"{difference:.2f}")
                except ValueError:
                    logging.error(f"Erreur lors du calcul de la différence pour {field}")
                    self.widgets[f"{field}_Différence"].set("Erreur")

            # Mettre à jour les champs Total
            self.widgets["Total_Réel"].set(f"{total_reel:.2f}")
            self.widgets["Total_Soumission"].set(f"{total_soumission:.2f}")
            self.widgets["Total_Différence"].set(f"{total_soumission - total_reel:.2f}")

            # Mettre à jour le profit
            self.update_profit()

        except Exception as e:
            logging.error(f"Erreur dans calculate_totals: {e}")

    def update_profit(self):
        """Met à jour le champ Profit : Montant facturé av.tx - Total_Réel."""
        try:
            montant_facture = self.widgets["Montant facturé av.tx"].get()
            total_reel = self.widgets["Total_Réel"].get()
            montant_facture_float = float(montant_facture) if montant_facture and montant_facture != "Erreur" else 0.0
            total_reel_float = float(total_reel) if total_reel and total_reel != "Erreur" else 0.0
            profit = montant_facture_float - total_reel_float
            self.widgets["Profit"].set(f"{profit:.2f}")
        except Exception as e:
            logging.error(f"Erreur dans update_profit: {e}")
            self.widgets["Profit"].set("Erreur")

    def update_all_calculations(self):
        """Met à jour tous les calculs dynamiques : prix produit, apprêts, rouleaux, sable, main d'œuvre, machinerie, totaux, et profit."""
        # Mettre à jour les calculs dépendants de Taux de change et Surface
        self.update_prix_produit_reel()
        self.update_apprets_and_rouleaux()
        self.update_voyages_and_prix_sable_reel()
        self.update_prix_total_sable_reel()
        self.update_prix_total_produits()

        # Mettre à jour Main d'œuvre et Machinerie
        submission_details = self.db_manager.get_submission_details(self.data.get("soumission_reel", ""))
        submission_type_main = submission_details.get("type_main", "Cimentier/journalier")
        submission_type_machinerie = submission_details.get("type_machinerie", "Materiel roulant job std")
        self.widgets["Main d'œuvre_Réel"].set(f"{self.calculate_main_doeuvre_reel(submission_type_main):.2f}")
        self.widgets["Machinerie_Réel"].set(f"{self.calculate_machinerie_reel(submission_type_machinerie):.2f}")

        # Mettre à jour le Ratio de mélange réel
        self.widgets["Ratio de mélange réel"].set(self.calculate_ratio_reel())


        # Mettre à jour les totaux et différences
        self.calculate_totals()

    def update_prix_produit_reel(self):
        """Met à jour le champ Prix produit (Réel) lorsque le taux de change change."""
        taux_change = self.widgets["Taux de change actuel"].get()
        try:
            taux_change = float(taux_change)
        except ValueError:
            taux_change = 1.40
        product_name = self.data.get("produit_reel", "")
        prix_produit_reel = self.calculate_prix_par_sac(product_name, taux_change, self.db_manager)
        self.widgets["Prix produit_Réel"].set(prix_produit_reel)
        # Recalculer Prix total produits (Réel)
        qte_sacs = self.data.get("sacs_utilises_reel", "")
        prix_total_produits = self.calculate_prix_total_produits(qte_sacs, prix_produit_reel)
        self.widgets["Prix total produits_Réel"].set(prix_total_produits)

    def update_apprets_and_rouleaux(self):
        """Met à jour Prix total apprêts et Nombre de rouleaux (Soumission) lorsque Surface change."""
        surface = self.widgets["Surface (pi²)"].get()
        appret = self.widgets["Apprêts_Réel"].get()
        prix_total_apprets = self.calculate_prix_total_apprets(surface, appret)
        self.widgets["Prix total apprêts_Réel"].set(prix_total_apprets)
        self.widgets["Prix total apprêts_Soumission"].set(prix_total_apprets)
        membrane = self.data.get("type_membrane", "")
        nombre_rouleaux = self.calculate_nombre_rouleaux_soumission(surface, membrane)
        self.widgets["Nombre rouleaux_Soumission"].set(nombre_rouleaux)
        prix_total_membrane = self.calculate_prix_total_membrane(membrane, nombre_rouleaux)
        self.widgets["Prix total membrane_Soumission"].set(prix_total_membrane)

    def update_prix_total_produits(self):
        """Met à jour Prix total produits lorsque Quantité de sacs change."""
        qte_sacs_reel = self.data.get("sacs_utilises_reel", "")
        prix_produit_reel = self.widgets["Prix produit_Réel"].get()
        prix_total_produits_reel = self.calculate_prix_total_produits(qte_sacs_reel, prix_produit_reel)
        self.widgets["Prix total produits_Réel"].set(prix_total_produits_reel)
        qte_sacs_soumission = self.data.get("nb_sacs_prevus", "")
        prix_produit_soumission = self.widgets["Prix produit_Soumission"].get()
        prix_total_produits_soumission = self.calculate_prix_total_produits(qte_sacs_soumission, prix_produit_soumission)
        self.widgets["Prix total produits_Soumission"].set(prix_total_produits_soumission)

    def get_camions_for_transporteur(self, transporteur):
        """Récupère la liste des camions pour un transporteur donné."""
        try:
            sable_data = self.db_manager.get_sable()
            camions = [row[2] for row in sable_data if row[1] == transporteur]
            camions = sorted(list(set(camions)))
            return camions if camions else ["Aucun camion disponible"]
        except Exception:
            return ["Erreur"]

    def get_secteurs_for_transporteur(self, transporteur):
        """Récupère la liste des secteurs pour un transporteur donné."""
        try:
            sable_data = self.db_manager.get_sable()
            secteurs = [row[3] for row in sable_data if row[1] == transporteur]
            secteurs = sorted(list(set(secteurs)))
            return secteurs if secteurs else ["Aucun secteur disponible"]
        except Exception:
            return ["Erreur"]

    def get_sable_details(self, transporteur, secteur):
        """Récupère prix_voyage et prix_sable pour un transporteur et un secteur."""
        try:
            sable_data = self.db_manager.get_sable()
            for row in sable_data:
                if row[1] == transporteur and row[3] == secteur:
                    return {"prix_voyage": row[4], "prix_sable": row[5]}
            return {"prix_voyage": 0.0, "prix_sable": 0.0}
        except Exception:
            return {"prix_voyage": 0.0, "prix_sable": 0.0}

    def get_appret_details(self, nom_produit):
        """Récupère couverture_pi2 et prix pour un apprêt donné."""
        try:
            apprets = self.db_manager.get_appret_details()
            for appret in apprets:
                if appret[0] == nom_produit:
                    return {"couverture_pi2": appret[1], "prix": appret[2]}
            return {"couverture_pi2": 1.0, "prix": 0.0}
        except Exception:
            return {"couverture_pi2": 1.0, "prix": 0.0}

    def get_membrane_details(self, modele_membrane):
        """Récupère couverture_pi2 et prix_rouleau pour une membrane donnée."""
        try:
            membranes = self.db_manager.get_membrane_details()
            for membrane in membranes:
                if membrane[0] == modele_membrane:
                    return {"couverture_pi2": membrane[1], "prix_rouleau": membrane[2]}
            return {"couverture_pi2": 1.0, "prix_rouleau": 0.0}
        except Exception:
            return {"couverture_pi2": 1.0, "prix_rouleau": 0.0}

    def calculate_nombre_voyages(self, qte_sable, camion):
        """Calcule le nombre de voyages : ceil(Qté sable commandée / Type de camion)."""
        try:
            qte_sable = float(qte_sable) if qte_sable else 0.0
            camion_tonnage = float(camion) if camion and camion != "Aucun camion disponible" else 1.0
            return str(math.ceil(qte_sable / camion_tonnage)) if qte_sable > 0 else "0"
        except ValueError:
            return "0"

    def calculate_prix_total_sable(self, transporteur, secteur, qte_sable, nombre_voyages):
        """Calcule le prix total sable : (Nombre de voyages * prix_voyage) + (Qté sable * prix_sable)."""
        try:
            qte_sable = float(qte_sable) if qte_sable else 0.0
            nombre_voyages = float(nombre_voyages) if nombre_voyages else 0.0
            sable_details = self.get_sable_details(transporteur, secteur)
            prix_voyage = float(sable_details["prix_voyage"])
            prix_sable = float(sable_details["prix_sable"])
            total = (nombre_voyages * prix_voyage) + (qte_sable * prix_sable)
            return f"{total:.2f}"
        except Exception:
            return "Erreur"

    def calculate_prix_total_apprets(self, surface, appret):
        """Calcule le prix total apprêts : (Surface / couverture_pi2) * prix."""
        try:
            surface = float(surface) if surface else 0.0
            appret_details = self.get_appret_details(appret)
            couverture_pi2 = float(appret_details["couverture_pi2"]) if appret_details["couverture_pi2"] else 1.0
            prix = float(appret_details["prix"])
            total = (surface / couverture_pi2) * prix
            return f"{total:.2f}"
        except Exception:
            return "Erreur"

    def calculate_nombre_rouleaux_soumission(self, surface, membrane):
        """Calcule le nombre de rouleaux (Soumission) : ceil(Surface / couverture_pi2)."""
        try:
            if membrane.lower() == "aucune":
                return "0"
            surface = float(surface) if surface else 0.0
            membrane_details = self.get_membrane_details(membrane)
            couverture_pi2 = float(membrane_details["couverture_pi2"]) if membrane_details["couverture_pi2"] else 1.0
            return str(math.ceil(surface / couverture_pi2)) if surface > 0 else "0"
        except ValueError:
            return "0"

    def calculate_prix_total_membrane(self, membrane, nombre_rouleaux):
        """Calcule le prix total membrane : Nombre de rouleaux * prix_rouleau."""
        try:
            if membrane.lower() == "aucune":
                return "0.00"
            nombre_rouleaux = float(nombre_rouleaux) if nombre_rouleaux else 0.0
            membrane_details = self.get_membrane_details(membrane)
            prix_rouleau = float(membrane_details["prix_rouleau"])
            total = nombre_rouleaux * prix_rouleau
            return f"{total:.2f}"
        except Exception:
            return "Erreur"

    def calculate_prix_total_produits(self, qte_sacs, prix_produit):
        """Calcule le prix total produits : Quantité de sacs * Prix produit."""
        try:
            qte_sacs = float(qte_sacs) if qte_sacs else 0.0
            prix_produit = float(prix_produit) if prix_produit else 0.0
            total = qte_sacs * prix_produit
            return f"{total:.2f}"
        except ValueError:
            return "Erreur"

    def update_camions_and_secteurs(self):
        """Met à jour les combobox Type de camion et Secteur (Réel) lorsque le transporteur change."""
        transporteur = self.widgets["Fournisseur sable_Réel"].get()
        camions = self.get_camions_for_transporteur(transporteur)
        combobox_camion = self.widgets["Type de camion_Réel"].master
        combobox_camion["values"] = camions
        if camions:
            self.widgets["Type de camion_Réel"].set(camions[0])
        else:
            self.widgets["Type de camion_Réel"].set("Aucun camion disponible")
        secteurs = self.get_secteurs_for_transporteur(transporteur)
        combobox_secteur = self.widgets["Secteur_Réel"].master
        combobox_secteur["values"] = secteurs
        submission_transporteur = self.widgets["Fournisseur sable_Soumission"].get()
        submission_secteur = self.widgets["Secteur_Soumission"].get()
        default_secteur = submission_secteur if transporteur == submission_transporteur and submission_secteur in secteurs else (secteurs[0] if secteurs else "Aucun secteur disponible")
        self.widgets["Secteur_Réel"].set(default_secteur)
        self.update_voyages_and_prix_sable_reel()

    def update_voyages_and_prix_sable_reel(self):
        """Met à jour Nombre de voyages et Prix total sable (Réel) lorsque Type de camion change."""
        transporteur = self.widgets["Fournisseur sable_Réel"].get()
        if not transporteur or transporteur.lower() == "none":
            self.widgets["Nombre de voyages_Réel"].set("0")
        else:
            qte_sable = self.data.get("sable_commande_reel", "")
            camion = self.widgets["Type de camion_Réel"].get()
            nombre_voyages = self.calculate_nombre_voyages(qte_sable, camion)
            self.widgets["Nombre de voyages_Réel"].set(nombre_voyages)
        transporteur = self.widgets["Fournisseur sable_Réel"].get()
        secteur = self.widgets["Secteur_Réel"].get()
        qte_sable = self.data.get("sable_commande_reel", "")
        nombre_voyages = self.widgets["Nombre de voyages_Réel"].get()
        prix_total_sable = self.calculate_prix_total_sable(transporteur, secteur, qte_sable, nombre_voyages)
        self.widgets["Prix total sable_Réel"].set(prix_total_sable)

    def update_prix_total_sable_reel(self):
        """Met à jour Prix total sable (Réel) lorsque Secteur change."""
        transporteur = self.widgets["Fournisseur sable_Réel"].get()
        secteur = self.widgets["Secteur_Réel"].get()
        qte_sable = self.data.get("sable_commande_reel", "")
        nombre_voyages = self.widgets["Nombre de voyages_Réel"].get()
        prix_total_sable = self.calculate_prix_total_sable(transporteur, secteur, qte_sable, nombre_voyages)
        self.widgets["Prix total sable_Réel"].set(prix_total_sable)

    @staticmethod
    def calculate_prix_par_sac(product_name, usd_cad_rate, db_manager):
        """Calcule le prix par sac en CAD pour un produit donné."""
        try:
            product_mapping = {
                "Maxcrete": "MAXCRETE COMPLETE (2500-3500 PSI)",
                "Surface Gyp": "SURFACE GYP (2500-3500 PSI)",
                "Autre": None
            }
            table_product_name = product_mapping.get(product_name, product_name)
            if table_product_name is None:
                logging.debug(f"Aucun produit correspondant pour {product_name}")
                return "0.00"
            usd_cad_rate = float(usd_cad_rate)
            produits = db_manager.get_produit_details()
            produit = next((p for p in produits if p[0] == table_product_name), None)
            if not produit:
                logging.debug(f"Produit {table_product_name} non trouvé dans la table produits")
                return "0.00"
            # Déstructurer les 7 colonnes, en ignorant type_produit et couverture_1_pouce
            nom, prix_base, devise_base, prix_transport, devise_transport, _, _ = produit
            prix_base_cad = prix_base * usd_cad_rate if devise_base == "USD" else prix_base
            prix_transport_cad = prix_transport * usd_cad_rate if devise_transport == "USD" else prix_transport
            total = prix_base_cad + prix_transport_cad
            logging.debug(f"Prix par sac pour {nom}: prix_base={prix_base_cad:.2f}, prix_transport={prix_transport_cad:.2f}, total={total:.2f}")
            return f"{total:.2f}"
        except Exception as e:
            logging.error(f"Erreur dans calculate_prix_par_sac pour {product_name}: {e}")
            return "Erreur"
        
    def _on_closing(self):
        """Nettoie la liaison de l'événement MouseWheel avant de fermer la fenêtre."""
        self.window.unbind_all("<MouseWheel>")
        self.window.destroy()

    def save_to_table(self):
        """Sauvegarde les données dans la table costs avec vérification des doublons et mise à jour de est_calcule."""
        try:
            # Récupérer les données des champs
            submission_number = self.widgets["Soumission"].get()
            date_travaux = self.widgets["Date des travaux"].get()
            client = self.widgets["Client"].get()
            adresse = self.widgets["Adresse"].get()
            surface = self.widgets["Surface (pi²)"].get()
            facture_no = self.widgets["Facture no."].get()
            montant_facture_av_tx = self.widgets["Montant facturé av.tx"].get()
            total_reel = self.widgets["Total_Réel"].get()
            profit = self.widgets["Profit"].get()
            ratio_reel = self.widgets["Ratio de mélange réel"].get()

            # Convertir les valeurs numériques
            try:
                surface = float(surface) if surface else 0.0
                montant_facture_av_tx = float(montant_facture_av_tx) if montant_facture_av_tx and montant_facture_av_tx != "Erreur" else 0.0
                total_reel = float(total_reel) if total_reel and total_reel != "Erreur" else 0.0
                profit = float(profit) if profit and profit != "Erreur" else 0.0
                ratio_reel = float(ratio_reel) if ratio_reel and ratio_reel != "Erreur" else 0.0
            except ValueError as e:
                logging.error(f"Erreur lors de la conversion des valeurs numériques : {e}")
                tk.messagebox.showerror("Erreur", "Veuillez vérifier les valeurs numériques (Surface, Montant facturé, Total, Profit, Ratio de mélange réel).")
                return

            # Valider les champs obligatoires
            if not submission_number:
                tk.messagebox.showerror("Erreur", "Le numéro de soumission est requis.")
                return
            if not date_travaux:
                tk.messagebox.showerror("Erreur", "La date des travaux est requise.")
                return

            # Vérifier si une entrée existe déjà pour ce submission_number et date_travaux
            if self.db_manager.check_cost_exists(submission_number, date_travaux):
                if not tk.messagebox.askyesno(
                    "Avertissement",
                    f"Une entrée existe déjà pour le numéro de soumission {submission_number} et la date {date_travaux}. "
                    "Voulez-vous écraser les données existantes ?"
                ):
                    tk.messagebox.showinfo("Annulé", "Les données n'ont pas été sauvegardées.")
                    return
                # Supprimer l'entrée existante avant d'insérer la nouvelle
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "DELETE FROM costs WHERE submission_number = ? AND date_travaux = ?",
                        (submission_number, date_travaux)
                    )
                    conn.commit()
                    logging.info(f"Entrée existante supprimée pour submission_number={submission_number}, date_travaux={date_travaux}")

            # Sauvegarder dans la table costs
            self.db_manager.save_costs(
                submission_number=submission_number,
                date_travaux=date_travaux,
                client=client,
                adresse=adresse,
                surface=surface,
                facture_no=facture_no,
                montant_facture_av_tx=montant_facture_av_tx,
                total_reel=total_reel,
                profit=profit,
                ratio_reel=ratio_reel
            )

            # Mettre à jour est_calcule dans chantiers_reels
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE chantiers_reels SET est_calcule = 1 WHERE soumission_reel = ?",
                    (submission_number,)
                )
                conn.commit()
                logging.info(f"chantiers_reels mis à jour: est_calcule=1 pour soumission_reel={submission_number}")

            tk.messagebox.showinfo("Succès", f"Données sauvegardées pour la soumission {submission_number}, date {date_travaux}.")
            self.window.destroy()

        except sqlite3.IntegrityError:
            logging.error(f"Erreur d'intégrité : combinaison submission_number={submission_number}, date_travaux={date_travaux} déjà existante.")
            tk.messagebox.showerror("Erreur", f"Une entrée existe déjà pour la soumission {submission_number} et la date {date_travaux}.")
        except Exception as e:
            logging.error(f"Erreur dans save_to_table : {e}")
            tk.messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {str(e)}")