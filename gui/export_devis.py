
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import openpyxl
import os
import re
import xlwings as xw


class ExportDevisWindow:
    def __init__(self, parent, submission_data, db_manager):
        self.db_manager = db_manager
        self.submission_data = submission_data
        self.window = tk.Toplevel(parent)
        self.window.title("Générer le devis")
        self.window.geometry("600x600")
        self.main_frame = tk.Frame(self.window)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.main_frame.rowconfigure(999, weight=1)


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
        tk.Checkbutton(main_frame, text="Marche d'escalier", variable=self.marche_var, command=self.toggle_marche_fields).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=20)

        # Termes de paiement
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

        # Préparation du frame pour les champs marche d’escalier
        self.marche_row = row + 1
        self.marche_fields_frame = tk.Frame(main_frame)

        # Contenu du frame (mais on ne l’affiche pas encore)
        tk.Label(self.marche_fields_frame, text="Épaisseur :").grid(row=0, column=0, sticky="e", padx=5)
        epaisseur_menu = tk.OptionMenu(self.marche_fields_frame, self.epaisseur_var, "1-1/4''", "1-1/2''", "2''")
        epaisseur_menu.grid(row=0, column=1, sticky="w", padx=5)

        tk.Label(self.marche_fields_frame, text="Quantité :").grid(row=1, column=0, sticky="e", padx=5)
        tk.Entry(self.marche_fields_frame, textvariable=self.quantite_var, width=10).grid(row=1, column=1, sticky="w", padx=5)

        # Configuration pour forcer la dernière rangée à pousser vers le bas
        main_frame.rowconfigure(999, weight=1)

        # Bouton "Exporter vers Excel" toujours en bas
        tk.Button(main_frame, text="Exporter vers Excel", command=self.export_to_excel).grid(
            row=999, column=0, columnspan=2, pady=20, sticky="s")


    def toggle_marche_fields(self):
        if self.marche_var.get():
            self.marche_fields_frame.grid(row=self.marche_row, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="w")
        else:
            self.marche_fields_frame.grid_forget()






    def export_to_excel(self):
        try:
            chemin_modele = "c:/gestion_clients/models/Devis_PBL.xlsx"
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

            app = xw.App(visible=False)
            wb = app.books.open(chemin_modele)
            ws = wb.sheets[0]

            ws.range("B14").value = self.entries["client_name"].get()
            ws.range("I18").value = self.entries["projet"].get()
            ws.range("B16").value = self.entries["contact"].get()

            contact_nom = self.entries["contact"].get()
            infos_contact = self.db_manager.get_contact_by_name(contact_nom)
            if infos_contact:
                telephone, courriel = infos_contact
                ws.range("B18").value = telephone
                ws.range("B22").value = courriel

            ws.range("B34").value = self.submission_data.get("product", "")
            ws.range("I14").value = submission
            ws.range("I16").value = date
            ws.range("F34").value = self.surface_totale_var.get()
            ws.range("E34").value = self.submission_data.get("thickness", "")
            ws.range("J34").value = self.submission_data.get("prix_unitaire", "")
            ws.range("E27").value = self.submission_data.get("mobilisations", "")
            ws.range("J28").value = self.termes_var.get()
            if self.repere_var.get():
                ws.range("E28").value = "OUI"

            texte = ""
            for clause, var in self.clause_vars.items():
                if var.get():
                    texte += self.clauses_texts[clause]
            ws.range("B26").value = texte.strip()

            membrane = self.submission_data.get("membrane", "").strip()
            if membrane and membrane.upper() != "AUCUNE":
                ws.range("B37").value = membrane
                ws.range("E38").value = "1/8\""
                ws.range("E39").value = "1/8\""
                ws.range("B38").value = "   POSE SANS DIVISIONS"
                ws.range("B39").value = "   POSE AVEC DIVISIONS"
                ws.range("I38").value = "PI²"
                ws.range("I39").value = "PI²"

                try:
                    membrane_data = self.db_manager.get_membrane_by_nom(membrane)
                    if membrane_data:
                        prix_rouleau, prix_sans_div, prix_avec_div = membrane_data
                        total_sans_div = round(prix_rouleau + prix_sans_div, 2)
                        total_avec_div = round(prix_rouleau + prix_avec_div, 2)
                        ws.range("J38").value = total_sans_div
                        ws.range("J39").value = total_avec_div
                        ws.range("F38").value = ws.range("F34").value
                        ws.range("F39").value = ws.range("F34").value
                except Exception as e:
                    print(f"[ERREUR] Prix membrane : {e}")

            if self.marche_var.get():
                ws.range("B41").value = "REMPLISSAGE PANNE DE MARCHE"
                ws.range("E41").value = self.epaisseur_var.get()
                ws.range("F41").value = self.quantite_var.get()
                ws.range("I41").value = "UN"
                ws.range("J41").value = "18.00"

            wb.save(chemin_export)
            wb.close()
            app.quit()

            messagebox.showinfo("Succès", f"Devis exporté à :\n{chemin_export}")
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export : {e}")
