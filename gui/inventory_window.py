import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date, timedelta
import logging

class InventoryWindow:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db_manager = db_manager
        self.window = tk.Toplevel(parent)
        self.window.title("Gestion de l'inventaire")
        self.window.geometry("1200x800")

        # Frame principal
        main_frame = ttk.Frame(self.window)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Notebook pour les onglets
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, pady=5)

        # Onglet Produits de béton
        self.beton_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.beton_frame, text="Produits de béton")
        self.setup_inventory_tab(self.beton_frame, "Produit de béton")

        # Onglet Membranes
        self.membrane_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.membrane_frame, text="Membranes")
        self.setup_inventory_tab(self.membrane_frame, "Membrane")

        # Bouton Actualiser
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill="x", pady=5)
        ttk.Button(action_frame, text="Actualiser", command=self.load_inventory).pack(side="left", padx=5)

        # Charger les données initiales
        self.load_inventory()

    def setup_inventory_tab(self, frame, categorie):
        """Configure un onglet pour une catégorie donnée avec formulaire, filtres et tableau."""
        # Frame pour le formulaire
        add_frame = ttk.LabelFrame(frame, text=f"Ajouter/Modifier une entrée ({categorie})", padding=10)
        add_frame.pack(fill="x", pady=5)

        # Formulaire
        ttk.Label(add_frame, text="Nom du produit :" if categorie == "Produit de béton" else "Nom de la membrane :").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        produit_var = tk.StringVar()
        if categorie == "Produit de béton":
            values = self.db_manager.get_produits()
            self.produit_beton_var = produit_var
        else:
            values = [row[1] for row in self.db_manager.get_membranes()]
            self.produit_membrane_var = produit_var
        ttk.Combobox(add_frame, textvariable=produit_var, values=values, state="readonly").grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Quantité commandée :").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        quantite_var = tk.StringVar()
        if categorie == "Produit de béton":
            self.quantite_beton_var = quantite_var
        else:
            self.quantite_membrane_var = quantite_var
        ttk.Entry(add_frame, textvariable=quantite_var).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(add_frame, text="Numéro P.O. ou descriptif :").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        po_var = tk.StringVar()
        if categorie == "Produit de béton":
            self.po_beton_var = po_var
        else:
            self.po_membrane_var = po_var
        ttk.Entry(add_frame, textvariable=po_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Date du P.O. (YYYY-MM-DD) :").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        date_po_var = tk.StringVar()
        if categorie == "Produit de béton":
            self.date_po_beton_var = date_po_var
        else:
            self.date_po_membrane_var = date_po_var
        ttk.Entry(add_frame, textvariable=date_po_var).grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(add_frame, text="Date de livraison prévue (YYYY-MM-DD) :").grid(row=1, column=4, padx=5, pady=5, sticky="e")
        date_arrivee_var = tk.StringVar()
        if categorie == "Produit de béton":
            self.date_arrivee_beton_var = date_arrivee_var
        else:
            self.date_arrivee_membrane_var = date_arrivee_var
        ttk.Entry(add_frame, textvariable=date_arrivee_var).grid(row=1, column=5, padx=5, pady=5)

        ttk.Label(add_frame, text="Approximatif :").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        approximatif_var = tk.BooleanVar()
        if categorie == "Produit de béton":
            self.approximatif_beton_var = approximatif_var
        else:
            self.approximatif_membrane_var = approximatif_var
        ttk.Checkbutton(add_frame, variable=approximatif_var).grid(row=2, column=1, padx=5, pady=5)

        # Boutons d'action
        button_frame = ttk.Frame(add_frame)
        button_frame.grid(row=3, column=0, columnspan=6, pady=10)
        ttk.Button(button_frame, text="Ajouter", command=lambda: self.add_entry(categorie)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Modifier", command=lambda: self.update_entry(categorie)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Supprimer", command=lambda: self.delete_entry(categorie)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Effacer formulaire", command=lambda: self.clear_form(categorie)).pack(side="left", padx=5)

        # Frame pour les filtres
        filter_frame = ttk.LabelFrame(frame, text="Filtres", padding=10)
        filter_frame.pack(fill="x", pady=5)

        ttk.Label(filter_frame, text="Produit :").pack(side="left", padx=5)
        filter_produit_var = tk.StringVar()
        filter_produit_values = ["Tous"] + values
        ttk.Combobox(filter_frame, textvariable=filter_produit_var, values=filter_produit_values, state="readonly").pack(side="left", padx=5)
        
        ttk.Label(filter_frame, text="Date début (YYYY-MM-DD) :").pack(side="left", padx=5)
        filter_date_start_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=filter_date_start_var, width=12).pack(side="left", padx=5)

        ttk.Label(filter_frame, text="Date fin (YYYY-MM-DD) :").pack(side="left", padx=5)
        filter_date_end_var = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=filter_date_end_var, width=12).pack(side="left", padx=5)

        ttk.Button(filter_frame, text="Appliquer filtres", command=lambda: self.load_inventory(
            filter_categorie=categorie,
            filter_produit=filter_produit_var.get() if filter_produit_var.get() != "Tous" else None,
            filter_date_start=filter_date_start_var.get().strip() or None,
            filter_date_end=filter_date_end_var.get().strip() or None
        )).pack(side="left", padx=5)

        # Frame pour le tableau
        list_frame = ttk.LabelFrame(frame, text=f"Inventaire ({categorie})", padding=10)
        list_frame.pack(fill="both", expand=True, pady=5)

        # Treeview pour afficher les données
        columns = ("Date", "Client", "Produit", "Quantité", "Approximatif", "Total courant")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col, anchor="w")
        tree.column("Date", width=100, anchor="w")
        tree.column("Client", width=200, anchor="w")
        tree.column("Produit", width=200, anchor="w")
        tree.column("Quantité", width=150, anchor="w")
        tree.column("Approximatif", width=100, anchor="w")
        tree.column("Total courant", width=150, anchor="w")
        tree.pack(fill="both", expand=True)

        # Configurer les tags pour le surlignage
        tree.tag_configure("highlight", background="yellow")
        tree.tag_configure("today", background="lightgreen")

        # Associer un clic sur une ligne à la fonction de sélection
        tree.bind("<<TreeviewSelect>>", lambda e: self.select_inventory_entry(tree, categorie))

        # Frame pour le total à la date du jour
        total_frame = ttk.Frame(list_frame)
        total_frame.pack(fill="x", pady=5)
        ttk.Label(total_frame, text="Total disponible aujourd'hui :").pack(side="left", padx=5)
        total_today_var = tk.StringVar(value="0.00")
        ttk.Label(total_frame, textvariable=total_today_var).pack(side="left", padx=5)

        # Stocker le treeview, le total_today_var et l'ID courant
        if not hasattr(self, 'trees'):
            self.trees = {}
        self.trees[categorie] = {
            'tree': tree,
            'total_today_var': total_today_var,
            'current_id': None
        }

    def select_inventory_entry(self, tree, categorie):
        """Remplit le formulaire avec les données de l'entrée sélectionnée."""
        selected_item = tree.selection()
        if not selected_item:
            return

        item = tree.item(selected_item[0])
        values = item['values']
        tags = item['tags']
        if 'inventory' not in tags:
            messagebox.showinfo("Information", "Les utilisations ne peuvent pas être modifiées.")
            return

        inventory_id = tags[0] if tags else None
        if not inventory_id:
            return

        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, produit_nom, categorie, quantite_commandee, po_number, date_po, date_arrivee, est_approximatif
                FROM inventaire WHERE id = ?
            """, (inventory_id,))
            entry = cursor.fetchone()

        if entry:
            self.trees[categorie]['current_id'] = entry[0]
            if categorie == "Produit de béton":
                self.produit_beton_var.set(entry[1])
                self.quantite_beton_var.set(str(entry[3]))
                self.po_beton_var.set(entry[4] or "")
                self.date_po_beton_var.set(entry[5] or "")
                self.date_arrivee_beton_var.set(entry[6] or "")
                self.approximatif_beton_var.set(bool(entry[7]))
            else:  # Membrane
                self.produit_membrane_var.set(entry[1])
                self.quantite_membrane_var.set(str(entry[3]))
                self.po_membrane_var.set(entry[4] or "")
                self.date_po_membrane_var.set(entry[5] or "")
                self.date_arrivee_membrane_var.set(entry[6] or "")
                self.approximatif_membrane_var.set(bool(entry[7]))

    def clear_form(self, categorie):
        """Efface le formulaire pour la catégorie donnée."""
        self.trees[categorie]['current_id'] = None
        if categorie == "Produit de béton":
            self.produit_beton_var.set("")
            self.quantite_beton_var.set("")
            self.po_beton_var.set("")
            self.date_po_beton_var.set("")
            self.date_arrivee_beton_var.set("")
            self.approximatif_beton_var.set(False)
        else:  # Membrane
            self.produit_membrane_var.set("")
            self.quantite_membrane_var.set("")
            self.po_membrane_var.set("")
            self.date_po_membrane_var.set("")
            self.date_arrivee_membrane_var.set("")
            self.approximatif_membrane_var.set(False)

    def add_entry(self, categorie):
        """Ajoute une nouvelle entrée pour la catégorie donnée."""
        produit_var = self.produit_beton_var if categorie == "Produit de béton" else self.produit_membrane_var
        quantite_var = self.quantite_beton_var if categorie == "Produit de béton" else self.quantite_membrane_var
        po_var = self.po_beton_var if categorie == "Produit de béton" else self.po_membrane_var
        date_po_var = self.date_po_beton_var if categorie == "Produit de béton" else self.date_po_membrane_var
        date_arrivee_var = self.date_arrivee_beton_var if categorie == "Produit de béton" else self.date_arrivee_membrane_var
        approximatif_var = self.approximatif_beton_var if categorie == "Produit de béton" else self.approximatif_membrane_var

        produit_nom = produit_var.get().strip()
        quantite = quantite_var.get().strip()
        po_number = po_var.get().strip() or None
        date_po = date_po_var.get().strip() or None
        date_arrivee = date_arrivee_var.get().strip() or None
        est_approximatif = 1 if approximatif_var.get() else 0

        if not produit_nom or not quantite:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires (Produit, Quantité).")
            return

        try:
            quantite_float = float(quantite)
            if date_po:
                datetime.strptime(date_po, "%Y-%m-%d")
            if date_arrivee:
                datetime.strptime(date_arrivee, "%Y-%m-%d")
        except ValueError as e:
            messagebox.showerror("Erreur", f"Quantité invalide ou format de date incorrect (YYYY-MM-DD) : {e}")
            return

        try:
            self.db_manager.add_inventory(produit_nom, categorie, quantite_float, po_number, date_po, date_arrivee, est_approximatif)
            messagebox.showinfo("Succès", "Entrée d'inventaire ajoutée.")
            self.clear_form(categorie)
            self.load_inventory(highlight_categorie=categorie, highlight_produit=produit_nom, highlight_date=date_arrivee or "1900-01-01")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ajout : {e}")

    def update_entry(self, categorie):
        """Met à jour une entrée pour la catégorie donnée."""
        current_id = self.trees[categorie]['current_id']
        if not current_id:
            messagebox.showerror("Erreur", "Veuillez sélectionner une entrée à modifier.")
            return

        produit_var = self.produit_beton_var if categorie == "Produit de béton" else self.produit_membrane_var
        quantite_var = self.quantite_beton_var if categorie == "Produit de béton" else self.quantite_membrane_var
        po_var = self.po_beton_var if categorie == "Produit de béton" else self.po_membrane_var
        date_po_var = self.date_po_beton_var if categorie == "Produit de béton" else self.date_po_membrane_var
        date_arrivee_var = self.date_arrivee_beton_var if categorie == "Produit de béton" else self.date_arrivee_membrane_var
        approximatif_var = self.approximatif_beton_var if categorie == "Produit de béton" else self.approximatif_membrane_var

        produit_nom = produit_var.get().strip()
        quantite = quantite_var.get().strip()
        po_number = po_var.get().strip() or None
        date_po = date_po_var.get().strip() or None
        date_arrivee = date_arrivee_var.get().strip() or None
        est_approximatif = 1 if approximatif_var.get() else 0

        if not produit_nom or not quantite:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires (Produit, Quantité).")
            return

        try:
            quantite_float = float(quantite)
            if date_po:
                datetime.strptime(date_po, "%Y-%m-%d")
            if date_arrivee:
                datetime.strptime(date_arrivee, "%Y-%m-%d")
        except ValueError as e:
            messagebox.showerror("Erreur", f"Quantité invalide ou format de date incorrect (YYYY-MM-DD) : {e}")
            return

        try:
            self.db_manager.update_inventory(current_id, produit_nom, categorie, quantite_float, po_number, date_po, date_arrivee, est_approximatif)
            messagebox.showinfo("Succès", "Entrée d'inventaire mise à jour.")
            self.clear_form(categorie)
            self.load_inventory()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la mise à jour : {e}")

    def delete_entry(self, categorie):
        """Supprime une entrée pour la catégorie donnée."""
        current_id = self.trees[categorie]['current_id']
        if not current_id:
            messagebox.showerror("Erreur", "Veuillez sélectionner une entrée à supprimer.")
            return

        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cette entrée ?"):
            try:
                self.db_manager.delete_inventory(current_id)
                messagebox.showinfo("Succès", "Entrée d'inventaire supprimée.")
                self.clear_form(categorie)
                self.load_inventory()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression : {e}")

    def load_inventory(self, highlight_categorie=None, highlight_produit=None, highlight_date=None, filter_categorie=None, filter_produit=None, filter_date_start=None, filter_date_end=None):
        """Charge les données de l'inventaire et des utilisations dans les tableaux avec filtres."""
        today = date.today().strftime("%Y-%m-%d")
        today_dt = datetime.strptime(today, "%Y-%m-%d")

        categories = [filter_categorie] if filter_categorie else ["Produit de béton", "Membrane"]
        for categorie in categories:
            tree = self.trees[categorie]['tree']
            total_today_var = self.trees[categorie]['total_today_var']
            tree.delete(*tree.get_children())

            # Récupérer les données de l'inventaire
            inventory_data = self.db_manager.get_inventory(categorie)
            work_sheets = self.db_manager.get_work_sheets_for_inventory(categorie)

            # Combiner les données
            combined_data = []
            for entry in inventory_data:
                id, produit_nom, _, quantite_commandee, po_number, date_po, date_arrivee, est_approximatif = entry
                combined_data.append({
                    'date': date_arrivee or "1900-01-01",
                    'client': po_number or "",
                    'produit': produit_nom,
                    'quantite': quantite_commandee,
                    'est_approximatif': est_approximatif,
                    'source': 'inventory',
                    'id': id
                })

            for entry in work_sheets:
                date_travaux, client_reel, produit, quantite, est_approximatif = entry
                logging.debug(f"Entrée work_sheet: date={date_travaux}, client={client_reel}, produit={produit}, quantite={quantite}")
                try:
                    quantite = -float(quantite)
                except ValueError:
                    continue
                combined_data.append({
                    'date': date_travaux or "1900-01-01",
                    'client': client_reel or "",  # S'assurer que client_reel n'est pas None
                    'produit': produit,
                    'quantite': quantite,
                    'est_approximatif': est_approximatif,
                    'source': 'work_sheet',
                    'id': None
                })

            # Appliquer les filtres
            filtered_data = combined_data
            if filter_produit:
                filtered_data = [entry for entry in filtered_data if entry['produit'] == filter_produit]
            if filter_date_start:
                try:
                    datetime.strptime(filter_date_start, "%Y-%m-%d")
                    filtered_data = [entry for entry in filtered_data if entry['date'] >= filter_date_start]
                except ValueError:
                    messagebox.showerror("Erreur", "Format de date de début invalide (YYYY-MM-DD).")
                    return
            if filter_date_end:
                try:
                    datetime.strptime(filter_date_end, "%Y-%m-%d")
                    filtered_data = [entry for entry in filtered_data if entry['date'] <= filter_date_end]
                except ValueError:
                    messagebox.showerror("Erreur", "Format de date de fin invalide (YYYY-MM-DD).")
                    return

            # Trier par date
            filtered_data.sort(key=lambda x: x['date'])

            # Trouver la date la plus proche antérieure ou égale à aujourd'hui
            closest_date = None
            closest_date_diff = None
            for entry in filtered_data:
                try:
                    entry_date = datetime.strptime(entry['date'], "%Y-%m-%d")
                    if entry_date <= today_dt:
                        diff = today_dt - entry_date
                        if closest_date_diff is None or diff < closest_date_diff:
                            closest_date_diff = diff
                            closest_date = entry['date']
                except (ValueError, TypeError):
                    continue

            # Calculer les totaux courants
            total_courant = 0.0
            total_today = 0.0
            for entry in filtered_data:
                date_entry = entry['date']
                quantite = entry['quantite']
                total_courant += quantite
                try:
                    if date_entry <= today:
                        total_today += quantite
                except TypeError:
                    pass
                # Déterminer les tags
                tags = [entry['id'] if entry['source'] == 'inventory' else "", entry['source']]
                if (categorie == highlight_categorie and 
                    entry['produit'] == highlight_produit and 
                    entry['date'] == highlight_date):
                    tags.append('highlight')
                if date_entry == closest_date:
                    tags.append('today')
                # Insérer dans le Treeview
                tree.insert("", "end", values=(
                    date_entry,
                    entry['client'],
                    entry['produit'],
                    f"{quantite:.2f}",
                    "Oui" if entry['est_approximatif'] else "Non",
                    f"{total_courant:.2f}"
                ), tags=tags)

            # Mettre à jour le total du jour
            total_today_var.set(f"{total_today:.2f}")