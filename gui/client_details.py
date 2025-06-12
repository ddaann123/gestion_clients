
import tkinter as tk
from tkinter import ttk, messagebox
from gui.submission_form import SubmissionForm


class ContactForm:
    def __init__(self, parent, db_manager, client_id, contact_data=None):
        self.db_manager = db_manager
        self.client_id = client_id
        self.contact_data = contact_data  # None pour ajout, tuple (id, nom, telephone, courriel) pour modification
        self.window = tk.Toplevel(parent)
        self.window.title("Ajouter Contact" if contact_data is None else "Modifier Contact")
        self.window.geometry("400x250")
        self.window.transient(parent)  # Lier à la fenêtre parent
        self.window.grab_set()  # Capturer les interactions

        frame = ttk.LabelFrame(self.window, text="Informations Contact", padding=10)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        fields = [
            ("Nom", tk.StringVar()),
            ("Téléphone", tk.StringVar()),
            ("Courriel", tk.StringVar())
        ]
        self.entries = {}
        for i, (label, var) in enumerate(fields):
            tk.Label(frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = tk.Entry(frame, textvariable=var, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[label] = var

        if contact_data:
            self.entries["Nom"].set(contact_data[1])
            self.entries["Téléphone"].set(contact_data[2] or "")
            self.entries["Courriel"].set(contact_data[3] or "")

        tk.Button(frame, text="Enregistrer", command=self.save_contact).grid(row=len(fields), column=0, columnspan=2, pady=10)
        tk.Button(frame, text="Annuler", command=self.window.destroy).grid(row=len(fields)+1, column=0, columnspan=2, pady=5)

    def save_contact(self):
        try:
            nom = self.entries["Nom"].get().strip()
            if not nom:
                raise ValueError("Le nom est requis")
            telephone = self.entries["Téléphone"].get().strip()
            courriel = self.entries["Courriel"].get().strip()

            if self.contact_data:  # Modification
                self.db_manager.update_contact(self.contact_data[0], nom, telephone, courriel)
                messagebox.showinfo("Succès", "Contact modifié")
            else:  # Ajout
                self.db_manager.add_contact(self.client_id, nom, telephone, courriel)
                messagebox.showinfo("Succès", "Contact ajouté")
            self.window.destroy()  # Ferme uniquement la fenêtre du formulaire
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur d'enregistrement : {e}")


class ClientDetails:
    def __init__(self, parent, db_manager, client_data):
        self.db_manager = db_manager
        self.client_data = client_data  # (id, nom, courriel, telephone, adresse)
        self.selected_contact = None  # Stocker le contact sélectionné
        self.window = tk.Toplevel(parent)
        self.window.title(f"Détails Client - {client_data[1]}")
        self.window.geometry("600x500")

        main_frame = ttk.Frame(self.window)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Informations client
        info_frame = ttk.LabelFrame(main_frame, text="Informations Client", padding=10)
        info_frame.pack(fill="x", pady=5)
        fields = ["Nom", "Courriel", "Téléphone", "Adresse"]
        for i, (field, value) in enumerate(zip(fields, client_data[1:])):
            tk.Label(info_frame, text=f"{field} :").grid(row=i, column=0, padx=5, pady=5, sticky="w")
            tk.Label(info_frame, text=value or "-").grid(row=i, column=1, padx=5, pady=5, sticky="w")

        # Liste des contacts
        contacts_frame = ttk.LabelFrame(main_frame, text="Contacts", padding=10)
        contacts_frame.pack(fill="both", expand=True, pady=5)
        self.contact_tree = ttk.Treeview(contacts_frame, columns=("ID", "Nom", "Téléphone", "Courriel"), show="headings")
        self.contact_tree.heading("ID", text="ID")
        self.contact_tree.heading("Nom", text="Nom")
        self.contact_tree.heading("Téléphone", text="Téléphone")
        self.contact_tree.heading("Courriel", text="Courriel")
        self.contact_tree.column("ID", width=50)
        self.contact_tree.column("Nom", width=200)
        self.contact_tree.column("Téléphone", width=150)
        self.contact_tree.column("Courriel", width=200)
        self.contact_tree.pack(fill="both", expand=True)
        self.contact_tree.bind("<<TreeviewSelect>>", self.select_contact)

        # Boutons contacts
        action_frame = ttk.Frame(contacts_frame)
        action_frame.pack(fill="x", pady=5)
        tk.Button(action_frame, text="Ajouter Contact", command=self.add_contact).pack(side="left", padx=5)
        tk.Button(action_frame, text="Modifier Contact", command=self.edit_contact).pack(side="left", padx=5)
        tk.Button(action_frame, text="Supprimer Contact", command=self.delete_contact).pack(side="left", padx=5)
        tk.Button(action_frame, text="Feuille de calcul", command=self.open_submission_form).pack(side="left", padx=5)

        # Charger les contacts
        self.load_contacts()

    def load_contacts(self):
        """Charge la liste des contacts du client."""
        for item in self.contact_tree.get_children():
            self.contact_tree.delete(item)
        contacts = self.db_manager.get_contacts(self.client_data[0])
        for contact in contacts:
            self.contact_tree.insert("", "end", values=contact)

    def select_contact(self, event):
        """Stocke le contact sélectionné dans le Treeview."""
        selected = self.contact_tree.selection()
        if selected:
            values = self.contact_tree.item(selected[0])["values"]
            self.selected_contact = (values[0], values[1], values[2], values[3])
        else:
            self.selected_contact = None

    def add_contact(self):
        """Ouvre le formulaire pour ajouter un contact."""
        form = ContactForm(self.window, self.db_manager, self.client_data[0])
        self.window.wait_window(form.window)  # Attendre la fermeture du formulaire
        self.load_contacts()  # Rafraîchir la liste

    def edit_contact(self):
        """Ouvre le formulaire pour modifier un contact sélectionné."""
        if not self.selected_contact:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un contact")
            return
        form = ContactForm(self.window, self.db_manager, self.client_data[0], self.selected_contact)
        self.window.wait_window(form.window)  # Attendre la fermeture du formulaire
        self.load_contacts()

    def delete_contact(self):
        """Supprime le contact sélectionné."""
        if not self.selected_contact:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un contact")
            return
        contact_id = self.selected_contact[0]
        if messagebox.askyesno("Confirmation", "Voulez-vous supprimer ce contact ?"):
            try:
                self.db_manager.delete_contact(contact_id)
                self.selected_contact = None
                self.load_contacts()
                messagebox.showinfo("Succès", "Contact supprimé")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur de suppression : {e}")

    def open_submission_form(self):
        # Vérifier si un contact est sélectionné
        if not self.selected_contact:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un contact avant d'ouvrir la soumission")
            return
        
        # Récupérer les données dynamiques
        selected_contact = self.selected_contact[1]  # Nom du contact (index 1 du tuple)
        selected_client = self.client_data[1]       # Nom du client (index 1 de client_data)
        
        # Ouvrir le formulaire de soumission avec les valeurs dynamiques
        SubmissionForm(self.window, self.db_manager, selected_client, selected_contact)