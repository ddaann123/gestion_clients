from ttkbootstrap import ttk

import tkinter as tk
import re
import json
from tkinter import messagebox
from datetime import datetime
from .submission_calcs import (calculate_distance, calculate_surface_per_mob, get_truck_tonnages, calculate_prix_par_sac, 
                               calculate_total_sacs, calculate_prix_total_sacs, calculer_quantite_sable, calculer_nombre_voyages_sable, 
                               calculer_prix_total_sable, calculer_heures_chantier, calculer_heures_transport, calculer_prix_total_machinerie, 
                               calculer_prix_total_pension, valider_entree_numerique
)
from gui.export_devis import ExportDevisWindow
from gui.select_contact_window import ContactSelector
from gui.export_feuille_travail import ExportFeuilleTravailWindow
from gui.utils import validate_date, validate_date_on_focusout, check_date_on_save





from config import DEFAULT_USD_CAD_RATE, THICKNESS_OPTIONS, SUBFLOOR_OPTIONS, DEFAULT_SUBFLOOR, POSE_MEMBRANE_OPTIONS



def safe_float(value):
    try:
        return float(value.replace('$', '').replace(',', '').replace(' ', '').strip())
    except Exception:
        return 0.0


class ProjectNotesWindow:
    def __init__(self, parent, notes_data=None):
        self.window = tk.Toplevel(parent)
        self.window.title("Notes de Projet")
        self.window.geometry("600x650")
        self.window.transient(parent)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)  # Gestion de la fermeture
        self.window.grab_set()

        self.notes_data = notes_data or {}  # Données passées depuis SubmissionForm
        self.initial_data = notes_data.copy() if notes_data else {}  # Sauvegarde initiale pour comparaison

        frame = ttk.LabelFrame(self.window, text="Détails des Notes", padding=10)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Type de projet
        tk.Label(frame, text="Type de projet :").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.project_type_var = tk.StringVar(value=self.notes_data.get("project_type", "Résidentiel"))
        tk.OptionMenu(frame, self.project_type_var, "Résidentiel", "Commercial", "Institutionnel").grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Type d'immeuble
        tk.Label(frame, text="Type d'immeuble :").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.building_type_var = tk.StringVar(value=self.notes_data.get("building_type", ""))
        tk.Entry(frame, textvariable=self.building_type_var, width=30).grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Plans disponibles
        tk.Label(frame, text="Plans disponibles :").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.plans_var = tk.BooleanVar(value=self.notes_data.get("plans", False))
        tk.Checkbutton(frame, variable=self.plans_var).grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Surface évaluée par client
        tk.Label(frame, text="Surface évaluée par client :").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.client_surface_var = tk.BooleanVar(value=self.notes_data.get("client_surface", False))
        tk.Checkbutton(frame, variable=self.client_surface_var).grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Plancher radiant
        tk.Label(frame, text="Plancher radiant :").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.radiant_floor_var = tk.StringVar(value=self.notes_data.get("radiant_floor", "Aucun"))
        tk.OptionMenu(frame, self.radiant_floor_var, "Électrique", "Hydronique", "Aucun").grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        # Fini de plancher
        tk.Label(frame, text="Fini de plancher :").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.floor_finish_var = tk.StringVar(value=self.notes_data.get("floor_finish", ""))
        tk.Entry(frame, textvariable=self.floor_finish_var, width=30).grid(row=5, column=1, padx=5, pady=5, sticky="w")

        # Travaux au-dessus du sol
        tk.Label(frame, text="Travaux au-dessus du sol :").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.above_ground_var = tk.BooleanVar(value=self.notes_data.get("above_ground", False))
        tk.Checkbutton(frame, variable=self.above_ground_var).grid(row=6, column=1, padx=5, pady=5, sticky="w")

        # Date requise des travaux
        tk.Label(frame, text="Date requise des travaux :").grid(row=7, column=0, padx=5, pady=5, sticky="w")
        self.required_date_var = tk.StringVar(value=self.notes_data.get("required_date", ""))
        tk.Entry(frame, textvariable=self.required_date_var, width=30).grid(row=7, column=1, padx=5, pady=5, sticky="w")

        # Type de nivellement
        tk.Label(frame, text="Type de nivellement :").grid(row=8, column=0, padx=5, pady=5, sticky="w")
        self.leveling_type_var = tk.StringVar(value=self.notes_data.get("leveling_type", "Profil existant"))
        tk.OptionMenu(frame, self.leveling_type_var, "Profil existant", "Pièce par pièce", "Niveau exact").grid(row=8, column=1, padx=5, pady=5, sticky="ew")

        # Notes variées
        tk.Label(frame, text="Notes variées :").grid(row=9, column=0, padx=5, pady=5, sticky="w")
        self.notes_var = tk.Text(frame, height=10, width=30)
        self.notes_var.insert("1.0", self.notes_data.get("notes", ""))
        self.notes_var.grid(row=9, column=1, padx=5, pady=5, sticky="ew")

        # Boutons Enregistrer et Fermer
        tk.Button(self.window, text="Enregistrer", command=self.save_notes).pack(pady=5)
        tk.Button(self.window, text="Fermer", command=self.on_closing).pack(pady=5)

    def save_notes(self):
        self.notes_data = {
            "project_type": self.project_type_var.get(),
            "building_type": self.building_type_var.get(),
            "plans": self.plans_var.get(),
            "client_surface": self.client_surface_var.get(),
            "radiant_floor": self.radiant_floor_var.get(),
            "floor_finish": self.floor_finish_var.get(),
            "above_ground": self.above_ground_var.get(),
            "required_date": self.required_date_var.get(),
            "leveling_type": self.leveling_type_var.get(),
            "notes": self.notes_var.get("1.0", tk.END).strip()
        }
        self.window.destroy()

    def on_closing(self):
        if self.notes_data != self.initial_data:
            if messagebox.askyesno("Confirmation", "Des modifications non enregistrées seront perdues. Voulez-vous continuer ?"):
                self.window.destroy()
        else:
            self.window.destroy()

class DetailedSurfaceWindow:
    def __init__(self, parent, surface_data=None):
        self.window = tk.Toplevel(parent)
        self.window.title("Surface Détaillée")
        self.window.geometry("400x650")
        self.window.transient(parent)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)  # Gestion de la fermeture
        self.window.grab_set()

        self.surface_data = surface_data or {}  # Données passées depuis SubmissionForm
        self.initial_data = surface_data.copy() if surface_data else {}  # Sauvegarde initiale

        frame = ttk.LabelFrame(self.window, text="Détails des Surfaces", padding=10)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        # En-têtes des colonnes
        tk.Label(frame, text="Étage").grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        tk.Label(frame, text="Surface par étage (pi²)").grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # Champs pour 15 lignes
        self.floor_vars = {}
        self.surface_vars = {}
        for i in range(15):
            row = i + 1
            self.floor_vars[row] = tk.StringVar(value=self.surface_data.get(f"floor_{row}", ""))
            self.surface_vars[row] = tk.StringVar(value=self.surface_data.get(f"surface_{row}", ""))
            tk.Entry(frame, textvariable=self.floor_vars[row], width=15).grid(row=row, column=0, padx=5, pady=2, sticky="ew")
            tk.Entry(frame, textvariable=self.surface_vars[row], width=15).grid(row=row, column=1, padx=5, pady=2, sticky="ew")

        # Calcul de la somme
        tk.Label(frame, text="Total :").grid(row=16, column=0, padx=5, pady=5, sticky="e")
        self.total_var = tk.StringVar()
        tk.Label(frame, textvariable=self.total_var, width=15).grid(row=16, column=1, padx=5, pady=5, sticky="w")
        self.update_total()  # Initialisation du total

        # Binder les changements pour recalculer la somme
        for var in self.surface_vars.values():
            var.trace("w", self.update_total)

        # Boutons Enregistrer et Fermer
        tk.Button(self.window, text="Enregistrer", command=self.save_surfaces).pack(pady=5)
        tk.Button(self.window, text="Fermer", command=self.on_closing).pack(pady=5)

    def update_total(self, *args):
        try:
            total = sum(int(self.surface_vars[row].get() or 0) for row in range(1, 16))
            self.total_var.set(str(total))
        except ValueError:
            self.total_var.set("Erreur")

    def save_surfaces(self):
        self.surface_data = {f"floor_{i}": self.floor_vars[i].get() for i in range(1, 16)}
        self.surface_data.update({f"surface_{i}": self.surface_vars[i].get() for i in range(1, 16)})
        self.window.destroy()

    def on_closing(self):
        if self.surface_data != self.initial_data:
            if messagebox.askyesno("Confirmation", "Des modifications non enregistrées seront perdues. Voulez-vous continuer ?"):
                self.window.destroy()
        else:
            self.window.destroy()

class SubmissionForm:
     
    def __init__(self, parent, db_manager, selected_client=None, selected_contact=None, existing_submission=None):
        self.db_manager = db_manager
        self.selected_client = selected_client
        self.selected_contact = selected_contact
        self.notes_data = {}  # Stocke les notes temporairement
        self.surface_data = {}  # Stocke les surfaces temporairement
        self.total_surface_var = tk.StringVar(value="0")  # Stocke la surface totale
        self.mobilizations_var = tk.StringVar(value="1.0")  # Nombre de mobilisations
        self.surface_per_mob_var = tk.StringVar(value="0.0")  # Surface par mobilisation
        self.area_var = tk.StringVar(value="")  # Superficie (pi²)
        self.area_var.trace("w", self.update_sealant_total)  # 🔁 observe changement de superficie
        self.area_var.trace("w", self.update_total_sacs)
        self.product_var = tk.StringVar()  # Produit sélectionné
        self.product_var.trace("w", self.update_ratio_options)
        self.product_var.trace("w", self.update_prix_par_sac)
        self.product_var.trace("w", self.update_total_sacs)
        self.ratio_var = tk.StringVar()  # Ratio sélectionné
        self.ratio_var.trace("w", self.update_total_sacs)
        self.usd_cad_rate_var = tk.StringVar(value=str(DEFAULT_USD_CAD_RATE))  # Taux de change USD/CAD
        self.usd_cad_rate_var.trace("w", self.update_prix_par_sac)
        self.thickness_var = tk.StringVar(value="1-1/2\"")  # Épaisseur, défaut à 1-1/2"
        self.thickness_var.trace("w", self.update_total_sacs)
        self.subfloor_var = tk.StringVar(value=DEFAULT_SUBFLOOR)  # Type de sous-plancher
        self.subfloor_var.trace("w", self.update_sealant_default)
        self.membrane_var = tk.StringVar(value="Aucune")  # Type de membrane, défaut à "Aucune"
        self.pose_membrane_var = tk.StringVar(value="Aucune")  # Pose membrane, défaut à "Aucune"
        # Variables pour les nouveaux champs
        self.sable_transporter_var = tk.StringVar()  # Transporteur de sable
        self.truck_tonnage_var = tk.StringVar()  # Tonnage camion
        self.transport_sector_var = tk.StringVar()  # Secteur de transport
        self.thaw_work_var = tk.BooleanVar(value=False)  # Travaux en dégel, défaut à False
        self.sealant_var = tk.StringVar(value="Aucun")  # Apprets et scellants, défaut à "Aucun"
        self.sealant_total_var = tk.StringVar(value="0.00")
        self.sealant_var.trace("w", self.update_sealant_total)  # 🔁 observe changement de produit scellant
        self.prix_par_sac_var = tk.StringVar(value="0.00")
        self.total_sacs_var = tk.StringVar(value="0")
        self.nb_sacs_var = tk.StringVar(value="0")
        self.prix_total_sacs_var = tk.StringVar(value="0.00")
        self.nb_sacs_var.trace("w", self.update_prix_total_sacs)
        self.prix_par_sac_var.trace("w", self.update_prix_total_sacs)
        self.total_sacs_var.trace("w", self.update_prix_total_sacs)
        self.sable_total_var = tk.StringVar(value="0")
        self.total_sacs_var.trace("w", self.update_sable_total)
        self.ratio_var.trace("w", self.update_sable_total)
        self.voyage_sable_var = tk.StringVar()
        self.tonnage_camion_var = tk.StringVar(value="")  # Valeur par défaut vide ou "10" si tu préfères
        self.nombre_voyages_var = tk.StringVar(value="0")
        self.sable_total_var.trace("w", self.update_nombre_voyages)
        self.truck_tonnage_var.trace("w", self.update_nombre_voyages)
        self.prix_total_sable_var = tk.StringVar(value="0.00")
        self.sable_transporter_var.trace("w", lambda *args: self.update_prix_total_sable())
        self.truck_tonnage_var.trace("w", lambda *args: self.update_prix_total_sable())
        self.sable_total_var.trace("w", lambda *args: self.update_prix_total_sable())
        self.nombre_voyages_var.trace("w", lambda *args: self.update_prix_total_sable())
        self.sable_transporter_var.trace("w", self.update_prix_total_sable)
        self.truck_tonnage_var.trace("w", self.update_prix_total_sable)
        self.champs = {}
        self.nombre_hommes_var = tk.StringVar(value="6")
        self.heures_chantier_var = tk.StringVar(value="0")
        self.heures_transport_var = tk.StringVar(value="0")
        self.heures_transport_var.set("0")
        self.distance_var = tk.StringVar()
        self.distance_var.trace("w", self.update_heures_transport)
        self.area_var.trace("w", self.update_heures_chantier)
        self.prix_total_machinerie_var = tk.StringVar(value="0.00")
        self.heures_chantier_var.trace("w", self.update_prix_total_machinerie)
        self.prix_total_pension_var = tk.StringVar(value="0.00")
        self.nombre_hommes_var.trace("w", self.update_prix_total_pension)
        self.prix_total_heures_chantier_var = tk.StringVar(value="0.00")
        self.nombre_hommes_var.trace("w", self.update_prix_total_heures_chantier)
        self.heures_chantier_var.trace("w", self.update_prix_total_heures_chantier)
        self.prix_total_heures_transport_var = tk.StringVar(value="0.00")
        self.nombre_hommes_var.trace("w", self.update_prix_total_heures_transport)
        self.heures_transport_var.trace("w", self.update_prix_total_heures_transport)
        self.ajustement1_var = tk.StringVar(value="0.00")
        self.ajustement2_var = tk.StringVar(value="0.00")
        self.ajustement3_var = tk.StringVar(value="0.00")
        self.reperes_var = tk.StringVar(value="0.00")
        self.sous_total_ajustements_var = tk.StringVar(value="0.00")
        self.ajustement1_var.trace("w", self.update_sous_total_ajustements)
        self.ajustement2_var.trace("w", self.update_sous_total_ajustements)
        self.ajustement3_var.trace("w", self.update_sous_total_ajustements)
        self.reperes_var.trace("w", self.update_sous_total_ajustements)
        self.sous_total_fournisseurs_var = tk.StringVar(value="0.00")
        self.sous_total_main_machinerie_var = tk.StringVar(value="0.00 $")
        self.total_prix_coutants_var = tk.StringVar(value="0.00 $")
        self.admin_profit_var = tk.StringVar(value="0 %")
        self.admin_profit_montant_var = tk.StringVar(value="0.00 $")
        self.prix_vente_client_var = tk.StringVar(value="0.00 $")
        self.admin_profit_var.trace("w", self.update_admin_profit_montant)
        self.admin_profit_var.trace("w", self.format_admin_profit_percent)
        self.prix_unitaire_var = tk.StringVar(value="0.00 $")
        self.prix_vente_client_var.trace("w", self.update_prix_unitaire)
        self.area_var.trace("w", self.update_prix_unitaire)
        self.prix_total_immeuble_var = tk.StringVar(value="0.00")
        self.prix_pi2_ajuste_var = tk.StringVar(value="0.00")
        self.prix_total_ajuste_var = tk.StringVar(value="0.00")
        self.prix_unitaire_var.trace_add("write", self.update_prix_total_immeuble)
        self.total_surface_var.trace_add("write", self.update_prix_total_immeuble)
        self.admin_profit_var.trace("w", self.update_admin_profit_et_dependants)
        self.prix_vente_client_var.trace("w", self.update_dependants_apres_vente)
        self.transport_sector_var.trace_add("write", self.update_sable_total)
        self.truck_tonnage_var.trace_add("write", self.update_sable_total)
        self.sable_transporter_var.trace_add("write", self.update_sable_total)
        self.sealant_total_var.trace_add("write", self.update_sous_total_fournisseurs)
        self.prix_total_sacs_var.trace_add("write", self.update_sous_total_fournisseurs)
        self.prix_total_sable_var.trace_add("write", self.update_sous_total_fournisseurs)
        standard_width = 15 #LARGEUR UNIFORME POUR LES CHAMPS






   


        




        self.window = tk.Toplevel(parent)
        self.window.title("Nouvelle Soumission")

        self.window.geometry("1000x900")  # ← tu peux ajuster ici largeur x hauteur


        # ---- SCROLLBAR CONFIGURATION ----
        container = ttk.Frame(self.window)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ---- Nouveau parent pour les widgets ----
        self.main_frame = scrollable_frame

        self.window.transient(parent)
        self.window.grab_set()

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)



        # Frame Informations Générales
        gen_frame = ttk.LabelFrame(self.main_frame, text="INFORMATIONS GENERALES", padding=10)
        gen_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Champ Client (pré-rempli et non modifiable)
        tk.Label(gen_frame, text="Client :").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.client_var = tk.StringVar()
        if self.selected_client:
            self.client_var.set(self.selected_client)
        else:
            self.client_var.set("Aucun client sélectionné")
        tk.Entry(gen_frame, textvariable=self.client_var, state="disabled", width=30).grid(row=0, column=1, padx=5, pady=5)

        # Champ Contact (pré-rempli et non modifiable)
        tk.Label(gen_frame, text="Contact :").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.contact_var = tk.StringVar()
        self.contact_var.set(self.selected_contact if self.selected_contact else "")
        tk.Entry(gen_frame, textvariable=self.contact_var, state="disabled", width=30).grid(row=1, column=1, padx=5, pady=5)

        # Champ Date de soumission
        tk.Label(gen_frame, text="Date de soumission (JJ-MM-AAAA) :").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.date_var = tk.StringVar()
        self.date_var.set(datetime.now().strftime("%d-%m-%Y"))  # Date par défaut : 05-07-2025
        date_entry = tk.Entry(gen_frame, textvariable=self.date_var, width=30)
        date_entry.grid(row=2, column=1, padx=5, pady=5)
        date_entry.configure(validate="key", validatecommand=(self.window.register(validate_date), "%P"))
        date_entry.bind("<FocusOut>", lambda event: validate_date_on_focusout(self.date_var, "Erreur de date de soumission"))

        # Champ No Soumission
        tk.Label(gen_frame, text="No Soumission :").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.submission_number_var = tk.StringVar()
        tk.Entry(gen_frame, textvariable=self.submission_number_var, state="disabled", width=30).grid(row=3, column=1, padx=5, pady=5)

        # Frame Détails du Projet
        proj_frame = ttk.LabelFrame(self.main_frame, text="DETAILS DU PROJET", padding=10)
        proj_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Champ Projet (2 lignes) et bouton Notes de projet
        tk.Label(proj_frame, text="Projet :").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.projet_var = tk.Text(proj_frame, height=2, width=30, font=("TkDefaultFont", 9))
        self.projet_var.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        tk.Button(proj_frame, text="Notes de projet", command=self.open_project_notes).grid(row=0, column=2, padx=5, pady=5)

        # Champ Ville
        tk.Label(proj_frame, text="Adresse-Ville :").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.ville_var = tk.StringVar()
        tk.Entry(proj_frame, textvariable=self.ville_var, width=35).grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Champ Distance chantier aller-simple (km) et bouton Calculer
        tk.Label(proj_frame, text="Distance aller-simple (km) :").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(proj_frame, textvariable=self.distance_var, width=20, justify="center").grid(row=2, column=1, padx=5, pady=5, sticky="w")
        tk.Button(proj_frame, text="Calculer distance", command=lambda: calculate_distance(self.ville_var.get())).grid(row=2, column=2, padx=5, pady=5)

        
        #Section Produits et fournisseurs
        # Frame pour disposer les champs sur 2 lignes et 2 colonnes
        surface_frame = tk.Frame(proj_frame)
        surface_frame.grid(row=3, column=0, columnspan=6, padx=5, pady=5)

        # Ligne 1 : Surface détaillée à gauche, Surface totale à droite
        tk.Button(surface_frame, text="Surface détaillée par étage", command=self.open_surface_details).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tk.Label(surface_frame, text="Surface totale (pi²) :").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        tk.Label(surface_frame, textvariable=self.total_surface_var, width=12, relief="solid", borderwidth=1).grid(row=0, column=3, sticky="w", padx=5, pady=5)

        # Ligne 2 : Nombre de mobilisations à gauche, Surface par mob. prévue à droite
        tk.Label(surface_frame, text="Nombre de mobilisations :").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(surface_frame, textvariable=self.mobilizations_var, width=10, justify="center").grid(row=1, column=1, sticky="w", padx=5, pady=5)

        tk.Label(surface_frame, text="Surface par mob. prévue :").grid(row=1, column=2, sticky="e", padx=5, pady=5)
        tk.Label(surface_frame, textvariable=self.surface_per_mob_var, width=12, relief="solid", borderwidth=1).grid(row=1, column=3, sticky="w", padx=5, pady=5)





        # Ajouter le trace pour mobilizations_var
        self.mobilizations_var.trace("w", self.update_surface_per_mob)

        # Frame Paramètres de calcul
        calc_frame = ttk.LabelFrame(self.main_frame, text="PARAMETRES DE CALCUL", padding=10)
        calc_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Champ Superficie (pi²)
        tk.Label(calc_frame, text="Superficie (pi²) :").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        entry_superficie = tk.Entry(calc_frame, textvariable=self.area_var, width=standard_width, justify="center")
        entry_superficie.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.area_var.trace("w", lambda *args: valider_entree_numerique(entry_superficie, self.area_var.get(), "Superficie (pi²)"))



        # Champ Produit
        tk.Label(calc_frame, text="Produit :").grid(row=0, column=2, padx=5, pady=5, sticky="e")

        # Récupération des produits
        details = self.db_manager.get_produit_details()
        self.products = [(d[0], d) for d in details]  # d[0] = nom du produit



        # ✅ Sélection du premier produit par défaut, s’il existe
        if self.products:
            self.product_var.set(self.products[0][0])  # Définit le premier nom de produit

        # Création du menu déroulant avec texte aligné à gauche
        self.product_menu = tk.OptionMenu(calc_frame, self.product_var, *[p[0] for p in self.products])
        self.product_menu.config(width=standard_width, anchor="w")  # 👈 Texte aligné à gauche
        self.product_menu.grid(row=0, column=3, padx=5, pady=5, sticky="w")


        # Champ Ratio
        tk.Label(calc_frame, text="Ratio :").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.ratio_menu = tk.OptionMenu(calc_frame, self.ratio_var, "")
        self.ratio_menu.config(width=standard_width)
        self.ratio_menu.grid(row=0, column=5, padx=5, pady=5, sticky="w")
        self.ratio_menu.config(state="disabled")
        self.update_ratio_options()


        # Nouveau champ Type de membrane
        tk.Label(calc_frame, text="Type de membrane :").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        # Récupérer les modèles de membrane depuis la base de données
        membrane_options = ["Aucune"] + [row[1] for row in self.db_manager.get_membranes()]  # Ajoute "Aucune" comme première option
        self.membrane_menu = tk.OptionMenu(calc_frame, self.membrane_var, *membrane_options)
        self.membrane_menu.config(width=standard_width)
        self.membrane_menu.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Nouveau champ Pose membrane
        tk.Label(calc_frame, text="Pose membrane :").grid(row=2, column=2, padx=5, pady=5, sticky="e")
        self.pose_membrane_menu = tk.OptionMenu(calc_frame, self.pose_membrane_var, *POSE_MEMBRANE_OPTIONS)
        self.pose_membrane_menu.config(width=standard_width)
        self.pose_membrane_menu.grid(row=2, column=3, padx=5, pady=5, sticky="w")

        
        # Champ Taux de change USD/CAD
        tk.Label(calc_frame, text="Taux de change USD/CAD :").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.usd_cad_rate_var = tk.StringVar(value=str(DEFAULT_USD_CAD_RATE))
        tk.Entry(calc_frame, textvariable=self.usd_cad_rate_var, width=standard_width, justify="center").grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.usd_cad_rate_var.trace("w", self.update_prix_par_sac)  # 🔁 observe changement taux de change

        # Champ Épaisseur
        tk.Label(calc_frame, text="Épaisseur :").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.thickness_menu = tk.OptionMenu(calc_frame, self.thickness_var, *THICKNESS_OPTIONS)
        self.thickness_menu.config(width=standard_width)
        self.thickness_menu.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # Champ Type de sous-plancher
        tk.Label(calc_frame, text="Type de sous-plancher :").grid(row=1, column=4, padx=5, pady=5, sticky="e")
        self.subfloor_menu = tk.OptionMenu(calc_frame, self.subfloor_var, *SUBFLOOR_OPTIONS)
        self.subfloor_menu.config(width=standard_width)
        self.subfloor_menu.grid(row=1, column=5, padx=5, pady=5, sticky="w")
        self.subfloor_var.set(DEFAULT_SUBFLOOR)  # Définir la valeur par défaut

        # Nouveaux champs dans Paramètres de calcul
        # Champ Transporteur de sable
        tk.Label(calc_frame, text="Transporteur de sable :").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        sable_data = self.db_manager.get_sable()
        transporters = sorted(set(row[1] for row in sable_data))  # Colonne 1 est transporteur
        self.sable_transporter_menu = tk.OptionMenu(calc_frame, self.sable_transporter_var, *transporters)
        self.sable_transporter_menu.config(width=standard_width)
        self.sable_transporter_menu.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.sable_transporter_var.trace("w", self.update_truck_tonnage_options)  # Mettre à jour le tonnage dynamiquement

        # Champ Tonnage camion (tm)
        tk.Label(calc_frame, text="Tonnage camion (tm) :").grid(row=3, column=2, padx=5, pady=5, sticky="e")
        self.truck_tonnage_menu = tk.OptionMenu(calc_frame, self.truck_tonnage_var, "")
        self.truck_tonnage_menu.config(width=standard_width)
        self.truck_tonnage_menu.grid(row=3, column=3, padx=5, pady=5, sticky="w")

        # Champ Secteur de transport
        tk.Label(calc_frame, text="Secteur de transport :").grid(row=3, column=4, padx=5, pady=5, sticky="e")
        self.transport_sector_menu = tk.OptionMenu(calc_frame, self.transport_sector_var, "")
        self.transport_sector_menu.config(width=standard_width)
        self.transport_sector_menu.grid(row=3, column=5, padx=5, pady=5, sticky="w")

        # Nouveau champ Travaux en dégel
        tk.Label(calc_frame, text="Travaux en dégel :").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.thaw_work_check = tk.Checkbutton(calc_frame, variable=self.thaw_work_var)
        self.thaw_work_check.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Enveloppe pour la section Produits et Fournisseurs
        prod_frame_wrapper = tk.Frame(self.main_frame)
        prod_frame_wrapper.pack(fill="x", padx=10, pady=10)

        # Frame de contenu avec bordure
        prod_frame = ttk.LabelFrame(prod_frame_wrapper, text="PRODUITS ET FOURNISSEURS", padding=10)
        prod_frame.pack(fill="x", expand=True)

        # Configurer les colonnes
        for i in range(6):
            prod_frame.grid_columnconfigure(i, weight=1)


        # Champ Apprets et scellants
        tk.Label(prod_frame, text="Apprets et scellants :").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        sealant_data = self.db_manager.get_apprets_scellants()
        sealant_options = ["Aucun"] + sorted(set(row[1] for row in sealant_data))  # Colonne 1 est nom_produit
        self.sealant_menu = tk.OptionMenu(prod_frame, self.sealant_var, *sealant_options)
        self.sealant_menu.config(width=standard_width)
        self.sealant_menu.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(prod_frame, text="Total scellants et apprêts ($) :").grid(row=0, column=3, padx=5, pady=5, sticky="e")
        tk.Label(prod_frame, textvariable=self.sealant_total_var, width=standard_width, relief="solid", borderwidth=1, anchor="center").grid(row=0, column=4, padx=5, pady=5, sticky="w")

        tk.Label(prod_frame, text="Prix par sac ($) :").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        tk.Label(prod_frame, textvariable=self.prix_par_sac_var, width=standard_width, relief="solid", borderwidth=1, anchor="center").grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Label(prod_frame, text="Quantité totale de sacs :").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        tk.Label(prod_frame, textvariable=self.total_sacs_var, width=standard_width, relief="solid", borderwidth=1, anchor="center").grid(row=2, column=1, padx=5, pady=5, sticky="w")

        tk.Label(prod_frame, text="Quantité totale de sable (tm) :").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        tk.Label(prod_frame, textvariable=self.sable_total_var, width=standard_width, relief="solid", borderwidth=1, anchor="center").grid(row=3, column=1, padx=5, pady=5, sticky="w")

        tk.Label(prod_frame, text="Nombre voyage de sable :").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        tk.Label(prod_frame, textvariable=self.nombre_voyages_var, width=standard_width, relief="solid", borderwidth=1, anchor="center").grid(row=4, column=1, padx=5, pady=5, sticky="w")

        tk.Label(prod_frame, text="Prix total sable ($) :").grid(row=4, column=3, padx=5, pady=5, sticky="e")
        tk.Label(prod_frame, textvariable=self.prix_total_sable_var, width=standard_width, relief="solid", borderwidth=1, anchor="center").grid(row=4, column=4, padx=5, pady=5, sticky="w")

        tk.Label(prod_frame, text="Prix total sacs ($) :").grid(row=2, column=3, padx=5, pady=5, sticky="e")
        tk.Label(prod_frame, textvariable=self.prix_total_sacs_var, width=standard_width, relief="solid", borderwidth=1, anchor="center").grid(row=2, column=4, padx=5, pady=5, sticky="w")

    
    
    
    
        # Nouvelle section Main d’œuvre et machinerie
        main_frame_wrapper = tk.Frame(self.main_frame)
        main_frame_wrapper.pack(fill="x", padx=10, pady=10)

        main_frame = ttk.LabelFrame(main_frame_wrapper, text="MAIN D'OEUVRE ET MACHINERIE", padding=10)
        main_frame.pack(fill="x", expand=True)

        # Définir les colonnes pour permettre un bon alignement
        for i in range(6):  # Ajuste à ton besoin
            main_frame.grid_columnconfigure(i, weight=1)


        # Champ Type de main d’œuvre
        tk.Label(main_frame, text="Type de main d’œuvre :", width=20).grid(row=0, column=0, padx=5, pady=5, sticky="e")

        main_doeuvre_data = self.db_manager.get_main_doeuvre()
        metiers = [row[1] for row in main_doeuvre_data]  # Colonne 1 = metier
        self.type_main_var = tk.StringVar()
        if metiers:
            self.type_main_var.set(metiers[0])
        else:
            self.type_main_var.set("")

        

        self.main_doeuvre_menu = tk.OptionMenu(main_frame, self.type_main_var, *metiers)
        self.main_doeuvre_menu.config(width=standard_width, anchor="w")
        self.main_doeuvre_menu.grid(row=0, column=1, padx=5, pady=5, sticky="w")


        # Déclenche le calcul du prix total heures chantier si le métier change
        self.type_main_var.trace("w", self.update_prix_total_heures_chantier)
        self.type_main_var.trace("w", self.update_prix_total_heures_transport)
        # Ajouter au dictionnaire des champs avec la bonne orthographe
        self.champs["Type de main d'oeuvre"] = self.type_main_var



        # Champ Type de pension
        tk.Label(main_frame, text="Type de pension :", width=standard_width).grid(row=0, column=3, padx=5, pady=5, sticky="e")

        pension_data = self.db_manager.get_pensions()
        types_pension = [row[1] for row in pension_data]

        self.type_pension_var = tk.StringVar(value=types_pension[0] if types_pension else "")
        self.type_pension_var.trace("w", self.update_prix_total_pension)
        self.update_prix_total_pension()
       
        self.pension_menu = tk.OptionMenu(main_frame, self.type_pension_var, *types_pension)
        self.pension_menu.config(width=standard_width)
        self.pension_menu.grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.champs["Type de pension"] = self.type_pension_var




        # Champ Type de machinerie
        tk.Label(main_frame, text="Type de machinerie :", width=standard_width).grid(row=1, column=0, padx=5, pady=5, sticky="e")

        machinerie_data = self.db_manager.get_machinerie()
        types_machinerie = [row[1] for row in machinerie_data]  # Colonne 1 = type_machinerie
        self.type_machinerie_var = tk.StringVar()
        if types_machinerie:
            self.type_machinerie_var.set(types_machinerie[0])
        else:
            self.type_machinerie_var.set("")

        self.prix_total_machinerie_var = tk.StringVar(value="0.00")

        self.type_machinerie_var.trace("w", self.update_prix_total_machinerie)
        self.heures_transport_var.trace("w", self.update_prix_total_machinerie)


        self.type_machinerie_menu = tk.OptionMenu(main_frame, self.type_machinerie_var, *types_machinerie)
        self.type_machinerie_menu.config(width=standard_width, anchor="w")  # 👈 Texte aligné à gauche
        self.type_machinerie_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")


        # Ajouter au dictionnaire des champs
        self.champs["Type machinerie"] = self.type_machinerie_var

        # Champ Prix total machinerie
        tk.Label(main_frame, text="Prix total machinerie ($) :", width=20).grid(row=1, column=3, padx=5, pady=5, sticky="e")
        self.prix_total_machinerie_var = tk.StringVar(value="0.00")
        tk.Label(main_frame, textvariable=self.prix_total_machinerie_var, width=standard_width, relief="solid", borderwidth=1, anchor="center").grid(row=1, column=4, padx=5, pady=5, sticky="w")




        # Champ Nombre d'hommes
        tk.Label(main_frame, text="Nombre d'hommes :", width=standard_width).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        entry_nombre_hommes = tk.Entry(main_frame, textvariable=self.nombre_hommes_var, justify='center', width=standard_width)
        entry_nombre_hommes.grid(row=2, column=1, padx=5, pady=5, sticky="w")


        # Champ Prix total pension


        tk.Label(main_frame, text="Prix total pension ($) :", width=standard_width).grid(row=2, column=3, padx=5, pady=5, sticky="e")
        tk.Label(main_frame, textvariable=self.prix_total_pension_var, width=standard_width, relief="solid", borderwidth=1, anchor="center").grid(row=2, column=4, padx=5, pady=5, sticky="w")



        # Ajouter au dictionnaire des champs
        self.champs["Nombre d'hommes"] = self.nombre_hommes_var

        # Champ Heures chantier calculées
        tk.Label(main_frame, text="Heures chantier calculées :", width=20).grid(row=3, column=0, padx=5, pady=5, sticky="e")
        entry_heures_chantier = tk.Entry(main_frame, textvariable=self.heures_chantier_var, justify='center', width=standard_width)
        entry_heures_chantier.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Ajouter au dictionnaire des champs si besoin
        self.champs["Heures chantier calculées"] = self.heures_chantier_var


        #Champ Prix total heures chantier
        tk.Label(main_frame, text="Prix total heures chantier ($) :", width=22).grid(row=3, column=3, padx=5, pady=5, sticky="e")
        tk.Label(main_frame, textvariable=self.prix_total_heures_chantier_var, width=standard_width, relief="solid", borderwidth=1, anchor="center").grid(row=3, column=4, padx=5, pady=5, sticky="w")



        # Champ Heures transport calculées
        tk.Label(main_frame, text="Heures transport calculées :", width=20).grid(row=4, column=0, padx=5, pady=5, sticky="e")
        entry_heures_transport = tk.Entry(main_frame, textvariable=self.heures_transport_var, justify='center', width=standard_width)
        entry_heures_transport.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        self.champs["Heures transport calculées"] = self.heures_transport_var

        # Champ Prix total heures transport
        tk.Label(main_frame, text="Prix total heures transport ($) :", width=22).grid(row=4, column=3, padx=5, pady=5, sticky="e")
        tk.Label(main_frame, textvariable=self.prix_total_heures_transport_var, width=standard_width, relief="solid", borderwidth=1, anchor="center").grid(row=4, column=4, padx=5, pady=5, sticky="w")



        # Nouvelle section AJUSTEMENTS ET TOTAUX
        ajustements_frame = ttk.LabelFrame(self.main_frame, text="AJUSTEMENTS ET TOTAUX", padding=10)
        ajustements_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Champs Ajustement 1
        ajust_label1 = tk.Entry(ajustements_frame, width=20)
        ajust_label1.insert(0, "Ajustement 1")
        ajust_label1.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ajust_value1 = tk.Entry(ajustements_frame, textvariable=self.ajustement1_var, width=16, justify='center')
        ajust_value1.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Champs Ajustement 2
        ajust_label2 = tk.Entry(ajustements_frame, width=20)
        ajust_label2.insert(0, "Ajustement 2")
        ajust_label2.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ajust_value2 = tk.Entry(ajustements_frame, textvariable=self.ajustement2_var, width=16, justify='center')
        ajust_value2.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Champs Ajustement 3
        ajust_label3 = tk.Entry(ajustements_frame, width=20)
        ajust_label3.insert(0, "Ajustement 3")
        ajust_label3.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        ajust_value3 = tk.Entry(ajustements_frame, textvariable=self.ajustement3_var, width=16, justify='center')
        ajust_value3.grid(row=2, column=1, padx=5, pady=5, sticky="w")



        # Repères de nivellement
        tk.Label(ajustements_frame, text="Repères de nivellement :").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        entry_reperes = tk.Entry(ajustements_frame, textvariable=self.reperes_var, width=16, justify='center')
        entry_reperes.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Sous-total ajustements (non modifiable)
        tk.Label(ajustements_frame, text="Sous-total Ajustements ($) :").grid(row=5, column=0, padx=5, pady=10, sticky="e")
        tk.Label(
            ajustements_frame,
            textvariable=self.sous_total_ajustements_var,
            width=12,
            relief="solid",
            borderwidth=1,
            anchor="center",
            font=("Helvetica", 10, "bold")
        ).grid(row=5, column=1, padx=5, pady=10, sticky="w")



        # SOUS-TOTAL PRODUITS ET FOURNISSEURS
        tk.Label(ajustements_frame, text="Sous-total Produits et Fournisseurs ($) :").grid(row=6, column=0, padx=5, pady=5, sticky="e")
        tk.Label(ajustements_frame, textvariable=self.sous_total_fournisseurs_var, width=12, relief="solid", borderwidth=1, anchor="center", font=("Helvetica", 10, "bold")).grid(row=6, column=1, padx=5, pady=5, sticky="w")


        # SOUS-TOTAL MAIN D’OEUVRE ET MACHINERIE
        tk.Label(ajustements_frame, text="Sous-total Main d'oeuvre et Machinerie ($) :").grid(row=7, column=0, padx=5, pady=5, sticky="e")
        tk.Label(ajustements_frame, textvariable=self.sous_total_main_machinerie_var, font=("Helvetica", 10, "bold"),
                width=12, relief="solid", borderwidth=1, anchor="center").grid(row=7, column=1, padx=5, pady=5, sticky="w")


        # TOTAL DES PRIX COÛTANTS
        tk.Label(ajustements_frame, text="Total des prix coutants ($) :").grid(row=8, column=0, padx=5, pady=10, sticky="e")
        tk.Label(ajustements_frame, textvariable=self.total_prix_coutants_var, font=("Helvetica", 10, "bold"),
                width=12, relief="solid", borderwidth=1, anchor="center").grid(row=8, column=1, padx=5, pady=10, sticky="w")


        # Champ Administ./profit (%)
        tk.Label(ajustements_frame, text="Administ./profit (%) :").grid(row=9, column=0, padx=5, pady=5, sticky="e")
        entry_admin_profit = tk.Entry(ajustements_frame, textvariable=self.admin_profit_var, width=16, justify='center')
        entry_admin_profit.grid(row=9, column=1, padx=5, pady=5, sticky="w")


        # Champ Montant administ./profit ($)
        tk.Label(ajustements_frame, text="Montant administ./profit ($) :").grid(row=10, column=0, padx=5, pady=5, sticky="e")
        tk.Label(ajustements_frame, textvariable=self.admin_profit_montant_var, width=12, relief="solid", borderwidth=1, anchor="center", font=("Helvetica", 10, "bold")).grid(row=10, column=1, padx=5, pady=5, sticky="w")

        # Champ Prix de vente client ($)
        tk.Label(ajustements_frame, text="Prix de vente client ($) :").grid(row=11, column=0, padx=5, pady=5, sticky="e")
        tk.Label(ajustements_frame, textvariable=self.prix_vente_client_var, width=12, relief="solid", borderwidth=1, anchor="center", font=("Helvetica", 10, "bold")).grid(row=11, column=1, padx=5, pady=5, sticky="w")


        # Champ Prix unitaire au pi²
        # Champ Prix unitaire au pi²
        tk.Label(ajustements_frame, text="Prix unitaire au pi² ($) :", font=("Arial", 10, "bold")).grid(row=12, column=0, padx=5, pady=5, sticky="e")
        tk.Label(ajustements_frame, textvariable=self.prix_unitaire_var, width=12, relief="solid", borderwidth=1, anchor="center", font=('Helvetica', 10, 'bold')).grid(row=12, column=1, padx=5, pady=5, sticky="w")


        # Champ Prix total par immeuble
        tk.Label(ajustements_frame, text="Prix total par immeuble ($) :", font=("Arial", 10, "bold")).grid(row=13, column=0, padx=5, pady=5, sticky="e")
        tk.Label(ajustements_frame, textvariable=self.prix_total_immeuble_var, width=12, relief="solid", borderwidth=1, anchor="center", font=('Helvetica', 10, 'bold')).grid(row=13, column=1, padx=5, pady=5, sticky="w")

        # Champ Prix au pi² ajusté (modifiable)
        tk.Label(ajustements_frame, text="Prix au pi² ajusté :").grid(row=14, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(ajustements_frame, textvariable=self.prix_pi2_ajuste_var, width=16, justify='center').grid(row=14, column=1, padx=5, pady=5, sticky="w")

        # Champ Prix total ajusté (modifiable)
        tk.Label(ajustements_frame, text="Prix total ajusté :").grid(row=15, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(ajustements_frame, textvariable=self.prix_total_ajuste_var, width=16, justify='center').grid(row=15, column=1, padx=5, pady=5, sticky="w")



        # Boutons
        # ---- NOUVEAUX BOUTONS ----
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Enregistrer comme Final", command=lambda: self.save_submission(final=True)).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Enregistrer comme Brouillon", command=lambda: self.save_submission(final=False)).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Créer une Révision", command=lambda: self.save_submission(final=True, revision=True)).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Dupliquer cette Soumission", command=lambda: self.save_submission(final=True, duplication=True)).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Annuler", command=self.window.destroy).grid(row=0, column=4, padx=5)
        tk.Button(btn_frame, text="Générer le devis", command=self.generer_devis).grid(row=0, column=5, padx=5)
        tk.Button(btn_frame, text="Feuille de travail", command=lambda: ExportFeuilleTravailWindow(self.window, self.get_submission_data(), self.db_manager)).grid(row=0, column=6, padx=5)






        self.existing_submission = existing_submission
        self.init_chargement()


    def get_submission_data(self):
        try:
            data = {
                "submission_number": self.submission_number_var.get(),
                "client_name": self.client_var.get(),
                "contact": self.contact_var.get(),
                # "telephone": self.telephone_contact_var.get(),  # ❌ À retirer
                "ville": self.ville_var.get(),
                "product": self.product_var.get(),
                "area": self.area_var.get(),
                "thickness": self.thickness_var.get(),
                "subfloor": self.subfloor_var.get(),
                "distance": self.distance_var.get(),
                "total_sacs": self.total_sacs_var.get(),
                "sable_total": self.sable_total_var.get(),          
                "sable_transporter": self.sable_transporter_var.get(),
                "membrane": self.membrane_var.get(),
                "pose_membrane": self.pose_membrane_var.get(),


            }

            # Recherche le téléphone du contact
            contact_name = data["contact"]
            client_name = data["client_name"]
            all_contacts = self.db_manager.get_all_contacts_with_clients()

            data["telephone"] = ""  # Valeur par défaut
            for c in all_contacts:
                if c["nom"] == contact_name and c["client_name"] == client_name:
                    data["telephone"] = c["telephone"]
                    break

            return data


        except Exception as e:
           
            return {}




    def init_chargement(self):
        if self.existing_submission:
            self.charger_donnees_submission(self.existing_submission)
        else:
            self.generate_submission_number()



    def charger_donnees_submission(self, data):
        self.submission_number_var.set(data.get("submission_number", ""))
        self.date_var.set(data.get("date_submission", ""))
        self.client_var.set(data.get("client_name", ""))
        self.contact_var.set(data.get("contact", ""))
        self.projet_var.delete("1.0", tk.END)
        self.projet_var.insert("1.0", data.get("projet", ""))
        self.ville_var.set(data.get("ville", ""))
        self.distance_var.set(data.get("distance", ""))

        self.area_var.set(data.get("area", ""))
        self.product_var.set(data.get("product", ""))
        self.ratio_var.set(data.get("ratio", ""))
        self.usd_cad_rate_var.set(data.get("usd_cad_rate", ""))
        self.thickness_var.set(data.get("thickness", ""))
        self.subfloor_var.set(data.get("subfloor", ""))
        self.membrane_var.set(data.get("membrane", ""))
        self.pose_membrane_var.set(data.get("pose_membrane", ""))
        self.sealant_var.set(data.get("sealant", ""))

        self.prix_par_sac_var.set(data.get("prix_par_sac", ""))
        self.total_sacs_var.set(data.get("total_sacs", ""))
        self.prix_total_sacs_var.set(data.get("prix_total_sacs", ""))
        self.sable_total_var.set(data.get("sable_total", ""))
        self.nombre_voyages_var.set(data.get("voyages_sable", ""))
        self.prix_total_sable_var.set(data.get("prix_total_sable", ""))
        self.mobilizations_var.set(data.get("mobilisations", ""))
        self.surface_per_mob_var.set(data.get("surface_per_mob", ""))

        self.type_main_var.set(data.get("type_main", ""))
        self.type_pension_var.set(data.get("type_pension", ""))
        self.type_machinerie_var.set(data.get("type_machinerie", ""))
        self.nombre_hommes_var.set(data.get("nb_hommes", ""))
        self.heures_chantier_var.set(data.get("heures_chantier", ""))
        self.heures_transport_var.set(data.get("heures_transport", ""))
        self.prix_total_pension_var.set(data.get("prix_total_pension", ""))
        self.prix_total_machinerie_var.set(data.get("prix_total_machinerie", ""))
        self.prix_total_heures_chantier_var.set(data.get("prix_total_heures_chantier", ""))
        self.prix_total_heures_transport_var.set(data.get("prix_total_heures_transport", ""))

        self.ajustement1_var.set(data.get("ajustement1_valeur", ""))
        self.ajustement2_var.set(data.get("ajustement2_valeur", ""))
        self.ajustement3_var.set(data.get("ajustement3_valeur", ""))
        self.reperes_var.set(data.get("reperes_nivellement", ""))

        self.sous_total_ajustements_var.set(data.get("sous_total_ajustements", ""))
        self.sous_total_fournisseurs_var.set(data.get("sous_total_fournisseurs", ""))
        self.sous_total_main_machinerie_var.set(data.get("sous_total_main_machinerie", ""))
        self.total_prix_coutants_var.set(data.get("total_prix_coutants", ""))

        self.admin_profit_var.set(data.get("admin_profit_pct", ""))
        self.admin_profit_montant_var.set(data.get("admin_profit_montant", ""))
        self.prix_vente_client_var.set(data.get("prix_vente_client", ""))
        self.prix_unitaire_var.set(data.get("prix_unitaire", ""))
        self.prix_total_immeuble_var.set(data.get("prix_total_immeuble", ""))
        self.prix_pi2_ajuste_var.set(data.get("prix_pi2_ajuste", ""))
        self.prix_total_ajuste_var.set(data.get("prix_total_ajuste", ""))

        import json
        self.notes_data = json.loads(data.get("notes_json", "{}"))
        self.surface_data = json.loads(data.get("surfaces_json", "{}"))

        self.sable_transporter_var.set(data.get("sable_transporter", ""))
        self.truck_tonnage_var.set(data.get("truck_tonnage", ""))
        
        self.transport_sector_var.set(data.get("transport_sector", ""))






    def update_dependants_apres_vente(self, *args):
        self.update_prix_unitaire()
        self.update_prix_total_immeuble()
    


    def update_prix_total_immeuble(self, *args):
        try:
            prix_unitaire = safe_float(self.prix_unitaire_var.get())
            surface_totale = safe_float(self.total_surface_var.get())

            total = prix_unitaire * surface_totale
            self.prix_total_immeuble_var.set(f"{total:.2f} $")
        except Exception as e:
            
            self.prix_total_immeuble_var.set("0.00")


        

    def update_prix_unitaire(self, *args):
        try:
            prix_vente_str = self.prix_vente_client_var.get().replace(",", "").replace("$", "").strip()
            superficie_str = self.area_var.get().replace(",", "").strip()

            # Vérification de la validité numérique
            if not prix_vente_str.replace('.', '', 1).isdigit() or not superficie_str.replace('.', '', 1).isdigit():
                self.prix_unitaire_var.set("0.00")
                return

            prix_vente = safe_float(prix_vente_str)
            superficie = safe_float(superficie_str)

            if superficie == 0:
                self.prix_unitaire_var.set("0.00")
                return

            unitaire = prix_vente / superficie
            self.prix_unitaire_var.set(f"{unitaire:.2f}")
        except Exception as e:
            
            self.prix_unitaire_var.set("0.00")



    def update_admin_profit_et_dependants(self, *args):
        self.update_admin_profit_montant()
        self.update_prix_unitaire()
        self.update_prix_total_immeuble()



    def update_prix_vente_client(self, *args):
        try:
            total_str = self.total_prix_coutants_var.get().replace(" $", "").strip()
            admin_str = self.admin_profit_montant_var.get().replace(" $", "").strip()

            

            if not total_str.replace('.', '', 1).isdigit() or not admin_str.replace('.', '', 1).isdigit():
                raise ValueError("Valeur non numérique")

            total = safe_float(total_str)
            admin = safe_float(admin_str)

            prix_vente = total + admin
            self.prix_vente_client_var.set(f"{prix_vente:.2f} $")

        except Exception as e:
            
            self.prix_vente_client_var.set("Erreur")





    def format_admin_profit_percent(self, *args):
        value = self.admin_profit_var.get().replace('%', '').strip()
        if value:
            try:
                float(value)  # validation numérique
                self.admin_profit_var.set(f"{value} %")
            except ValueError:
                self.admin_profit_var.set("0 %")



    def update_admin_profit_montant(self, *args):
        try:
            # Extraire le pourcentage (en retirant le symbole %)
            pourcentage_str = self.admin_profit_var.get().replace('%', '').strip()
            pourcentage = float(pourcentage_str) / 100

            # Lire le total des prix coûtants
            total_str = self.total_prix_coutants_var.get().replace('$', '').replace(',', '').strip()
            total = float(total_str)

            # Calcul du montant de profit
            montant = total * pourcentage
            self.admin_profit_montant_var.set(f"{montant:.2f} $")

            # Calcul du prix de vente
            prix_vente = total + montant
            self.prix_vente_client_var.set(f"{prix_vente:.2f} $")

        except Exception as e:
            self.admin_profit_montant_var.set("Erreur")
            self.prix_vente_client_var.set("Erreur")


    def update_total_prix_coutants(self, *args):
        try:
            def get_float(var):
                val = var.get().replace(" $", "").replace(",", ".")
                return float(val) if val.strip() else 0.0

            total_ajustements = get_float(self.sous_total_ajustements_var)
            total_fournisseurs = get_float(self.sous_total_fournisseurs_var)
            total_main_machinerie = get_float(self.sous_total_main_machinerie_var)

            total = total_ajustements + total_fournisseurs + total_main_machinerie
            self.total_prix_coutants_var.set(f"{total:.2f} $")

        except Exception as e:
            
            self.total_prix_coutants_var.set("Erreur")


    def update_sous_total_main_machinerie(self, *args):
        try:
            def get_float(var):
                val = var.get().replace(" $", "").replace(",", ".")
                return float(val) if val.strip() else 0.0

            total_machinerie = get_float(self.prix_total_machinerie_var)
            total_pension = get_float(self.prix_total_pension_var)
            total_chantier = get_float(self.prix_total_heures_chantier_var)
            total_transport = get_float(self.prix_total_heures_transport_var)

            total = total_machinerie + total_pension + total_chantier + total_transport
            self.sous_total_main_machinerie_var.set(f"{total:.2f} $")

        except Exception as e:
            
            self.sous_total_main_machinerie_var.set("Erreur")

        self.update_total_prix_coutants()


    def update_sous_total_fournisseurs(self, *args):
        try:
            sealant_total = safe_float(self.sealant_total_var.get())
            total_sacs = safe_float(self.prix_total_sacs_var.get())
            total_sable = safe_float(self.prix_total_sable_var.get())

            total = sealant_total + total_sacs + total_sable
            self.sous_total_fournisseurs_var.set(f"{total:.2f} $")
        except Exception as e:
            
            self.sous_total_fournisseurs_var.set("Erreur")

        self.update_total_prix_coutants()





    def update_sous_total_ajustements(self, *args):
        try:
            montants = [
                float(self.ajustement1_var.get() or 0),
                float(self.ajustement2_var.get() or 0),
                float(self.ajustement3_var.get() or 0),
                float(self.reperes_var.get() or 0)
            ]
            total = sum(montants)
            self.sous_total_ajustements_var.set(f"{total:.2f} $")
        except Exception as e:
            
            self.sous_total_ajustements_var.set("Erreur")

        self.update_total_prix_coutants()



    def update_prix_total_heures_transport(self, *args):
        try:
            nb_hommes = int(self.nombre_hommes_var.get())
            heures_transport = float(self.heures_transport_var.get())
            type_main = self.type_main_var.get()

            main_data = self.db_manager.get_main_doeuvre()
            taux = next((row[3] for row in main_data if row[1] == type_main), None)

            if taux is not None:
                total = nb_hommes * heures_transport * taux
                self.prix_total_heures_transport_var.set(f"{total:.2f} $")
            else:
                self.prix_total_heures_transport_var.set("0.00")
        except Exception as e:
            self.prix_total_heures_transport_var.set("0.00")
        
        self.update_sous_total_main_machinerie()





    def update_prix_total_heures_chantier(self, *args):
        
        try:
            type_main = self.champs.get("Type de main d'oeuvre", tk.StringVar()).get()
            heures_chantier_str = self.heures_chantier_var.get()
            nb_hommes_str = self.nombre_hommes_var.get()

            if not type_main or not heures_chantier_str or not nb_hommes_str:
                self.prix_total_heures_chantier_var.set("0.00")
                return

            heures_chantier = float(heures_chantier_str)
            nb_hommes = int(nb_hommes_str)

            for mo in self.db_manager.get_main_doeuvre():
                if mo[1] == type_main:
                    taux_horaire = mo[2]
                    total = nb_hommes * heures_chantier * taux_horaire
                    self.prix_total_heures_chantier_var.set(f"{total:.2f} $")
                    return

            

        except Exception as e:
            self.prix_total_heures_chantier_var.set("0.00")

        self.update_sous_total_main_machinerie()





    def update_prix_total_pension(self, *args):
        try:
            type_pension = self.type_pension_var.get()
            nombre_hommes = self.nombre_hommes_var.get()
            

            total = calculer_prix_total_pension(self.db_manager, type_pension, nombre_hommes)

            if total is None:
                raise ValueError("Résultat du calcul est None")

            total_float = float(total)
            self.prix_total_pension_var.set(f"{total_float:.2f} $")
            

        except Exception as e:
            self.prix_total_pension_var.set("Erreur")

        self.update_sous_total_main_machinerie()





    def update_prix_total_machinerie(self, *args):
        try:
            type_machinerie = self.type_machinerie_var.get()
            heures_chantier = self.heures_chantier_var.get()
            heures_transport = self.heures_transport_var.get()

            total = calculer_prix_total_machinerie(self.db_manager, type_machinerie, heures_chantier, heures_transport)

            if total is None:
                raise ValueError("Résultat du calcul est None")

            total_float = float(total)
            self.prix_total_machinerie_var.set(f"{total_float:.2f} $")
            

        except Exception as e:
            self.prix_total_machinerie_var.set("Erreur")

        self.update_sous_total_main_machinerie()





    def update_heures_transport(self, *args):
        
        self.heures_transport_var.set(
            calculer_heures_transport(self.distance_var.get())
        )




    def update_heures_chantier(self, *args):
        superficie = self.area_var.get()
        heures = calculer_heures_chantier(superficie)
        self.heures_chantier_var.set(heures)
        self.update_prix_total_machinerie()
        self.update_prix_total_heures_chantier()


    def update_nombre_voyages(self, *args): 
        try:
            sable_str = self.sable_total_var.get()
            tonnage_str = self.truck_tonnage_var.get()

            # Vérifier si les champs sont vides
            if not sable_str or not tonnage_str:
                self.nombre_voyages_var.set("0")
                return

            voyages = calculer_nombre_voyages_sable(sable_str, tonnage_str)            
            self.nombre_voyages_var.set(voyages)
        except Exception as e:
            self.nombre_voyages_var.set("Erreur")
        
        self.update_prix_total_sable()



    def update_prix_total_sable(self, *args):
        try:
            sable_str = self.sable_total_var.get()
            voyages_str = self.nombre_voyages_var.get()
            transporteur = self.sable_transporter_var.get()
            type_camion = self.truck_tonnage_var.get()


            total = calculer_prix_total_sable(self.db_manager, sable_str, voyages_str, transporteur, type_camion)
            self.prix_total_sable_var.set(total)
            
        except Exception as e:
            
            self.prix_total_sable_var.set("Erreur")

        self.update_sous_total_fournisseurs()




    def update_sable_total(self, *args):
        nb_sacs = self.total_sacs_var.get()
        ratio = self.ratio_var.get()
        sable_total = calculer_quantite_sable(nb_sacs, ratio)
        self.sable_total_var.set(sable_total)

        if sable_total.isdigit():
            self.update_nombre_voyages()

        # ➕ Met à jour le prix du sable
        self.update_prix_total_sable()


    def update_prix_total_sable(self, *args):
        try:
            transporteur = self.sable_transporter_var.get()
            tonnage_str = self.truck_tonnage_var.get()
            secteur = self.transport_sector_var.get()


            if not (transporteur and tonnage_str and secteur):
                self.prix_total_sable_var.set("0.00")
                return

            tonnage = int(tonnage_str)
            sable_data = self.db_manager.get_sable()
            

            entry = next(
                (row for row in sable_data if row[1] == transporteur and row[2] == tonnage and row[3] == secteur),
                None
            )

            if not entry:
                
                self.prix_total_sable_var.set("Erreur")
                return

            prix_voyage = float(entry[4])
            prix_sable_tm = float(entry[5])
            

            sable_total_str = self.sable_total_var.get().replace(",", "")
            sable_total = float(sable_total_str) if sable_total_str else 0.0
           

            # Calcul du nombre de voyages requis
            voyages = max(1, int((sable_total + tonnage - 1) // tonnage))  # arrondi supérieur
            

            total_sable = sable_total * prix_sable_tm
            total_transport = voyages * prix_voyage
            total = round(total_sable + total_transport, 2)



            self.prix_total_sable_var.set(f"{total:,.2f}")

        except Exception as e:

            self.prix_total_sable_var.set("Erreur")




    def update_prix_total_sacs(self, *args):
        try:
            nb_sacs_str = self.total_sacs_var.get()
            prix_unitaire_str = self.prix_par_sac_var.get()

            

            nb_sacs = int(nb_sacs_str)
            prix_unitaire = float(prix_unitaire_str.replace(",", "."))

            total = nb_sacs * prix_unitaire
            
            self.prix_total_sacs_var.set(f"{total:.2f}")
        except Exception as e:
            
            self.prix_total_sacs_var.set("0.00")

        self.update_sous_total_fournisseurs()

    





    def update_total_sacs(self, *args):
        superficie = self.area_var.get()
        epaisseur = self.thickness_var.get()
        produit = self.product_var.get()
        ratio = self.ratio_var.get()

        result = calculate_total_sacs(superficie, epaisseur, produit, ratio, self.db_manager)
        
        self.total_sacs_var.set(result)

        # ✅ Forcer le recalcul du prix total
        self.update_prix_total_sacs()




    def update_prix_par_sac(self, *args):
        produit = self.product_var.get()
        taux_change = self.usd_cad_rate_var.get()
        if produit and taux_change:
            result = calculate_prix_par_sac(produit, taux_change, self.db_manager)
            self.prix_par_sac_var.set(result)
        else:
            self.prix_par_sac_var.set("0.00")



    def update_sealant_total(self, *args):
        try:
            area = float(self.area_var.get().replace(",", "") or 0)
            selected_sealant = self.sealant_var.get()

            if selected_sealant == "Aucun" or not selected_sealant:
                self.sealant_total_var.set("0.00")
                return

            for row in self.db_manager.get_apprets_scellants():
                nom, prix, _, couverture = row[1], row[2], row[3], row[4]
                if nom == selected_sealant:
                    if couverture <= 0:
                        self.sealant_total_var.set("Erreur")
                        return
                    total = (area / couverture) * prix
                    self.sealant_total_var.set(f"{total:.2f}")
                    return

            self.sealant_total_var.set("0.00")  # si non trouvé
        except Exception as e:
            self.sealant_total_var.set("Erreur")

        self.update_sous_total_fournisseurs()



    def update_sealant_default(self, *args):
        """Mettre à jour la sélection d'apprêt en fonction du type de sous-plancher."""
        subfloor = self.subfloor_var.get()
        sealant_data = self.db_manager.get_apprets_scellants()
        sealant_options = [row[1] for row in sealant_data]  # Liste des nom_produit
        if subfloor == "Béton" and sealant_options:
            self.sealant_var.set(sealant_options[0])  # Sélectionne le premier apprêt
        else:
            self.sealant_var.set("Aucun")  # Réinitialise à "Aucun" pour Bois ou Acier


    def update_truck_tonnage_options(self, *args):
        selected_transporter = self.sable_transporter_var.get()
        truck_tonnages = get_truck_tonnages(self.db_manager, selected_transporter) if selected_transporter else []

        # Met à jour le menu de tonnage
        menu_tonnage = self.truck_tonnage_menu["menu"]
        menu_tonnage.delete(0, "end")
        for tonnage in truck_tonnages:
            menu_tonnage.add_command(label=str(tonnage), command=lambda x=str(tonnage): self.on_truck_tonnage_change(x))
        self.truck_tonnage_menu.config(state="normal" if truck_tonnages else "disabled")
        self.truck_tonnage_var.set(str(truck_tonnages[0]) if truck_tonnages else "")

        # Rafraîchit les secteurs selon le premier tonnage (ou vide)
        self.update_transport_sector_options()

    def on_truck_tonnage_change(self, tonnage):
        self.truck_tonnage_var.set(tonnage)
        self.update_transport_sector_options()

    def update_transport_sector_options(self):
        selected_transporter = self.sable_transporter_var.get()
        selected_tonnage = self.truck_tonnage_var.get()

        sable_data = self.db_manager.get_sable()
        transport_sectors = sorted(set(
            row[3] for row in sable_data
            if row[1] == selected_transporter and str(row[2]) == selected_tonnage
        ))

        menu_sector = self.transport_sector_menu["menu"]
        menu_sector.delete(0, "end")
        for sector in transport_sectors:
            menu_sector.add_command(label=sector, command=lambda x=sector: self.transport_sector_var.set(x))
        self.transport_sector_menu.config(state="normal" if transport_sectors else "disabled")
        self.transport_sector_var.set(transport_sectors[0] if transport_sectors else "")


    def generate_submission_number(self):
        current_year = datetime.now().year
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT MAX(sequence) FROM submissions WHERE year = ?
            """, (current_year,))
            max_sequence = cursor.fetchone()[0]
            new_sequence = 200 if max_sequence is None else max_sequence + 1
            submission_number = f"S{current_year % 100:02d}-{new_sequence:03d}"
            self.submission_number_var.set(submission_number)

    def save_submission(self, final=True, revision=False, duplication=False):
        try:
            # Valider et convertir la date
            date_submission = check_date_on_save(self.date_var.get())
            if date_submission is None:
                return

            submission_number = self.submission_number_var.get()

            if duplication and not hasattr(self, "_contact_selected"):
                def on_contact_selected(contact):
                    self.client_var.set(contact["client_name"])
                    self.contact_var.set(contact["nom"])
                    self._contact_selected = True
                    self.save_submission(final=final, revision=revision, duplication=True)

                ContactSelector(self.window, self.db_manager, on_contact_selected)
                return

            if duplication:
                self.generate_submission_number()
                submission_number = self.submission_number_var.get()
                revision_number = 0
                if hasattr(self, "_contact_selected"):
                    del self._contact_selected
            elif revision:
                base_number = submission_number.split(" ")[0]
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT MAX(revision) FROM submissions WHERE submission_number LIKE ?
                    """, (f"{base_number}%",))
                    max_rev = cursor.fetchone()[0]
                    revision_number = (max_rev or 0) + 1
                    submission_number = f"{base_number} REV.{revision_number}"
            else:
                revision_number = 0

            self.submission_number_var.set(submission_number)

            etat = "finalisé" if final else "brouillon"
            current_year = datetime.now().year
            sequence = int(submission_number.split("-")[1].split()[0]) if "-" in submission_number else 0

            data = {
                "submission_number": submission_number,
                "revision": revision_number,
                "is_active": 1,
                "etat": etat,
                "year": current_year,
                "sequence": sequence,
                "date_submission": date_submission,  # Utiliser la date validée
                "client_name": self.client_var.get(),
                "contact": self.contact_var.get(),
                "projet": self.projet_var.get("1.0", tk.END).strip(),
                "ville": self.ville_var.get(),
                "distance": self.distance_var.get(),
                "area": self.area_var.get(),
                "product": self.product_var.get(),
                "ratio": self.ratio_var.get(),
                "usd_cad_rate": self.usd_cad_rate_var.get(),
                "thickness": self.thickness_var.get(),
                "subfloor": self.subfloor_var.get(),
                "membrane": self.membrane_var.get(),
                "pose_membrane": self.pose_membrane_var.get(),
                "sealant": self.sealant_var.get(),
                "prix_par_sac": self.prix_par_sac_var.get(),
                "total_sacs": self.total_sacs_var.get(),
                "prix_total_sacs": self.prix_total_sacs_var.get(),
                "sable_total": self.sable_total_var.get(),
                "voyages_sable": self.nombre_voyages_var.get(),
                "prix_total_sable": self.prix_total_sable_var.get(),
                "mobilisations": self.mobilizations_var.get(),
                "surface_per_mob": self.surface_per_mob_var.get(),
                "type_main": self.type_main_var.get(),
                "type_pension": self.type_pension_var.get(),
                "type_machinerie": self.type_machinerie_var.get(),
                "nb_hommes": self.nombre_hommes_var.get(),
                "heures_chantier": self.heures_chantier_var.get(),
                "heures_transport": self.heures_transport_var.get(),
                "prix_total_pension": self.prix_total_pension_var.get(),
                "prix_total_machinerie": self.prix_total_machinerie_var.get(),
                "prix_total_heures_chantier": self.prix_total_heures_chantier_var.get(),
                "prix_total_heures_transport": self.prix_total_heures_transport_var.get(),
                "ajustement1_nom": "Ajustement 1",
                "ajustement1_valeur": self.ajustement1_var.get(),
                "ajustement2_nom": "Ajustement 2",
                "ajustement2_valeur": self.ajustement2_var.get(),
                "ajustement3_nom": "Ajustement 3",
                "ajustement3_valeur": self.ajustement3_var.get(),
                "reperes_nivellement": self.reperes_var.get(),
                "sous_total_ajustements": self.sous_total_ajustements_var.get(),
                "sous_total_fournisseurs": self.sous_total_fournisseurs_var.get(),
                "sous_total_main_machinerie": self.sous_total_main_machinerie_var.get(),
                "total_prix_coutants": self.total_prix_coutants_var.get(),
                "admin_profit_pct": self.admin_profit_var.get(),
                "admin_profit_montant": self.admin_profit_montant_var.get(),
                "prix_vente_client": self.prix_vente_client_var.get(),
                "prix_unitaire": self.prix_unitaire_var.get(),
                "prix_total_immeuble": self.prix_total_immeuble_var.get(),
                "prix_pi2_ajuste": self.prix_pi2_ajuste_var.get(),
                "prix_total_ajuste": self.prix_total_ajuste_var.get(),
                "notes_json": json.dumps(self.notes_data),
                "surfaces_json": json.dumps(self.surface_data),
                "sable_transporter": self.sable_transporter_var.get(),
                "truck_tonnage": self.truck_tonnage_var.get(),
                "transport_sector": self.transport_sector_var.get()
            }

            existing_submission = self.db_manager.get_submission_by_number(submission_number)

            if existing_submission and final and not revision and not duplication:
                self.db_manager.update_submission(submission_number, data)
                messagebox.showinfo("Succès", f"Soumission mise à jour : {submission_number}")
            else:
                self.db_manager.insert_submission(data)
                messagebox.showinfo("Succès", f"Soumission enregistrée : {submission_number}")

            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l’enregistrement : {e}")
        

    def open_project_notes(self):
        # Ouvre la fenêtre des notes et passe les données actuelles
        notes_window = ProjectNotesWindow(self.window, self.notes_data)
        self.window.wait_window(notes_window.window)  # Attend la fermeture de la fenêtre
        if hasattr(notes_window, 'notes_data'):
            self.notes_data.update(notes_window.notes_data)

    def open_surface_details(self):
        # Ouvre la fenêtre des surfaces et passe les données actuelles
        surface_window = DetailedSurfaceWindow(self.window, self.surface_data)
        self.window.wait_window(surface_window.window)  # Attend la fermeture de la fenêtre
        if hasattr(surface_window, 'surface_data'):
            self.surface_data.update(surface_window.surface_data)
            # Mettre à jour la surface totale après sauvegarde
            total = sum(int(self.surface_data.get(f"surface_{i}", 0) or 0) for i in range(1, 16))
            self.total_surface_var.set(str(total))
            self.update_surface_per_mob()  # Recalculer la surface par mobilisation



  
    def update_surface_per_mob(self, *args):
        try:
            total = int(self.total_surface_var.get() or 0)
            mobilizations = float(self.mobilizations_var.get() or 1.0)
            self.surface_per_mob_var.set(calculate_surface_per_mob(total, mobilizations))
        except ValueError:
            self.surface_per_mob_var.set("Erreur")


    def update_ratio_options(self, *args):
        product_name = self.product_var.get()
        if product_name:
            product_details = next((d for d in self.db_manager.get_produit_details() if d[0] == product_name), None)
            if product_details and product_details[5] == "COUVERTURE":
                self.ratio_var.set("")
                self.ratio_menu.config(state="disabled")
            else:
                ratios = self.db_manager.get_produit_ratios(product_name)
                menu = self.ratio_menu["menu"]
                menu.delete(0, "end")
                default_ratio = next((r[1] for r in ratios if r[2] == 1), None)  # Trouver le ratio par défaut
                for ratio in ratios:
                    menu.add_command(label=str(ratio[1]), command=lambda x=str(ratio[1]): self.ratio_var.set(x))
                self.ratio_menu.config(state="normal")
                if default_ratio is not None:
                    self.ratio_var.set(str(default_ratio))  # Définir le ratio par défaut
        else:
            self.ratio_var.set("")
            self.ratio_menu.config(state="disabled")

    def generer_devis(self):
        try:
            from gui.export_devis import ExportDevisWindow

            data = {
                "submission_number": self.submission_number_var.get(),
                "date_submission": self.check_date_on_save(self.date_var.get()),
                "client_name": self.client_var.get(),
                "contact": self.contact_var.get(),
                "projet": self.projet_var.get("1.0", "end").strip(),
                "ville": self.ville_var.get(),
                "product": self.product_var.get(),
                "area": self.area_var.get(),
                "thickness": self.thickness_var.get(),
                "prix_unitaire": self.prix_unitaire_var.get(),
                "mobilisations": self.mobilizations_var.get(),
                "membrane": self.membrane_var.get(),

            }

            ExportDevisWindow(self.window, data, self.db_manager)

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l’ouverture de la fenêtre d’export : {e}")



