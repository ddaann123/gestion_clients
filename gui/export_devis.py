
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import openpyxl
import os
import re

class ExportDevisWindow:
    def __init__(self, parent, submission_data, db_manager):
        self.db_manager = db_manager
        self.submission_data = submission_data
        self.window = tk.Toplevel(parent)
        self.window.title("Générer le devis")
        self.window.geometry("600x650")
        self.main_frame = tk.Frame(self.window)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)


        self.clauses_texts = {
            "Insonorisation standard": """UNE ALIMENTATION EN EAU EST REQUISE SUR LE BATIMENT PRINCIPAL (2 SORTIES 3/4'' MINIMUM).

UN ESPACE DE STATIONNEMENT D'ENVIRON 150' EST REQUIS EN AVANT DE L'IMMEUBLE POUR NOS OPÉRATION ET ÉQUIPEMENTS.
L'ACCES AU CHANTIER DOIT ETRE LIBRE ET ACCESSIBLE AVEC NOS CAMIONS REMORQUES 53'.

UN ARRET DE COULÉE 2X4''A PLAT DOIT ETRE INSTALLÉ À CHAQUE SEUIL DE PORTE OU PALIER PAR VOTRE ÉQUIPE AVANT NOTRE ARRIVÉE.

UN COUVRE PLANCHER EST REQUIS SUR LE BÉTON AUTONIVELANT.

POUR LA POSE DE REVETEMENTS SOUPLES, VEUILLEZ VOUS RÉFÉRER AUX RECOMMANDATIONS DU FABRICANT DE COUVRE-PLANCHER RELATIVEMENT A LA POSE SUR SUBSTRAT À BASE DE GYPSE. UNE PRÉPARATION PEUT ETRE EXIGÉE (APPRETS, SABLAGE, GLAISAGE OU AUTRE).
""",
            "Planchers radiants": """LE FIL ÉLECTRIQUE OU LA CONDUITE D'EAU DOIT ETRE SOLIDEMENT FIXÉE AFIN D'ÉVITER UN SOULEVEMENT LORS DE LA COULÉE. NOUS RECOMMANDONS DES ATTACHES AU 12'' A 16'' MAXIMUM. AUCUNE GARANTIE NE S'APPLIQUE POUR DES PROBLEMES RÉSULTANT D'UN SOULEVEMENT DU SYSTEME RADIANT.
""",
            "Coulée sur béton": """LE TAUX D'HUMIDITÉ DE DALLE DE BÉTON EXISTANTE DOIT ETRE INFÉRIEUR A 4.0% AU TRAMEX ET DEMEURER STABLE DANS LE TEMPS. NOS PRODUITS AUTONIVELANTS NE SONT PAS CONCUS POUR UNE EXPOSITION PROLONGÉE À LA VAPEUR D'EAU.  AUCUNE GARANTIE NE S'APPLIQUE POUR LES PROBLEMES POUVANT RÉSULTER D'UNE HUMDITÉ TROP ÉLEVÉE.
""",
        }

        self.clause_vars = {
            key: tk.BooleanVar(value=(key == "Insonorisation standard"))
            for key in self.clauses_texts
        }

        self.repere_var = tk.BooleanVar(value=False)
        self.termes_var = tk.StringVar(value="NET JOUR DES TRAVAUX")

        self.marche_var = tk.BooleanVar(value=False)
        self.epaisseur_var = tk.StringVar(value="1-1/4''")
        self.quantite_var = tk.StringVar()


        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        row = 0
        tk.Label(main_frame, text="CHAMPS MODIFIABLES À EXPORTER :", font=("Arial", 11, "bold")).grid(row=row, column=0, pady=10, sticky="w")


        self.entries = {}
        for label, key in [
            ("Client", "client_name"),
            ("Projet", "projet"),
            ("Contact", "contact"),
            ("Ville", "ville"),
        ]:
            

            row += 1
            tk.Label(main_frame, text=label + ":").grid(row=row, column=0, sticky="w", padx=10)
            var = tk.StringVar(value=self.submission_data.get(key, "").upper())
            entry = tk.Entry(main_frame, textvariable=var, width=40)
            entry.grid(row=row, column=1, sticky="w")
            self.entries[key] = var

        # ➕ Surface totale (readonly)
        row += 1
        tk.Label(main_frame, text="Surface totale (pi²):").grid(row=row, column=0, sticky="w", padx=10)
        self.surface_totale_var = tk.StringVar()
        entry_surface = tk.Entry(main_frame, textvariable=self.surface_totale_var, width=40, state="readonly")
        entry_surface.grid(row=row, column=1, sticky="w")


        row += 1
        tk.Label(main_frame, text="CLAUSES À INCLURE :", font=("Arial", 11, "bold")).grid(row=row, column=0, pady=(20, 5), sticky="w")


        for clause, var in self.clause_vars.items():
            row += 1
            tk.Checkbutton(main_frame, text=clause, variable=var).grid(row=row, column=0, columnspan=2, sticky="w", padx=20)

        row += 1
        tk.Checkbutton(main_frame, text="Repère de nivellement", variable=self.repere_var).grid(row=row, column=0, columnspan=2, sticky="w", padx=20, pady=(5, 10))

        # Case à cocher "Marche d'escalier"
        row += 1
        tk.Checkbutton(main_frame, text="Marche d'escalier", variable=self.marche_var, command=self.toggle_marche_fields).grid(row=row, column=0, columnspan=2, sticky="w", padx=20)

        # Champs conditionnels
        self.marche_fields_frame = tk.Frame(main_frame)


        row += 1
        tk.Label(main_frame, text="Termes de paiement:").grid(row=row, column=0, sticky="w", padx=10)
        options = ["NET JOUR DES TRAVAUX", "CH.POSTDATE 30 JRS", "NET 30 JOURS"]
        tk.OptionMenu(main_frame, self.termes_var, *options).grid(row=row, column=1, sticky="w")

        try:
            area = float(self.submission_data.get("area", "0").replace(",", ""))
            mobilisations = float(self.submission_data.get("mobilisations", "0").replace(",", ""))
            surface_totale = round(area * mobilisations, 2)

            self.surface_totale_var.set(str(surface_totale))
        except Exception as e:
            print(f"[DEBUG] Erreur calcul surface : {e}")
            self.surface_totale_var.set("")




        row += 1
        tk.Label(self.marche_fields_frame, text="Épaisseur :").grid(row=0, column=0, sticky="e", padx=5)
        epaisseur_menu = tk.OptionMenu(self.marche_fields_frame, self.epaisseur_var, "1-1/4''", "1-1/2''", "2''")
        epaisseur_menu.grid(row=0, column=1, sticky="w", padx=5)

        tk.Label(self.marche_fields_frame, text="Quantité :").grid(row=1, column=0, sticky="e", padx=5)
        tk.Entry(self.marche_fields_frame, textvariable=self.quantite_var, width=10).grid(row=1, column=1, sticky="w", padx=5)



        row += 1
        tk.Button(main_frame, text="Exporter vers Excel", command=self.export_to_excel).grid(row=row, column=0, columnspan=2, pady=20)

    def toggle_marche_fields(self):
        if self.marche_var.get():
            self.marche_fields_frame.grid(row=99, column=0, columnspan=2, padx=20, pady=(0,10), sticky="w")
        else:
            self.marche_fields_frame.grid_forget()



    def export_to_excel(self):
        try:
            wb = openpyxl.load_workbook("c:/gestion_clients/models/Devis_PBL.xlsx")
            ws = wb.active

            ws["B14"] = self.entries["client_name"].get()
            ws["I18"] = self.entries["projet"].get()
            ws["B16"] = self.entries["contact"].get()

            contact_nom = self.entries["contact"].get()
            infos_contact = self.db_manager.get_contact_by_name(contact_nom)
            if infos_contact:
                telephone, courriel = infos_contact
                ws["B18"] = telephone
                ws["B22"] = courriel

            ws["B34"] = self.submission_data.get("product", "")
            ws["I14"] = self.submission_data.get("submission_number", "")
            ws["I16"] = self.submission_data.get("date_submission", datetime.now().strftime("%Y-%m-%d"))
            ws["F34"] = self.surface_totale_var.get()

            ws["E34"] = self.submission_data.get("thickness", "")
            ws["J34"] = self.submission_data.get("prix_unitaire", "")
            ws["E27"] = self.submission_data.get("mobilisations", "")
            ws["J28"] = self.termes_var.get()
            if self.repere_var.get():
                ws["E28"] = "OUI"

            texte = ""
            for clause, var in self.clause_vars.items():
                if var.get():
                    texte += self.clauses_texts[clause]
            ws["B26"] = texte.strip()
            

            print(f"[DEBUG] Toutes les clés dans submission_data : {list(self.submission_data.keys())}")

            membrane = self.submission_data.get("membrane", "").strip()
            print(f"[DEBUG] Nom de membrane brut : {repr(membrane)}")

            if membrane and membrane.upper() != "AUCUNE":
                print("[DEBUG] Une membrane a été sélectionnée, tentative d’export.")
                ws["B37"] = membrane
                ws["B38"] = "   POSE SANS DIVISIONS"
                ws["B39"] = "   POSE AVEC DIVISIONS"
                ws["E38"] = "PI²"
                ws["E39"] = "PI²"

                try:
                    membrane_data = self.db_manager.get_membrane_by_nom(membrane)
                    print(f"[DEBUG] Résultat de get_membrane_by_nom : {membrane_data}")
                    if membrane_data:
                        prix_rouleau, prix_sans_div, prix_avec_div = membrane_data
                        total_sans_div = round(prix_rouleau + prix_sans_div, 2)
                        total_avec_div = round(prix_rouleau + prix_avec_div, 2)
                        ws["J38"] = total_sans_div
                        ws["J39"] = total_avec_div
                        ws["F38"] = ws["F34"].value
                        ws["F39"] = ws["F34"].value

                except Exception as e:
                    print(f"[ERREUR] Impossible de récupérer les prix de la membrane : {e}")
             


            if self.marche_var.get():
                ws["B41"] = "REMPLISSAGE PANNE DE MARCHE"
                ws["E41"] = self.epaisseur_var.get()
                ws["F41"] = self.quantite_var.get()
                ws["I41"] = "UN"
                ws["J41"] = "18.00"




            dossier_export = r"G:\Mon disque\SOUMISSIONS DL"
            os.makedirs(dossier_export, exist_ok=True)
            submission = self.submission_data.get("submission_number", "")
            client = self.entries["client_name"].get().upper()
            projet = self.entries["projet"].get().upper()
            date = self.submission_data.get("date_submission", datetime.now().strftime("%Y-%m-%d"))

            def nettoyer(texte):
                return re.sub(r'[\\/*?:"<>|]', '', texte.strip())

            nom_fichier = f"{nettoyer(submission)} - {nettoyer(client)} - {nettoyer(projet)} - {nettoyer(date)}.xlsx"
            chemin_export = os.path.join(dossier_export, nom_fichier)

            wb.save(chemin_export)
            messagebox.showinfo("Succès", f"Devis exporté à :\n{chemin_export}")
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export : {e}")
