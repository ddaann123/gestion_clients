# select_contact_window.py

import tkinter as tk
from tkinter import ttk

class ContactSelector(tk.Toplevel):
    def __init__(self, master, db_manager, on_contact_selected):
        super().__init__(master)
        self.title("Sélection du contact")
        self.db_manager = db_manager
        self.on_contact_selected = on_contact_selected

        self.geometry("600x400")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        tk.Label(self, text="Rechercher (nom ou client) :").pack(pady=5)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(self, textvariable=self.search_var)
        search_entry.pack(fill="x", padx=10)
        search_entry.bind("<KeyRelease>", self.search_contacts)

        self.tree = ttk.Treeview(self, columns=("Nom", "Client", "Téléphone", "Courriel"), show="headings")
        self.tree.heading("Nom", text="Nom")
        self.tree.heading("Client", text="Client")
        self.tree.heading("Téléphone", text="Téléphone")
        self.tree.heading("Courriel", text="Courriel")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree.bind("<Double-1>", self.on_double_click)

        self.contacts = []
        self.populate_all_contacts()

    def populate_all_contacts(self):
        self.contacts = self.db_manager.get_all_contacts_with_clients()
        self.update_treeview(self.contacts)

    def search_contacts(self, event=None):
        search_term = self.search_var.get().lower()
        filtered = [c for c in self.contacts if search_term in c["nom"].lower() or search_term in c["client_name"].lower()]
        self.update_treeview(filtered)

    def update_treeview(self, contacts):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for contact in contacts:
            self.tree.insert("", "end", iid=contact["id"], values=(contact["nom"], contact["client_name"], contact["telephone"], contact["courriel"]))

    def on_double_click(self, event):
        item_id = self.tree.focus()
        contact = next((c for c in self.contacts if c["id"] == int(item_id)), None)
        if contact:
            self.on_contact_selected(contact)
            self.destroy()
