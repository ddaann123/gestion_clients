import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from datetime import datetime


class SubmissionSearchWindow:
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager

        self.window = ttkb.Toplevel(parent)
        self.window.title("Recherche de soumissions")
        self.window.geometry("1100x900")

        self.create_widgets()

    def create_widgets(self):
        search_frame = ttkb.Frame(self.window)
        search_frame.pack(fill="x", padx=10, pady=10)

        # Champs de recherche
        self.vars = {
            'submission_number': ttkb.StringVar(),
            'client_name': ttkb.StringVar(),
            'contact': ttkb.StringVar(),
            'projet': ttkb.StringVar(),
            'ville': ttkb.StringVar(),
            'etat': ttkb.StringVar(),
            'date_debut': ttkb.StringVar(),
            'date_fin': ttkb.StringVar(),
        }

        row = 0
        for label, key in [
            ("Numéro soumission:", 'submission_number'),
            ("Client:", 'client_name'),
            ("Contact:", 'contact'),
            ("Projet:", 'projet'),
            ("Ville:", 'ville'),
            ("État:", 'etat'),
            ("Date début (AAAA-MM-JJ):", 'date_debut'),
            ("Date fin (AAAA-MM-JJ):", 'date_fin'),
        ]:
            ttkb.Label(search_frame, text=label).grid(row=row, column=0, sticky="e", padx=5, pady=3)
            ttkb.Entry(search_frame, textvariable=self.vars[key], width=30).grid(row=row, column=1, sticky="w", padx=5)
            row += 1

        ttkb.Button(search_frame, text="Rechercher", command=self.rechercher, bootstyle=PRIMARY).grid(row=row, column=0, columnspan=2, pady=10)

        self.tree = ttkb.Treeview(
            self.window,
            columns=("submission_number", "client_name", "contact", "projet", "ville", "etat", "date_submission"),
            show="headings",
            bootstyle="dark"
        )

        for col, label in zip(self.tree["columns"], [
            "Soumission", "Client", "Contact", "Projet", "Ville", "État", "Date"]):
            self.tree.heading(col, text=label)
            self.tree.column(col, width=120)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", self.ouvrir_soumission)

        ttkb.Button(self.window, text="Supprimer la soumission sélectionnée", command=self.supprimer_soumission, bootstyle=DANGER).pack(pady=(0, 10))

    def supprimer_soumission(self):
        item = self.tree.focus()
        if not item:
            Messagebox.show_warning("Veuillez sélectionner une soumission à supprimer.")
            return

        submission_number = self.tree.item(item)["values"][0]

        message = (
            f"⚠️ Cette action est irréversible.\n\n"
            f"Voulez-vous VRAIMENT supprimer définitivement la soumission :\n\n"
            f"{submission_number} ?"
        )

        confirmation = Messagebox.yesno("Confirmation de suppression", message)

        if confirmation:
            try:
                self.db_manager.supprimer_soumission(submission_number)
                Messagebox.show_info(f"La soumission {submission_number} a été supprimée définitivement.")
                self.rechercher()
            except Exception as e:
                Messagebox.show_error(f"Erreur lors de la suppression : {e}")

    def rechercher(self):
        criteres = {k: v.get().strip() for k, v in self.vars.items() if v.get().strip() != ""}
        try:
            resultats = self.db_manager.search_submissions(criteres)
            self.tree.delete(*self.tree.get_children())
            for row in resultats:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            Messagebox.show_error(f"Erreur lors de la recherche : {e}")

    def ouvrir_soumission(self, event):
        item = self.tree.focus()
        if not item:
            return
        submission_number = self.tree.item(item)['values'][0]
        print(f"[DEBUG] Numéro de soumission sélectionné : {submission_number}")
        try:
            from gui.submission_form import SubmissionForm
            data = self.db_manager.charger_soumission(submission_number)
            print(f"[DEBUG] Données chargées : {data}")
            if data:
                SubmissionForm(self.window, self.db_manager, existing_submission=data)
            else:
                Messagebox.show_error("Soumission introuvable")
        except Exception as e:
            Messagebox.show_error(f"Erreur lors de l'ouverture : {e}")
