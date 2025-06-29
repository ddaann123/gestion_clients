
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

import tkinter as tk
from tkinter import ttk, messagebox
from gui.client_form import ClientForm
from gui.client_details import ClientDetails
from gui.parameters_window import ParametersWindow
from gui.work_sheets_search_window import WorkSheetsSearchWindow  # Nouveau import

class MainWindow:
    def __init__(self, root, db_manager):
        self.root = root
        self.db_manager = db_manager
        self.root.title("Gestion des clients - PBL")
        self.root.geometry("900x700")

        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Section recherche
        search_frame = ttk.LabelFrame(main_frame, text="Recherche", padding=10)
        search_frame.pack(fill="x", pady=5)
        tk.Label(search_frame, text="Nom :").pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side="left", padx=5)
        tk.Button(search_frame, text="Rechercher", command=self.search_clients).pack(side="left", padx=5)
        tk.Button(search_frame, text="Réinitialiser", command=self.reset_search).pack(side="left", padx=5)
        tk.Button(search_frame, text="Recherche soumission", command=self.open_submission_search).pack(side="left", padx=5)

        # Section liste des clients
        list_frame = ttk.LabelFrame(main_frame, text="Liste des clients", padding=10)
        list_frame.pack(fill="both", expand=True, pady=5)
        self.client_tree = ttk.Treeview(list_frame, columns=("ID", "Nom", "Courriel", "Téléphone", "Adresse"), show="headings")
        self.client_tree.heading("ID", text="ID")
        self.client_tree.heading("Nom", text="Nom")
        self.client_tree.heading("Courriel", text="Courriel")
        self.client_tree.heading("Téléphone", text="Téléphone")
        self.client_tree.heading("Adresse", text="Adresse")
        self.client_tree.column("ID", width=50)
        self.client_tree.column("Nom", width=200)
        self.client_tree.column("Courriel", width=200)
        self.client_tree.column("Téléphone", width=150)
        self.client_tree.column("Adresse", width=200)
        self.client_tree.pack(fill="both", expand=True)
        self.client_tree.bind("<Double-1>", self.open_client_details)

        # Section actions
        action_frame = ttk.LabelFrame(main_frame, text="Actions", padding=10)
        action_frame.pack(fill="x", pady=5)

        # Groupe de gauche
        left_frame = tk.Frame(action_frame)
        left_frame.pack(side="left")

        tk.Button(left_frame, text="Ajouter Client", command=self.open_client_form).pack(side="left", padx=5)
        tk.Button(left_frame, text="Modifier Client", command=self.edit_client).pack(side="left", padx=5)
        tk.Button(left_frame, text="Supprimer Client", command=self.delete_client).pack(side="left", padx=5)
        tk.Button(left_frame, text="Détails Client", command=self.open_client_details).pack(side="left", padx=5)

        # Section gestion
        gestion_frame = ttk.LabelFrame(main_frame, text="Gestion", padding=10)
        gestion_frame.pack(fill="x", pady=5)
        tk.Button(gestion_frame, text="Gestion des paramètres", command=self.open_parameters).pack(side="left", padx=5)
        tk.Button(gestion_frame, text="Gestion des feuilles de travail", command=self.open_work_sheets).pack(side="left", padx=5)

        # Charger la liste initiale
        self.load_clients()

    def open_submission_search(self):
        from gui.submission_search_window import SubmissionSearchWindow
        SubmissionSearchWindow(self.root, self.db_manager)

    def open_work_sheets(self):
        WorkSheetsSearchWindow(self.root, self.db_manager)

    def load_clients(self, clients=None):
        """Charge ou actualise la liste des clients dans le Treeview."""
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)
        if clients is None:
            clients = self.db_manager.get_clients()
        for client in clients:
            self.client_tree.insert("", "end", values=client)

    def search_clients(self):
        """Recherche les clients selon le texte saisi."""
        query = self.search_var.get().strip()
        if query:
            clients = self.db_manager.search_clients(query)
            self.load_clients(clients)
        else:
            self.load_clients()

    def reset_search(self):
        """Réinitialise la recherche."""
        self.search_var.set("")
        self.load_clients()

    def open_client_form(self):
        """Ouvre le formulaire pour ajouter un client."""
        form = ClientForm(self.root, self.db_manager)
        self.root.wait_window(form.window)
        self.load_clients()

    def edit_client(self):
        """Ouvre le formulaire pour modifier un client sélectionné."""
        selected = self.client_tree.selection()
        if not selected:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un client")
            return
        client_data = self.client_tree.item(selected[0])["values"]
        form = ClientForm(self.root, self.db_manager, client_data)
        self.root.wait_window(form.window)
        self.load_clients()

    def delete_client(self):
        """Supprime le client sélectionné."""
        selected = self.client_tree.selection()
        if not selected:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un client")
            return
        client_id = self.client_tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirmation", "Voulez-vous supprimer ce client ?"):
            try:
                self.db_manager.delete_client(client_id)
                self.load_clients()
                messagebox.showinfo("Succès", "Client supprimé")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur de suppression : {e}")

    def open_client_details(self, event=None):
        """Ouvre les détails du client sélectionné."""
        selected = self.client_tree.selection()
        if not selected:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un client")
            return
        client_data = self.client_tree.item(selected[0])["values"]
        ClientDetails(self.root, self.db_manager, client_data)

    def open_parameters(self):
        """Ouvre la fenêtre de gestion des paramètres."""
        ParametersWindow(self.root, self.db_manager)