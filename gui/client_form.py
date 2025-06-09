# gui/client_form.py
import tkinter as tk
from tkinter import ttk, messagebox

class ClientForm:
    def __init__(self, parent, db_manager, client_data=None):
        self.db_manager = db_manager
        self.client_data = client_data  # None pour ajout, tuple (id, nom, courriel, telephone, adresse) pour modification
        self.window = tk.Toplevel(parent)
        self.window.title("Ajouter Client" if client_data is None else "Modifier Client")
        self.window.geometry("500x350")

        frame = ttk.LabelFrame(self.window, text="Informations Client", padding=10)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Champs
        fields = [
            ("Nom", tk.StringVar()),
            ("Courriel", tk.StringVar()),
            ("Téléphone", tk.StringVar()),
            ("Adresse", tk.StringVar())
        ]
        self.entries = {}
        for i, (label, var) in enumerate(fields):
            tk.Label(frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = tk.Entry(frame, textvariable=var, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[label] = var

        # Pré-remplir si modification
        if client_data:
            self.entries["Nom"].set(client_data[1])
            self.entries["Courriel"].set(client_data[2] or "")
            self.entries["Téléphone"].set(client_data[3] or "")
            self.entries["Adresse"].set(client_data[4] or "")

        # Boutons
        tk.Button(frame, text="Enregistrer", command=self.save_client).grid(row=len(fields), column=0, columnspan=2, pady=10)
        tk.Button(frame, text="Annuler", command=self.window.destroy).grid(row=len(fields)+1, column=0, columnspan=2, pady=5)

    def save_client(self):
        try:
            nom = self.entries["Nom"].get().strip()
            if not nom:
                raise ValueError("Le nom est requis")
            courriel = self.entries["Courriel"].get().strip()
            telephone = self.entries["Téléphone"].get().strip()
            adresse = self.entries["Adresse"].get().strip()

            if self.client_data:  # Modification
                self.db_manager.update_client(self.client_data[0], nom, courriel, telephone, adresse)
                messagebox.showinfo("Succès", "Client modifié")
            else:  # Ajout
                self.db_manager.add_client(nom, courriel, telephone, adresse)
                messagebox.showinfo("Succès", "Client ajouté")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur d'enregistrement : {e}")