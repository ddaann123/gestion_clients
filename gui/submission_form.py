import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from .submission_calcs import (calculate_distance, calculate_surface_per_mob, get_truck_tonnages, calculate_prix_par_sac, 
                               calculate_total_sacs, calculate_prix_total_sacs, calculer_quantite_sable, calculer_nombre_voyages_sable, 
                               calculer_prix_total_sable, calculer_heures_chantier, calculer_heures_transport, calculer_prix_total_machinerie, 
                               calculer_prix_total_pension
)


from config import DEFAULT_USD_CAD_RATE, THICKNESS_OPTIONS, SUBFLOOR_OPTIONS, DEFAULT_SUBFLOOR, POSE_MEMBRANE_OPTIONS



class ProjectNotesWindow:
    def __init__(self, parent, notes_data=None):
        self.window = tk.Toplevel(parent)
        self.window.title("Notes de Projet")
        self.window.geometry("400x500")
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
        self.window.geometry("400x500")
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
     
    def __init__(self, parent, db_manager, selected_client=None, selected_contact=None):
        self.db_manager = db_manager
        self.selected_client = selected_client
        self.selected_contact = selected_contact
        self.notes_data = {}  # Stocke les notes temporairement
        self.surface_data = {}  # Stocke les surfaces temporairement
        self.total_surface_var = tk.StringVar(value="0")  # Stocke la surface totale
        self.mobilizations_var = tk.StringVar(value="1.0")  # Nombre de mobilisations
        self.surface_per_mob_var = tk.StringVar(value="0.0")  # Surface par mobilisation
        self.area_var = tk.StringVar(value="0")  # Superficie (pi²)
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

        






        print("[DEBUG] Trace sur distance_var installée")








        self.window = tk.Toplevel(parent)
        self.window.title("Nouvelle Soumission")

        self.window.geometry("950x900")  # ← tu peux ajuster ici largeur x hauteur


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
        gen_frame = ttk.LabelFrame(self.main_frame, text="Informations Générales", padding=10)
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
        self.date_var.set(datetime.now().strftime("%d-%m-%Y"))  # Date par défaut : 11-06-2025
        tk.Entry(gen_frame, textvariable=self.date_var, width=30).grid(row=2, column=1, padx=5, pady=5)

        # Champ No Soumission
        tk.Label(gen_frame, text="No Soumission :").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.submission_number_var = tk.StringVar()
        self.generate_submission_number()
        tk.Entry(gen_frame, textvariable=self.submission_number_var, state="disabled", width=30).grid(row=3, column=1, padx=5, pady=5)

        # Frame Détails du Projet
        proj_frame = ttk.LabelFrame(self.main_frame, text="Détails du Projet", padding=10)
        proj_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Champ Projet (2 lignes) et bouton Notes de projet
        tk.Label(proj_frame, text="Projet :").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.projet_var = tk.Text(proj_frame, height=2, width=30, font=("TkDefaultFont", 9))
        self.projet_var.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        tk.Button(proj_frame, text="Notes de projet", command=self.open_project_notes).grid(row=0, column=2, padx=5, pady=5)

        # Champ Ville
        tk.Label(proj_frame, text="Ville :").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.ville_var = tk.StringVar()
        tk.Entry(proj_frame, textvariable=self.ville_var, width=30).grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Champ Distance chantier aller-simple (km) et bouton Calculer
        tk.Label(proj_frame, text="Distance chantier aller-simple (km) :").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(proj_frame, textvariable=self.distance_var, width=10).grid(row=2, column=1, padx=5, pady=5, sticky="w")
        tk.Button(proj_frame, text="Calculer distance", command=lambda: calculate_distance(self.ville_var.get())).grid(row=2, column=2, padx=5, pady=5)

        # Bouton Surface détaillée
        tk.Button(proj_frame, text="Surface détaillée", command=self.open_surface_details).grid(row=3, column=1, pady=5)

        # Champs Surface totale, Nombre de mobilisations, Surface par mob. prévue
        tk.Label(proj_frame, text="Surface totale (pi²) :").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        tk.Label(proj_frame, textvariable=self.total_surface_var, width=10).grid(row=4, column=1, padx=5, pady=5, sticky="w")
        tk.Label(proj_frame, text="Nombre de mobilisations :").grid(row=4, column=2, padx=5, pady=5, sticky="e")
        tk.Entry(proj_frame, textvariable=self.mobilizations_var, width=10).grid(row=4, column=3, padx=5, pady=5, sticky="w")
        tk.Label(proj_frame, text="Surface par mob. prévue :").grid(row=4, column=4, padx=5, pady=5, sticky="e")
        tk.Label(proj_frame, textvariable=self.surface_per_mob_var, width=10).grid(row=4, column=5, padx=5, pady=5, sticky="w")

        # Ajouter le trace pour mobilizations_var
        self.mobilizations_var.trace("w", self.update_surface_per_mob)

        # Frame Paramètres de calcul
        calc_frame = ttk.LabelFrame(self.main_frame, text="Paramètres de Calcul", padding=10)
        calc_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Champ Superficie (pi²)
        tk.Label(calc_frame, text="Superficie (pi²) :").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        tk.Entry(calc_frame, textvariable=self.area_var, width=10).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Champ Produit
        tk.Label(calc_frame, text="Produit :").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        details = self.db_manager.get_produit_details()
        self.products = [(d[0], d) for d in details]  # Inclure tous les produits
        self.product_menu = tk.OptionMenu(calc_frame, self.product_var, *tuple(p[0] for p in self.products))
        self.product_menu.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Champ Ratio
        tk.Label(calc_frame, text="Ratio :").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.ratio_menu = tk.OptionMenu(calc_frame, self.ratio_var, "")
        self.ratio_menu.grid(row=0, column=5, padx=5, pady=5, sticky="w")
        self.ratio_menu.config(state="disabled")
        self.update_ratio_options()


        # Nouveau champ Type de membrane
        tk.Label(calc_frame, text="Type de membrane :").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        # Récupérer les modèles de membrane depuis la base de données
        membrane_options = ["Aucune"] + [row[1] for row in self.db_manager.get_membranes()]  # Ajoute "Aucune" comme première option
        self.membrane_menu = tk.OptionMenu(calc_frame, self.membrane_var, *membrane_options)
        self.membrane_menu.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Nouveau champ Pose membrane
        tk.Label(calc_frame, text="Pose membrane :").grid(row=2, column=2, padx=5, pady=5, sticky="e")
        self.pose_membrane_menu = tk.OptionMenu(calc_frame, self.pose_membrane_var, *POSE_MEMBRANE_OPTIONS)
        self.pose_membrane_menu.grid(row=2, column=3, padx=5, pady=5, sticky="w")

        
        # Champ Taux de change USD/CAD
        tk.Label(calc_frame, text="Taux de change USD/CAD :").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.usd_cad_rate_var = tk.StringVar(value=str(DEFAULT_USD_CAD_RATE))
        tk.Entry(calc_frame, textvariable=self.usd_cad_rate_var, width=10).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.usd_cad_rate_var.trace("w", self.update_prix_par_sac)  # 🔁 observe changement taux de change

        # Champ Épaisseur
        tk.Label(calc_frame, text="Épaisseur :").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.thickness_menu = tk.OptionMenu(calc_frame, self.thickness_var, *THICKNESS_OPTIONS)
        self.thickness_menu.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # Champ Type de sous-plancher
        tk.Label(calc_frame, text="Type de sous-plancher :").grid(row=1, column=4, padx=5, pady=5, sticky="e")
        self.subfloor_menu = tk.OptionMenu(calc_frame, self.subfloor_var, *SUBFLOOR_OPTIONS)
        self.subfloor_menu.grid(row=1, column=5, padx=5, pady=5, sticky="w")
        self.subfloor_var.set(DEFAULT_SUBFLOOR)  # Définir la valeur par défaut

        # Nouveaux champs dans Paramètres de calcul
        # Champ Transporteur de sable
        tk.Label(calc_frame, text="Transporteur de sable :").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        sable_data = self.db_manager.get_sable()
        transporters = sorted(set(row[1] for row in sable_data))  # Colonne 1 est transporteur
        self.sable_transporter_menu = tk.OptionMenu(calc_frame, self.sable_transporter_var, *transporters)
        self.sable_transporter_menu.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.sable_transporter_var.trace("w", self.update_truck_tonnage_options)  # Mettre à jour le tonnage dynamiquement

        # Champ Tonnage camion (tm)
        tk.Label(calc_frame, text="Tonnage camion (tm) :").grid(row=3, column=2, padx=5, pady=5, sticky="e")
        self.truck_tonnage_menu = tk.OptionMenu(calc_frame, self.truck_tonnage_var, "")
        self.truck_tonnage_menu.grid(row=3, column=3, padx=5, pady=5, sticky="w")

        # Champ Secteur de transport
        tk.Label(calc_frame, text="Secteur de transport :").grid(row=3, column=4, padx=5, pady=5, sticky="e")
        self.transport_sector_menu = tk.OptionMenu(calc_frame, self.transport_sector_var, "")
        self.transport_sector_menu.grid(row=3, column=5, padx=5, pady=5, sticky="w")

        # Nouveau champ Travaux en dégel
        tk.Label(calc_frame, text="Travaux en dégel :").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.thaw_work_check = tk.Checkbutton(calc_frame, variable=self.thaw_work_var)
        self.thaw_work_check.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Nouvelle section Produits et Fournisseurs
        prod_frame = ttk.LabelFrame(self.main_frame, text="Produits et Fournisseurs", padding=10)
        prod_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Champ Apprets et scellants
        tk.Label(prod_frame, text="Apprets et scellants :").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        sealant_data = self.db_manager.get_apprets_scellants()
        sealant_options = ["Aucun"] + sorted(set(row[1] for row in sealant_data))  # Colonne 1 est nom_produit
        self.sealant_menu = tk.OptionMenu(prod_frame, self.sealant_var, *sealant_options)
        self.sealant_menu.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(prod_frame, text="Total scellants et apprêts ($) :").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        tk.Label(prod_frame, textvariable=self.sealant_total_var, width=10, relief="solid", borderwidth=1, anchor="center").grid(row=0, column=3, padx=5, pady=5, sticky="w")

        tk.Label(prod_frame, text="Prix par sac ($) :").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        tk.Label(prod_frame, textvariable=self.prix_par_sac_var, width=10, relief="solid", borderwidth=1, anchor="center").grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Champ Quantité totale de sacs
        tk.Label(prod_frame, text="Quantité totale de sacs :").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        tk.Label(prod_frame, textvariable=self.total_sacs_var, width=10, relief="solid", borderwidth=1, anchor="center").grid(row=2, column=1, padx=5, pady=5, sticky="w")

        tk.Label(prod_frame, text="Quantité totale de sable (tm) :").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        tk.Label(prod_frame, textvariable=self.sable_total_var, width=12, relief="solid", borderwidth=1, anchor="center").grid(row=3, column=1, padx=5, pady=5, sticky="w")

        tk.Label(prod_frame, text="Nombre voyage de sable :").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        tk.Label(prod_frame, textvariable=self.nombre_voyages_var, width=10, relief="solid", borderwidth=1, anchor="center").grid(row=4, column=1, padx=5, pady=5, sticky="w")

        tk.Label(prod_frame, text="Prix total sable ($) :").grid(row=4, column=2, padx=5, pady=5, sticky="e")
        tk.Label(prod_frame, textvariable=self.prix_total_sable_var, width=12, relief="solid", borderwidth=1, anchor="center").grid(row=4, column=3, padx=5, pady=5, sticky="w")

        # Champ Prix total sacs
        tk.Label(prod_frame, text="Prix total sacs ($) :").grid(row=2, column=2, padx=5, pady=5, sticky="e")
        tk.Label(prod_frame, textvariable=self.prix_total_sacs_var, relief="solid", width=12, borderwidth=1).grid(row=2, column=3, padx=5, pady=5, sticky="w")


        # Nouvelle section Main d’œuvre et machinerie
        main_frame = ttk.LabelFrame(self.main_frame, text="Main d’œuvre et machinerie", padding=10)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Champ Type de main d’œuvre
        tk.Label(main_frame, text="Type de main d’œuvre :").grid(row=0, column=0, padx=5, pady=5, sticky="e")

        main_doeuvre_data = self.db_manager.get_main_doeuvre()
        metiers = [row[1] for row in main_doeuvre_data]  # Colonne 1 = metier
        self.type_main_var = tk.StringVar()
        if metiers:
            self.type_main_var.set(metiers[0])
        else:
            self.type_main_var.set("")

        self.main_doeuvre_menu = tk.OptionMenu(main_frame, self.type_main_var, *metiers)
        self.main_doeuvre_menu.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Si tu veux une action dynamique quand on sélectionne un métier :
        # self.type_main_var.trace("w", self.fonction_de_mise_a_jour)

        # Ajouter au dictionnaire des champs
        self.champs["Type main d’œuvre"] = self.type_main_var


        # Champ Type de pension
        tk.Label(main_frame, text="Type de pension :").grid(row=0, column=2, padx=5, pady=5, sticky="e")

        pension_data = self.db_manager.get_pensions()
        types_pension = [row[1] for row in pension_data]

        self.type_pension_var = tk.StringVar(value=types_pension[0] if types_pension else "")
        self.type_pension_var.trace("w", self.update_prix_total_pension)
        self.update_prix_total_pension()
       
        self.pension_menu = tk.OptionMenu(main_frame, self.type_pension_var, *types_pension)
        self.pension_menu.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.champs["Type de pension"] = self.type_pension_var




        # Champ Type de machinerie
        tk.Label(main_frame, text="Type de machinerie :").grid(row=1, column=0, padx=5, pady=5, sticky="e")

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
        self.type_machinerie_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Ajouter au dictionnaire des champs
        self.champs["Type machinerie"] = self.type_machinerie_var

        # Champ Prix total machinerie
        tk.Label(main_frame, text="Prix total machinerie ($) :").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.prix_total_machinerie_var = tk.StringVar(value="0.00")
        tk.Label(main_frame, textvariable=self.prix_total_machinerie_var, width=12, relief="solid", borderwidth=1, anchor="center").grid(row=1, column=3, padx=5, pady=5, sticky="w")




        # Champ Nombre d'hommes
        tk.Label(main_frame, text="Nombre d'hommes :").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        entry_nombre_hommes = tk.Entry(main_frame, textvariable=self.nombre_hommes_var, justify='center', width=10)
        entry_nombre_hommes.grid(row=2, column=1, padx=5, pady=5, sticky="w")


        # Champ Prix total pension


        tk.Label(main_frame, text="Prix total pension ($) :").grid(row=2, column=2, padx=5, pady=5, sticky="e")
        tk.Label(main_frame, textvariable=self.prix_total_pension_var, width=12, relief="solid", borderwidth=1, anchor="center").grid(row=2, column=3, padx=5, pady=5, sticky="w")



        # Ajouter au dictionnaire des champs
        self.champs["Nombre d'hommes"] = self.nombre_hommes_var

                # Champ Heures chantier calculées
        tk.Label(main_frame, text="Heures chantier calculées :").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        entry_heures_chantier = tk.Entry(main_frame, textvariable=self.heures_chantier_var, justify='center', width=10)
        entry_heures_chantier.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Ajouter au dictionnaire des champs si besoin
        self.champs["Heures chantier calculées"] = self.heures_chantier_var


        # Champ Heures transport calculées
        tk.Label(main_frame, text="Heures transport calculées :").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        entry_heures_transport = tk.Entry(main_frame, textvariable=self.heures_transport_var, justify='center', width=10)
        entry_heures_transport.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        self.champs["Heures transport calculées"] = self.heures_transport_var



        # Boutons
        tk.Button(self.window, text="Enregistrer", command=self.save_submission).pack(pady=10)
        tk.Button(self.window, text="Annuler", command=self.window.destroy).pack(pady=5)


    def update_prix_total_pension(self, *args):
        try:
            print("[DEBUG] → Appel update_prix_total_pension")
            type_pension = self.type_pension_var.get()
            nombre_hommes = self.nombre_hommes_var.get()
            print(f"[DEBUG] type_pension={type_pension}, nombre_hommes={nombre_hommes}")

            total = calculer_prix_total_pension(self.db_manager, type_pension, nombre_hommes)
            print(f"[DEBUG] total calculé : {total}")
            self.prix_total_pension_var.set(total)

        except Exception as e:
            print(f"[ERREUR] update_prix_total_pension : {e}")
            self.prix_total_pension_var.set("Erreur")




    def update_prix_total_machinerie(self, *args):
        try:
            type_machinerie = self.type_machinerie_var.get()
            heures_chantier = self.heures_chantier_var.get()
            heures_transport = self.heures_transport_var.get()
            total = calculer_prix_total_machinerie(self.db_manager, type_machinerie, heures_chantier, heures_transport)
            self.prix_total_machinerie_var.set(total)
        except Exception as e:
            print(f"[ERREUR] update_prix_total_machinerie : {e}")
            self.prix_total_machinerie_var.set("Erreur")



    def update_heures_transport(self, *args):
        print("[DEBUG] Appel de update_heures_transport")
        print(f"[DEBUG] distance_var actuelle : {self.distance_var.get()}")
        self.heures_transport_var.set(
            calculer_heures_transport(self.distance_var.get())
        )




    def update_heures_chantier(self, *args):
        superficie = self.area_var.get()
        heures = calculer_heures_chantier(superficie)
        self.heures_chantier_var.set(heures)
        self.update_prix_total_machinerie()


    def update_nombre_voyages(self, *args): 
        try:
            sable_str = self.sable_total_var.get()
            tonnage_str = self.truck_tonnage_var.get()

            print(f"[DEBUG] Valeurs récupérées : sable = {sable_str}, tonnage camion = {tonnage_str}")

            # Vérifier si les champs sont vides
            if not sable_str or not tonnage_str:
                self.nombre_voyages_var.set("0")
                return

            voyages = calculer_nombre_voyages_sable(sable_str, tonnage_str)
            print(f"[DEBUG] Résultat voyages : {voyages}")
            self.nombre_voyages_var.set(voyages)
        except Exception as e:
            print(f"[DEBUG] Erreur dans update_nombre_voyages : {e}")
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
            print(f"[DEBUG] Prix total sable affiché : {total}")
        except Exception as e:
            print(f"[DEBUG] Erreur dans update_prix_total_sable : {e}")
            self.prix_total_sable_var.set("Erreur")




    def update_sable_total(self, *args):
        nb_sacs = self.total_sacs_var.get()
        ratio = self.ratio_var.get()
        sable_total = calculer_quantite_sable(nb_sacs, ratio)
        self.sable_total_var.set(sable_total)


        if sable_total.isdigit():  # 👈 évite les erreurs si 'Erreur'
            self.update_nombre_voyages()


    def update_prix_total_sacs(self, *args):
        try:
            nb_sacs_str = self.total_sacs_var.get()
            prix_unitaire_str = self.prix_par_sac_var.get()

            print(f"[DEBUG] Valeur récupérée : total_sacs_var = '{nb_sacs_str}', prix_par_sac_var = '{prix_unitaire_str}'")

            nb_sacs = int(nb_sacs_str)
            prix_unitaire = float(prix_unitaire_str.replace(",", "."))

            total = nb_sacs * prix_unitaire
            print(f"[DEBUG] Total sacs = {nb_sacs}, Prix unitaire = {prix_unitaire}, Total = {total}")
            self.prix_total_sacs_var.set(f"{total:.2f}")
        except Exception as e:
            print(f"[DEBUG] Erreur dans update_prix_total_sacs : {e}")
            self.prix_total_sacs_var.set("0.00")

    





    def update_total_sacs(self, *args):
        superficie = self.area_var.get()
        epaisseur = self.thickness_var.get()
        produit = self.product_var.get()
        ratio = self.ratio_var.get()

        result = calculate_total_sacs(superficie, epaisseur, produit, ratio, self.db_manager)
        print(f"[DEBUG] Résultat total sacs : {result}")
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
        """Mettre à jour les options de tonnage et secteur en fonction du transporteur sélectionné."""
        selected_transporter = self.sable_transporter_var.get()
        truck_tonnages = get_truck_tonnages(self.db_manager, selected_transporter) if selected_transporter else []
        transport_sectors = sorted(set(row[3] for row in self.db_manager.get_sable() if row[1] == selected_transporter)) if selected_transporter else []

        # Mettre à jour le menu Tonnage camion
        menu_tonnage = self.truck_tonnage_menu["menu"]
        menu_tonnage.delete(0, "end")
        for tonnage in truck_tonnages:
            menu_tonnage.add_command(label=str(tonnage), command=lambda x=str(tonnage): self.truck_tonnage_var.set(x))
        self.truck_tonnage_menu.config(state="normal" if truck_tonnages else "disabled")
        if truck_tonnages:
            self.truck_tonnage_var.set(str(truck_tonnages[0]))  # Définir le premier tonnage par défaut
        else:
            self.truck_tonnage_var.set("")

        # Mettre à jour le menu Secteur de transport
        menu_sector = self.transport_sector_menu["menu"]
        menu_sector.delete(0, "end")
        for sector in transport_sectors:
            menu_sector.add_command(label=sector, command=lambda x=sector: self.transport_sector_var.set(x))
        self.transport_sector_menu.config(state="normal" if transport_sectors else "disabled")
        if transport_sectors:
            self.transport_sector_var.set(transport_sectors[0])  # Définir la première ville par défaut
        else:
            self.transport_sector_var.set("")

    def generate_submission_number(self):
        current_year = datetime.now().year
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT MAX(sequence) FROM submissions WHERE year = ?
            """, (current_year,))
            max_sequence = cursor.fetchone()[0]
            new_sequence = 1 if max_sequence is None else max_sequence + 1
            submission_number = f"S{current_year % 100:02d}-{new_sequence:03d}"
            self.submission_number_var.set(submission_number)

    def save_submission(self):
        try:
            client_name = self.client_var.get()
            contact = self.contact_var.get()
            date_submission = self.date_var.get()
            submission_number = self.submission_number_var.get()
            projet = self.projet_var.get("1.0", tk.END).strip()
            ville = self.ville_var.get()
            distance = self.distance_var.get()
            notes = self.notes_data  # Inclure les notes temporaires
            surfaces = self.surface_data  # Inclure les surfaces temporaires
            area = self.area_var.get()
            product = self.product_var.get()
            ratio = self.ratio_var.get()
            usd_cad_rate = self.usd_cad_rate_var.get()
            thickness = self.thickness_var.get()
            subfloor = self.subfloor_var.get()

            if not client_name or not contact or not date_submission or not projet or not ville or not area:
                raise ValueError("Tous les champs sont requis")

            # Pour l'instant, afficher les données (sauvegarde dans la base à venir)
            message = f"Soumission {submission_number} prête à être sauvegardée.\nNotes : {notes}\nSurfaces : {surfaces}\nParamètres : Superficie={area}, Produit={product}, Ratio={ratio}, Taux USD/CAD={usd_cad_rate}, Épaisseur={thickness}, Type de sous-plancher={subfloor}"
            messagebox.showinfo("Info", message)
            self.window.destroy()  # Ferme la fenêtre et efface les données
            self.notes_data.clear()  # Efface les notes après enregistrement
            self.surface_data.clear()  # Efface les surfaces après enregistrement
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur : {e}")

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