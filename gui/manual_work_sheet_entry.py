import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
import re
import json

class ManualWorkSheetEntry:
    def __init__(self, parent, form_html, submission_data, db_manager, pose_membrane_value=""):
        self.submission_data = submission_data
        self.db_manager = db_manager
        self.form_html = form_html
        self.pose_membrane_value = pose_membrane_value

        self.window = tk.Toplevel(parent)
        self.window.title("Entrée manuelle feuille de travail")
        self.window.geometry("1200x900")

        # Canvas avec scrollbar
        canvas = tk.Canvas(self.window)
        scrollbar = tk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

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
        tk.Label(self.scrollable_frame, text="FEUILLE DE TRAVAIL - ENTREE MANUELLE", font=("Arial", 16, "bold")).pack(pady=10)

        # Conteneur principal
        main_frame = tk.Frame(self.scrollable_frame)
        main_frame.pack(padx=20, pady=20)

        # Section supérieure : Champs automatiques
        upper_frame = tk.Frame(main_frame)
        upper_frame.pack(fill="x", pady=10)

        self.widgets = {}
        self.parse_html(upper_frame, form_html)

        # Section tableau des heures
        hours_frame = tk.LabelFrame(main_frame, text="Heures chantier", font=("Arial", 12, "bold"))
        hours_frame.pack(fill="both", expand=True, pady=10, padx=10)

        self.create_hours_table(hours_frame)

        # Bouton d'enregistrement
        tk.Button(self.scrollable_frame, text="Enregistrer", command=self.save_work_sheet).pack(pady=20)

    def parse_html(self, parent, html):
        lines = html.split("\n")
        row = 0
        col = 0
        max_cols = 2

        table_start_idx = -1
        for i, line in enumerate(lines):
            if '<table' in line:
                table_start_idx = i
                break

        for line in lines[:table_start_idx]:  # Arrêter avant la table
            line = line.strip()
            if '<div class="form-row">' in line:
                col = 0
                row += 1
            elif '<label>' in line and '</label>' in line:
                label = re.search(r'<label>(.*?)</label>', line).group(1)
                tk.Label(parent, text=label, font=("Arial", 10)).grid(row=row, column=col * 2, sticky="e", padx=5, pady=5)
                col += 1
            elif '<input' in line:
                name = re.search(r'name="([^"]*)"', line).group(1)
                value = re.search(r'value="([^"]*)"', line)
                readonly = 'readonly' in line
                var = tk.StringVar(value=value.group(1) if value else "")
                entry = tk.Entry(parent, textvariable=var, state="normal" if not readonly else "readonly", width=40)
                entry.grid(row=row, column=(col * 2) + 1, sticky="w", padx=5, pady=5)
                self.widgets[name] = var
                if col >= max_cols - 1:
                    row += 1
                    col = 0
                else:
                    col += 1
            elif '<select' in line:
                name = re.search(r'name="([^"]*)"', line).group(1)
                var = tk.StringVar()
                if name == "produit_diff":
                    options = ["Maxcrete", "Surface Gyp", "Autre"]
                    var.set("")  # Default to empty
                elif name == "membrane_posee":
                    options = ["OUI", "NON", "OUI AVEC DIVISIONS", "OUI SANS DIVISIONS", "OUI POSE MIXTE", "PAR CLIENT"]
                    var.set(self.pose_membrane_value if self.pose_membrane_value in options else "")  # Set default from pose_membrane_value
                else:
                    options = self.extract_options(line)
                    var.set("")  # Default to empty for other dropdowns
                menu = ttk.OptionMenu(parent, var, var.get(), *options)
                menu.grid(row=row, column=(col * 2) + 1, sticky="w", padx=5, pady=5)
                self.widgets[name] = var
                if col >= max_cols - 1:
                    row += 1
                    col = 0
                else:
                    col += 1
            elif '<textarea' in line:
                name = re.search(r'name="([^"]*)"', line).group(1)
                value = re.search(r'>(.*?)</textarea>', line, re.DOTALL).group(1).strip()
                var = tk.Text(parent, height=3 if "rows=3" in line else 4, width=50)
                var.insert("1.0", value)
                var.grid(row=row, column=1, columnspan=3, sticky="w", padx=5, pady=5)
                self.widgets[name] = var
                row += 1
                col = 0
            elif '<h3>' in line:
                header = re.search(r'<h3>(.*?)</h3>', line).group(1)
                tk.Label(parent, text=header, font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=4, pady=(10, 5))
                row += 1
                col = 0

    def extract_options(self, line):
        options = re.findall(r'<option value="([^"]*)">(?:[^<]*)</option>', line)
        return options if options else [""]

    def create_hours_table(self, parent):
        time_choices = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 15, 30, 45)]
        transport_choices = [f"{h:02d}:{m:02d}" for h in range(13) for m in (0, 15, 30, 45)]

        headers = ["Employé", "Présence", "Véhicule", "Chauffeur Aller", "Chauffeur Retour", "Heure Début", "Heure Fin", "Total Heures", "Temps Transport", "Heures Entrepôt"]
        for col, header in enumerate(headers):
            tk.Label(parent, text=header, font=("Arial", 10, "bold"), borderwidth=1, relief="solid").grid(row=0, column=col, padx=2, pady=2, sticky="nsew")

        self.presence_vars = []
        self.heure_debut_vars = []
        self.heure_fin_vars = []
        self.total_heures_labels = []
        self.temps_transport_vars = []
        self.heures_entrepot_vars = []

        def calculer_total(i):
            debut = self.heure_debut_vars[i].get()
            fin = self.heure_fin_vars[i].get()
            try:
                if debut and fin:
                    fmt = "%H:%M"
                    d = datetime.strptime(debut, fmt)
                    f = datetime.strptime(fin, fmt)
                    diff = (f - d).seconds / 3600
                    self.total_heures_labels[i].config(text=f"{diff:.2f}")
                else:
                    self.total_heures_labels[i].config(text="-")
            except:
                self.total_heures_labels[i].config(text="?")

        def sync_hours(*args):
            present_indices = [i for i, var in enumerate(self.presence_vars) if var.get()]
            if present_indices and self.heure_debut_vars[0].get() and self.heure_fin_vars[0].get() and self.temps_transport_vars[0].get() and self.heures_entrepot_vars[0].get():
                for i in present_indices[1:]:  # Exclure le premier employé
                    self.heure_debut_vars[i].set(self.heure_debut_vars[0].get())
                    self.heure_fin_vars[i].set(self.heure_fin_vars[0].get())
                    self.temps_transport_vars[i].set(self.temps_transport_vars[0].get())
                    self.heures_entrepot_vars[i].set(self.heures_entrepot_vars[0].get())
                    calculer_total(i)

        employes = ["KASSIM GOSSELIN", "ALEX VALOIS", "KARL", "ANTHONY ALLAIRE", "MARC POTHIER", "NATHAN", "ANTHONY LABBÉ", "JONATHAN GRENIER"]
        for i, employe in enumerate(employes + [""] * 3, start=1):
            tk.Label(parent, text=employe if employe else "", borderwidth=1, relief="solid").grid(row=i, column=0, padx=2, pady=2, sticky="nsew")
            presence_var = tk.BooleanVar()
            self.presence_vars.append(presence_var)
            tk.Checkbutton(parent, variable=presence_var, command=sync_hours).grid(row=i, column=1, padx=2, pady=2, sticky="nsew")
            ttk.OptionMenu(parent, tk.StringVar(), "", "West", "Inter", "Hino", "Duramax 3500", "Duramax 2500").grid(row=i, column=2, padx=2, pady=2, sticky="nsew")
            tk.Checkbutton(parent, variable=tk.BooleanVar()).grid(row=i, column=3, padx=2, pady=2, sticky="nsew")
            tk.Checkbutton(parent, variable=tk.BooleanVar()).grid(row=i, column=4, padx=2, pady=2, sticky="nsew")

            var_debut = tk.StringVar()
            var_fin = tk.StringVar()
            var_transport = tk.StringVar()
            var_entrepot = tk.StringVar()
            self.heure_debut_vars.append(var_debut)
            self.heure_fin_vars.append(var_fin)
            self.temps_transport_vars.append(var_transport)
            self.heures_entrepot_vars.append(var_entrepot)

            ttk.OptionMenu(parent, var_debut, "", *time_choices, command=lambda _, j=i-1: [calculer_total(j), sync_hours()]).grid(row=i, column=5, padx=2, pady=2, sticky="nsew")
            ttk.OptionMenu(parent, var_fin, "", *time_choices, command=lambda _, j=i-1: [calculer_total(j), sync_hours()]).grid(row=i, column=6, padx=2, pady=2, sticky="nsew")
            total_label = tk.Label(parent, text="-", borderwidth=1, relief="solid")
            total_label.grid(row=i, column=7, padx=2, pady=2, sticky="nsew")
            self.total_heures_labels.append(total_label)
            ttk.OptionMenu(parent, var_transport, "", *transport_choices, command=sync_hours).grid(row=i, column=8, padx=2, pady=2, sticky="nsew")
            ttk.OptionMenu(parent, var_entrepot, "", *transport_choices, command=sync_hours).grid(row=i, column=9, padx=2, pady=2, sticky="nsew")

        for col in range(10):
            parent.grid_columnconfigure(col, weight=1)

    def save_work_sheet(self):
        try:
            data = {
                "soumission_reel": self.widgets.get("soumission", tk.StringVar(value="")).get(),
                "client_reel": self.widgets.get("client", tk.StringVar(value="")).get(),
                "superficie_reel": self.submission_data.get("area", ""),
                "produit_reel": self.submission_data.get("product", ""),
                "produit_diff": self.widgets.get("produit_diff", tk.StringVar(value="")).get(),
                "sable_total_reel": self.submission_data.get("sable_total", ""),
                "sable_transporter_reel": self.submission_data.get("sable_transporter", ""),
                "sable_commande_reel": self.widgets.get("sable_commande", tk.StringVar(value="")).get(),
                "sacs_utilises_reel": self.widgets.get("sacs_utilises", tk.StringVar(value="")).get(),
                "sable_utilise_reel": self.widgets.get("sable_utilise", tk.StringVar(value="")).get(),
                "membrane_posee_reel": self.widgets.get("membrane_posee", tk.StringVar(value="")).get(),
                "nb_rouleaux_installes_reel": self.widgets.get("nb_rouleaux_installes", tk.StringVar(value="")).get(),
                "marches_reel": self.widgets.get("marches_reel", tk.StringVar(value="")).get(),
                "notes_reel": self.widgets.get("notes_chantier", tk.Text()).get("1.0", "end").strip(),
                "date_travaux": self.widgets.get("date_travaux", tk.StringVar(value="")).get(),
                "date_soumission": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "donnees_json": json.dumps({"heures_chantier": {}}),
                "adresse_reel": self.submission_data.get("ville", ""),
                "type_membrane": self.submission_data.get("membrane", ""),
                "nb_sacs_prevus": self.submission_data.get("total_sacs", ""),
                "thickness": self.submission_data.get("thickness", ""),
                "notes_bureau": self.widgets.get("notes_bureau", tk.Text()).get("1.0", "end").strip()
            }

            # Collecter les heures chantier
            heures_chantier = {}
            hours_frame = self.scrollable_frame.winfo_children()[1]  # Accéder au LabelFrame
            for i in range(1, 12):  # 11 lignes (8 fixes + 3 personnalisées)
                employe = hours_frame.grid_slaves(row=i, column=0)[0].get() if i > 8 else hours_frame.grid_slaves(row=i, column=0)[0]["text"]
                presence = self.presence_vars[i-1].get()
                vehicule = hours_frame.grid_slaves(row=i, column=2)[0].getvar()
                chauffeur_aller = hours_frame.grid_slaves(row=i, column=3)[0].getvar()
                chauffeur_retour = hours_frame.grid_slaves(row=i, column=4)[0].getvar()
                heure_debut = self.heure_debut_vars[i-1].get()
                heure_fin = self.heure_fin_vars[i-1].get()
                temps_transport = self.temps_transport_vars[i-1].get()
                heures_entrepot = self.heures_entrepot_vars[i-1].get()

                heures_chantier[employe] = {
                    "presence": "1" if presence else "",
                    "vehicule": vehicule,
                    "chauffeur_aller": "1" if chauffeur_aller else "",
                    "chauffeur_retour": "1" if chauffeur_retour else "",
                    "heure_debut": heure_debut,
                    "heure_fin": heure_fin,
                    "temps_transport": temps_transport,
                    "heures_entrepot": heures_entrepot
                }
            data["donnees_json"] = json.dumps({"heures_chantier": heures_chantier})

            self.db_manager.insert_work_sheet(data)
            messagebox.showinfo("Succès", f"Feuille de travail enregistrée avec succès pour {data['soumission_reel']}")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement : {str(e)}")