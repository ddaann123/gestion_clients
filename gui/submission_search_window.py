import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class SubmissionSearchWindow:
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.window = tk.Toplevel(parent)
        self.window.title("Recherche de soumissions")
        self.window.geometry("900x900")

        self.create_widgets()

    def create_widgets(self):
        search_frame = tk.Frame(self.window)
        search_frame.pack(fill="x", padx=10, pady=10)

        # Champs de recherche
        self.vars = {
            'submission_number': tk.StringVar(),
            'client_name': tk.StringVar(),
            'contact': tk.StringVar(),
            'projet': tk.StringVar(),
            'ville': tk.StringVar(),
            'etat': tk.StringVar(),
            'date_debut': tk.StringVar(),
            'date_fin': tk.StringVar(),
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
            tk.Label(search_frame, text=label).grid(row=row, column=0, sticky="e", padx=5, pady=3)
            tk.Entry(search_frame, textvariable=self.vars[key], width=30).grid(row=row, column=1, sticky="w", padx=5)
            row += 1

        tk.Button(search_frame, text="Rechercher", command=self.rechercher).grid(row=row, column=0, columnspan=2, pady=10)

        # Résultats
        self.tree = ttk.Treeview(self.window, columns=("submission_number", "client_name", "contact", "projet", "ville", "etat", "date_submission"), show="headings")
        for col, label in zip(self.tree["columns"], [
            "Soumission", "Client", "Contact", "Projet", "Ville", "État", "Date"]):
            self.tree.heading(col, text=label)
            self.tree.column(col, width=120)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", self.ouvrir_soumission)

        bouton_supprimer = tk.Button(self.window, text="Supprimer la soumission sélectionnée", command=self.supprimer_soumission)
        bouton_supprimer.pack(pady=(0, 10))


    def supprimer_soumission(self):
        item = self.tree.focus()
        if not item:
            messagebox.showwarning("Attention", "Veuillez sélectionner une soumission à supprimer.")
            return

        submission_number = self.tree.item(item)["values"][0]
        
        message = (
            f"⚠️ Cette action est irréversible.\n\n"
            f"Voulez-vous VRAIMENT supprimer définitivement la soumission :\n\n"
            f"{submission_number} ?"
        )
        
        confirmation = messagebox.askyesno("Confirmation de suppression", message)

        if confirmation:
            try:
                self.db_manager.supprimer_soumission(submission_number)
                messagebox.showinfo("Succès", f"La soumission {submission_number} a été supprimée définitivement.")
                self.rechercher()  # rafraîchir la liste
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression : {e}")



    def rechercher(self):
        criteres = {k: v.get().strip() for k, v in self.vars.items() if v.get().strip() != ""}
        try:
            resultats = self.db_manager.search_submissions(criteres)
            self.tree.delete(*self.tree.get_children())
            for row in resultats:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la recherche : {e}")

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
                messagebox.showerror("Erreur", "Soumission introuvable")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ouverture : {e}")
