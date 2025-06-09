import tkinter as tk
from tkinter import ttk, messagebox

class ParamManager:
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.window = tk.Toplevel(parent)
        self.window.title("Gestion des Paramètres - Sable")
        self.window.geometry("800x600")

        main_frame = ttk.Frame(self.window)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Formulaire
        form_frame = ttk.LabelFrame(main_frame, text="Ajouter/Modifier Sable", padding=10)
        form_frame.pack(fill="x", pady=5)

        fields = [
            ("Transporteur", tk.StringVar()),
            ("Type de camion (tm)", tk.IntVar(value=10)),
            ("Ville", tk.StringVar()),
            ("Prix transport seul. par voyage ($)", tk.DoubleVar(value=200.0)),
            ("Prix du sable par tm ($/tm)", tk.DoubleVar(value=50.0))
        ]
        self.sable_entries = {}
        for i, (label, var) in enumerate(fields):
            tk.Label(form_frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            if isinstance(var, tk.IntVar):
                entry = tk.Entry(form_frame, textvariable=tk.StringVar(value=str(var.get())), width=30)
                entry.configure(validate='key', validatecommand=(form_frame.register(lambda p: p.isdigit() or not p), '%P'))
            elif isinstance(var, tk.DoubleVar):
                entry = tk.Entry(form_frame, textvariable=tk.StringVar(value=str(var.get())), width=30)
                entry.configure(validate='key', validatecommand=(form_frame.register(lambda p: p.replace('.', '', 1).isdigit() or not p), '%P'))
            else:
                entry = tk.Entry(form_frame, textvariable=var, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.sable_entries[label] = var if not isinstance(var, (tk.IntVar, tk.DoubleVar)) else entry

        tk.Button(form_frame, text="Enregistrer", command=self.save_sable).grid(row=len(fields), column=0, columnspan=2, pady=10)
        tk.Button(form_frame, text="Effacer", command=lambda: self.clear_sable_form()).grid(row=len(fields)+1, column=0, columnspan=2, pady=5)

        # Liste
        list_frame = ttk.LabelFrame(main_frame, text="Liste des Sables", padding=10)
        list_frame.pack(fill="both", expand=True, pady=5)
        self.sable_tree = ttk.Treeview(list_frame, columns=("ID", "Transporteur", "Type de camion (tm)", "Ville", "Prix transport seul. par voyage ($)", "Prix du sable par tm ($/tm)"), show="headings")
        self.sable_tree.heading("ID", text="ID")
        self.sable_tree.heading("Transporteur", text="Transporteur")
        self.sable_tree.heading("Type de camion (tm)", text="Type de camion (tm)")
        self.sable_tree.heading("Ville", text="Ville")
        self.sable_tree.heading("Prix transport seul. par voyage ($)", text="Prix transport seul. par voyage ($)")
        self.sable_tree.heading("Prix du sable par tm ($/tm)", text="Prix du sable par tm ($/tm)")
        self.sable_tree.column("ID", width=50)
        self.sable_tree.column("Transporteur", width=150)
        self.sable_tree.column("Type de camion (tm)", width=120)
        self.sable_tree.column("Ville", width=120)
        self.sable_tree.column("Prix transport seul. par voyage ($)", width=150)
        self.sable_tree.column("Prix du sable par tm ($/tm)", width=150)
        self.sable_tree.pack(fill="both", expand=True)
        self.sable_tree.bind("<Double-1>", self.edit_sable)

        tk.Button(list_frame, text="Supprimer", command=self.delete_sable).pack(pady=5)

        self.load_sable()

    def load_sable(self):
        for item in self.sable_tree.get_children():
            self.sable_tree.delete(item)
        sable_list = self.db_manager.get_sable()
        for sable in sable_list:
            self.sable_tree.insert("", "end", values=sable)

    def clear_sable_form(self):
        for label, var in self.sable_entries.items():
            if isinstance(var, tk.Entry):
                var.delete(0, tk.END)
            elif isinstance(var, tk.StringVar):
                var.set("")
            elif isinstance(var, tk.IntVar):
                var.set(10)
            elif isinstance(var, tk.DoubleVar):
                var.set(200.0 if label == "Prix transport seul. par voyage ($)" else 50.0)

    def save_sable(self):
        try:
            transporteur = self.sable_entries["Transporteur"].get() if isinstance(self.sable_entries["Transporteur"], tk.StringVar) else self.sable_entries["Transporteur"].get().strip()
            camion = int(self.sable_entries["Type de camion (tm)"].get() if isinstance(self.sable_entries["Type de camion (tm)"], tk.Entry) else self.sable_entries["Type de camion (tm)"].get())
            ville = self.sable_entries["Ville"].get() if isinstance(self.sable_entries["Ville"], tk.StringVar) else self.sable_entries["Ville"].get().strip()
            prix_voyage = float(self.sable_entries["Prix transport seul. par voyage ($)"].get() if isinstance(self.sable_entries["Prix transport seul. par voyage ($)"], tk.Entry) else self.sable_entries["Prix transport seul. par voyage ($)"].get())
            prix_sable = float(self.sable_entries["Prix du sable par tm ($/tm)"].get() if isinstance(self.sable_entries["Prix du sable par tm ($/tm)"], tk.Entry) else self.sable_entries["Prix du sable par tm ($/tm)"].get())
            if not transporteur or not ville or prix_voyage <= 0 or prix_sable <= 0:
                raise ValueError("Tous les champs sont requis et les prix doivent être positifs")

            selected = self.sable_tree.selection()
            if selected:
                sable_id = self.sable_tree.item(selected[0])["values"][0]
                self.db_manager.update_sable(sable_id, transporteur, camion, ville, prix_voyage, prix_sable)
                messagebox.showinfo("Succès", "Sable modifié")
            else:
                self.db_manager.add_sable(transporteur, camion, ville, prix_voyage, prix_sable)
                messagebox.showinfo("Succès", "Sable ajouté")
            self.load_sable()
            self.clear_sable_form()
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur d'enregistrement : {e}")

    def edit_sable(self, event=None):
        selected = self.sable_tree.selection()
        if not selected:
            return
        sable_data = self.sable_tree.item(selected[0])["values"]
        self.sable_entries["Transporteur"].set(sable_data[1]) if isinstance(self.sable_entries["Transporteur"], tk.StringVar) else self.sable_entries["Transporteur"].delete(0, tk.END).insert(0, sable_data[1])
        self.sable_entries["Type de camion (tm)"].set(str(sable_data[2])) if isinstance(self.sable_entries["Type de camion (tm)"], tk.Entry) else self.sable_entries["Type de camion (tm)"].set(sable_data[2])
        self.sable_entries["Ville"].set(sable_data[3]) if isinstance(self.sable_entries["Ville"], tk.StringVar) else self.sable_entries["Ville"].delete(0, tk.END).insert(0, sable_data[3])
        self.sable_entries["Prix transport seul. par voyage ($)"].set(str(sable_data[4])) if isinstance(self.sable_entries["Prix transport seul. par voyage ($)"], tk.Entry) else self.sable_entries["Prix transport seul. par voyage ($)"].set(sable_data[4])
        self.sable_entries["Prix du sable par tm ($/tm)"].set(str(sable_data[5])) if isinstance(self.sable_entries["Prix du sable par tm ($/tm)"], tk.Entry) else self.sable_entries["Prix du sable par tm ($/tm)"].set(sable_data[5])

    def delete_sable(self):
        selected = self.sable_tree.selection()
        if not selected:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner une entrée")
            return
        sable_id = self.sable_tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirmation", "Voulez-vous supprimer cette entrée ?"):
            try:
                self.db_manager.delete_sable(sable_id)
                self.load_sable()
                self.clear_sable_form()
                messagebox.showinfo("Succès", "Entrée supprimée")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur de suppression : {e}")





class MainDoeuvreForm:
    def __init__(self, parent, db_manager, main_doeuvre_data=None):
        self.db_manager = db_manager
        self.main_doeuvre_data = main_doeuvre_data
        self.window = tk.Toplevel(parent)
        self.window.title("Ajouter Main d'œuvre" if main_doeuvre_data is None else "Modifier Main d'œuvre")
        self.window.geometry("400x250")
        self.window.transient(parent)
        self.window.grab_set()

        frame = ttk.LabelFrame(self.window, text="Informations Main d'œuvre", padding=10)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        fields = [
            ("Métier", tk.StringVar()),
            ("Taux horaire chantier (CAD)", tk.DoubleVar()),
            ("Taux horaire transport (CAD)", tk.DoubleVar())
        ]
        self.entries = {}
        for i, (label, var) in enumerate(fields):
            tk.Label(frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = tk.Entry(frame, textvariable=var, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries[label] = var

        if main_doeuvre_data:
            self.entries["Métier"].set(main_doeuvre_data[1])
            self.entries["Taux horaire chantier (CAD)"].set(main_doeuvre_data[2])
            self.entries["Taux horaire transport (CAD)"].set(main_doeuvre_data[3])

        tk.Button(frame, text="Enregistrer", command=self.save_main_doeuvre).grid(row=len(fields), column=0, columnspan=2, pady=10)
        tk.Button(frame, text="Annuler", command=self.window.destroy).grid(row=len(fields)+1, column=0, columnspan=2, pady=5)

    def save_main_doeuvre(self):
        try:
            metier = self.entries["Métier"].get().strip()
            if not metier:
                raise ValueError("Le métier est requis")
            taux_chantier = self.entries["Taux horaire chantier (CAD)"].get()
            if taux_chantier <= 0:
                raise ValueError("Le taux horaire chantier doit être positif")
            taux_transport = self.entries["Taux horaire transport (CAD)"].get()
            if taux_transport <= 0:
                raise ValueError("Le taux horaire transport doit être positif")

            if self.main_doeuvre_data:
                self.db_manager.update_main_doeuvre(self.main_doeuvre_data[0], metier, taux_chantier, taux_transport)
                messagebox.showinfo("Succès", "Main d'œuvre modifiée")
            else:
                self.db_manager.add_main_doeuvre(metier, taux_chantier, taux_transport)
                messagebox.showinfo("Succès", "Main d'œuvre ajoutée")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur d'enregistrement : {e}")

class MainDoeuvreWindow:
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.window = tk.Toplevel(parent)
        self.window.title("Gestion Main d'œuvre")
        self.window.geometry("800x600")
        self.window.transient(parent)
        self.window.grab_set()

        main_frame = ttk.Frame(self.window)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        main_doeuvre_frame = ttk.LabelFrame(main_frame, text="Main d'œuvre", padding=10)
        main_doeuvre_frame.pack(fill="both", expand=True, pady=5)

        self.main_doeuvre_tree = ttk.Treeview(main_doeuvre_frame, columns=("ID", "Métier", "Taux Chantier", "Taux Transport"), show="headings")
        self.main_doeuvre_tree.heading("ID", text="ID")
        self.main_doeuvre_tree.heading("Métier", text="Métier")
        self.main_doeuvre_tree.heading("Taux Chantier", text="Taux Horaire Chantier (CAD)")
        self.main_doeuvre_tree.heading("Taux Transport", text="Taux Horaire Transport (CAD)")
        self.main_doeuvre_tree.column("ID", width=50)
        self.main_doeuvre_tree.column("Métier", width=200)
        self.main_doeuvre_tree.column("Taux Chantier", width=150)
        self.main_doeuvre_tree.column("Taux Transport", width=150)
        self.main_doeuvre_tree.pack(fill="both", expand=True)

        action_frame = ttk.Frame(main_doeuvre_frame)
        action_frame.pack(fill="x", pady=5)
        tk.Button(action_frame, text="Ajouter", command=self.add_main_doeuvre).pack(side="left", padx=5)
        tk.Button(action_frame, text="Modifier", command=self.edit_main_doeuvre).pack(side="left", padx=5)
        tk.Button(action_frame, text="Supprimer", command=self.delete_main_doeuvre).pack(side="left", padx=5)

        self.load_main_doeuvre()

    def load_main_doeuvre(self):
        for item in self.main_doeuvre_tree.get_children():
            self.main_doeuvre_tree.delete(item)
        main_doeuvre = self.db_manager.get_main_doeuvre()
        for entry in main_doeuvre:
            self.main_doeuvre_tree.insert("", "end", values=entry)

    def add_main_doeuvre(self):
        form = MainDoeuvreForm(self.window, self.db_manager)
        self.window.wait_window(form.window)
        self.load_main_doeuvre()

    def edit_main_doeuvre(self):
        selected = self.main_doeuvre_tree.selection()
        if not selected:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner une entrée")
            return
        main_doeuvre_data = self.main_doeuvre_tree.item(selected[0])["values"]
        form = MainDoeuvreForm(self.window, self.db_manager, main_doeuvre_data)
        self.window.wait_window(form.window)
        self.load_main_doeuvre()

    def delete_main_doeuvre(self):
        selected = self.main_doeuvre_tree.selection()
        if not selected:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner une entrée")
            return
        main_doeuvre_id = self.main_doeuvre_tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirmation", "Voulez-vous supprimer cette entrée ?"):
            try:
                self.db_manager.delete_main_doeuvre(main_doeuvre_id)
                self.load_main_doeuvre()
                messagebox.showinfo("Succès", "Entrée supprimée")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur de suppression : {e}")

class ProduitsBetonForm:
    def __init__(self, parent, db_manager, produit_data=None):
        self.db_manager = db_manager
        self.produit_data = produit_data
        self.window = tk.Toplevel(parent)
        self.window.title("Ajouter Produit de béton" if produit_data is None else "Modifier Produit de béton")
        self.window.geometry("600x700")
        self.window.transient(parent)
        self.window.grab_set()

        frame = ttk.LabelFrame(self.window, text="Informations Produit", padding=10)
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Champs de base
        fields = [
            ("Nom", tk.StringVar()),
            ("Prix de base ($/sac)", tk.DoubleVar()),
            ("Devise (base)", tk.StringVar(value="CAD")),
            ("Prix du transport ($/sac)", tk.DoubleVar()),
            ("Devise (transport)", tk.StringVar(value="CAD")),
            ("Type de produit", tk.StringVar(value="RATIO")),
            ("Couverture (pi²/po d'épaisseur)", tk.DoubleVar(value=0.0))
        ]
        self.entries = {}
        for i, (label, var) in enumerate(fields):
            tk.Label(frame, text=label).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            if label.startswith("Devise"):
                widget = ttk.Combobox(frame, textvariable=var, values=["USD", "CAD"], state="readonly", width=27)
            elif label == "Type de produit":
                widget = ttk.Combobox(frame, textvariable=var, values=["RATIO", "COUVERTURE"], state="readonly", width=27)
                widget.bind("<<ComboboxSelected>>", self.toggle_ratio_frame)
            else:
                widget = tk.Entry(frame, textvariable=var, width=30)
            widget.grid(row=i, column=1, padx=5, pady=5)
            self.entries[label] = var

        # Instruction pour les nombres décimaux
        tk.Label(frame, text="Utilisez un point (.) pour les nombres décimaux (ex. 1.5)", font=("Arial", 8, "italic")).grid(row=len(fields), column=0, columnspan=2, pady=2)

        # Frame pour les ratios
        self.ratio_frame = ttk.LabelFrame(frame, text="Ratios (pour type Ratio)", padding=10)
        self.ratio_frame.grid(row=len(fields)+1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.ratio_entries = []
        self.default_var = tk.IntVar(value=-1)
        tk.Button(self.ratio_frame, text="Ajouter un ratio", command=self.add_ratio_entry).grid(row=0, column=0, columnspan=2, pady=5)

        # Boutons d'action
        tk.Button(frame, text="Enregistrer", command=self.save_produit).grid(row=len(fields)+2, column=0, columnspan=2, pady=10)
        tk.Button(frame, text="Annuler", command=self.window.destroy).grid(row=len(fields)+3, column=0, columnspan=2, pady=5)

        # Charger les données existantes
        if produit_data:
            self.entries["Nom"].set(produit_data[0])
            self.entries["Prix de base ($/sac)"].set(produit_data[1])
            self.entries["Devise (base)"].set(produit_data[2])
            self.entries["Prix du transport ($/sac)"].set(produit_data[3])
            self.entries["Devise (transport)"].set(produit_data[4])
            self.entries["Type de produit"].set(produit_data[5])
            self.entries["Couverture (pi²/po d'épaisseur)"].set(produit_data[6] or 0.0)
            if produit_data[5] == "RATIO":
                ratios = self.db_manager.get_produit_ratios(produit_data[0])
                for i, (ratio_id, ratio, est_defaut) in enumerate(ratios):
                    self.add_ratio_entry(ratio, est_defaut)
            else:
                self.ratio_frame.grid_remove()

    def add_ratio_entry(self, ratio_value=None, est_defaut=False):
        row = len(self.ratio_entries) + 1
        ratio_var = tk.StringVar(value=str(ratio_value) if ratio_value is not None else "")
        radio_var = tk.IntVar(value=len(self.ratio_entries) if est_defaut else -1)
        if est_defaut:
            self.default_var.set(len(self.ratio_entries))
        
        tk.Label(self.ratio_frame, text=f"Ratio {row}").grid(row=row, column=0, padx=5, pady=2, sticky="w")
        tk.Entry(self.ratio_frame, textvariable=ratio_var, width=10).grid(row=row, column=1, padx=5, pady=2)
        tk.Radiobutton(self.ratio_frame, text="Par défaut", variable=self.default_var, value=len(self.ratio_entries)).grid(row=row, column=2, padx=5, pady=2)
        
        self.ratio_entries.append((ratio_var, radio_var))
        self.window.geometry(f"600x{700 + len(self.ratio_entries) * 30}")

    def toggle_ratio_frame(self, event=None):
        if self.entries["Type de produit"].get() == "RATIO":
            self.ratio_frame.grid()
            if not self.ratio_entries:
                self.add_ratio_entry()
        else:
            self.ratio_frame.grid_remove()
            self.ratio_entries.clear()
            self.default_var.set(-1)

    def parse_float(self, value):
        """Convertit une chaîne en float, gérant les virgules et les valeurs vides."""
        if not value.strip():
            return None
        try:
            return float(value.replace(",", "."))
        except ValueError:
            raise ValueError("Format numérique invalide (utilisez un point, ex. 1.5)")

    def save_produit(self):
        try:
            nom = self.entries["Nom"].get().strip()
            if not nom:
                raise ValueError("Le nom est requis")
            
            prix_base = self.entries["Prix de base ($/sac)"].get()
            if prix_base <= 0:
                raise ValueError("Le prix de base doit être positif")
            
            devise_base = self.entries["Devise (base)"].get()
            
            prix_transport = self.entries["Prix du transport ($/sac)"].get()
            if prix_transport <= 0:
                raise ValueError("Le prix du transport doit être positif")
            
            devise_transport = self.entries["Devise (transport)"].get()
            
            type_produit = self.entries["Type de produit"].get()
            
            couverture = self.entries["Couverture (pi²/po d'épaisseur)"].get()
            if type_produit == "COUVERTURE" and couverture <= 0:
                raise ValueError("La couverture doit être positive pour un produit de type Couverture")
            couverture = couverture or 0.0  # Définit à 0.0 si vide pour type Ratio

            ratios = []
            if type_produit == "RATIO":
                valid_ratios = []
                for i, (ratio_var, _) in enumerate(self.ratio_entries):
                    ratio = self.parse_float(ratio_var.get())
                    if ratio is not None and ratio > 0:
                        valid_ratios.append((ratio, i == self.default_var.get()))
                if not valid_ratios:
                    raise ValueError("Au moins un ratio positif est requis pour un produit de type Ratio")
                if not any(is_default for _, is_default in valid_ratios):
                    raise ValueError("Un ratio par défaut doit être sélectionné")
                ratios = valid_ratios

            if self.produit_data:  # Modification
                self.db_manager.update_produit(
                    self.produit_data[0], nom, prix_base, devise_base, prix_transport, devise_transport, type_produit, couverture, ratios
                )
                messagebox.showinfo("Succès", "Produit modifié")
            else:  # Ajout
                self.db_manager.add_produit(
                    nom, prix_base, devise_base, prix_transport, devise_transport, type_produit, couverture, ratios
                )
                messagebox.showinfo("Succès", "Produit ajouté")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur d'enregistrement : {e}")

class ProduitsBetonWindow:
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.window = tk.Toplevel(parent)
        self.window.title("Gestion Produits de béton")
        self.window.geometry("800x600")
        self.window.transient(parent)
        self.window.grab_set()

        main_frame = ttk.Frame(self.window)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        produits_frame = ttk.LabelFrame(main_frame, text="Produits de béton", padding=10)
        produits_frame.pack(fill="both", expand=True, pady=5)

        self.produit_tree = ttk.Treeview(produits_frame, columns=("Nom", "Prix Base", "Devise Base", "Prix Transport", "Devise Transport", "Type", "Couverture"), show="headings")
        self.produit_tree.heading("Nom", text="Nom")
        self.produit_tree.heading("Prix Base", text="Prix Base ($/sac)")
        self.produit_tree.heading("Devise Base", text="Devise Base")
        self.produit_tree.heading("Prix Transport", text="Prix Transport ($/sac)")
        self.produit_tree.heading("Devise Transport", text="Devise Transport")
        self.produit_tree.heading("Type", text="Type")
        self.produit_tree.heading("Couverture", text="Couverture (pi²/po)")
        self.produit_tree.column("Nom", width=150)
        self.produit_tree.column("Prix Base", width=100)
        self.produit_tree.column("Devise Base", width=80)
        self.produit_tree.column("Prix Transport", width=100)
        self.produit_tree.column("Devise Transport", width=80)
        self.produit_tree.column("Type", width=100)
        self.produit_tree.column("Couverture", width=100)
        self.produit_tree.pack(fill="both", expand=True)

        action_frame = ttk.Frame(produits_frame)
        action_frame.pack(fill="x", pady=5)
        tk.Button(action_frame, text="Ajouter", command=self.add_produit).pack(side="left", padx=5)
        tk.Button(action_frame, text="Modifier", command=self.edit_produit).pack(side="left", padx=5)
        tk.Button(action_frame, text="Supprimer", command=self.delete_produit).pack(side="left", padx=5)

        self.load_produits()

    def load_produits(self):
        for item in self.produit_tree.get_children():
            self.produit_tree.delete(item)
        produits = self.db_manager.get_produit_details()
        for produit in produits:
            self.produit_tree.insert("", "end", values=produit)

    def add_produit(self):
        form = ProduitsBetonForm(self.window, self.db_manager)
        self.window.wait_window(form.window)
        self.load_produits()

    def edit_produit(self):
        selected = self.produit_tree.selection()
        if not selected:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un produit")
            return
        produit_data = self.produit_tree.item(selected[0])["values"]
        form = ProduitsBetonForm(self.window, self.db_manager, produit_data)
        self.window.wait_window(form.window)
        self.load_produits()

    def delete_produit(self):
        selected = self.produit_tree.selection()
        if not selected:
            messagebox.showwarning("Avertissement", "Veuillez sélectionner un produit")
            return
        produit_nom = self.produit_tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirmation", "Voulez-vous supprimer ce produit ?"):
            try:
                self.db_manager.delete_produit(produit_nom)
                self.load_produits()
                messagebox.showinfo("Succès", "Produit supprimé")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur de suppression : {e}")

class ParametersWindow:
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.window = tk.Toplevel(parent)
        self.window.title("Gestion des paramètres")
        self.window.geometry("400x400")
        self.window.transient(parent)
        self.window.grab_set()

        main_frame = ttk.Frame(self.window)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        categories_frame = ttk.LabelFrame(main_frame, text="Sélectionner une catégorie", padding=10)
        categories_frame.pack(fill="both", expand=True)

        categories = [
            ("Produits de béton", self.open_produits_beton),
            ("Sable et transporteurs", self.open_sable_transporteurs),
            ("Membranes", self.open_membranes),
            ("Scellant et apprêts", self.open_scellant_apprets),
            ("Main d'œuvre", self.open_main_doeuvre),
            ("Machinerie", self.open_machinerie),
            ("Pensions", self.open_pensions)
        ]

        for i, (label, command) in enumerate(categories):
            tk.Button(categories_frame, text=label, command=command).pack(fill="x", pady=5)

    def open_produits_beton(self):
        ProduitsBetonWindow(self.window, self.db_manager)

    def open_sable_transporteurs(self):
        messagebox.showinfo("Info", "Gestion des Sable et transporteurs non implémentée. Fournissez les champs nécessaires.")

    def open_membranes(self):
        messagebox.showinfo("Info", "Gestion des Membranes non implémentée. Fournissez les champs nécessaires.")

    def open_scellant_apprets(self):
        messagebox.showinfo("Info", "Gestion des Scellant et apprêts non implémentée. Fournissez les champs nécessaires.")

    def open_main_doeuvre(self):
        MainDoeuvreWindow(self.window, self.db_manager)

    def open_machinerie(self):
        messagebox.showinfo("Info", "Gestion des Machinerie non implémentée. Fournissez les champs nécessaires.")

    def open_pensions(self):
        messagebox.showinfo("Info", "Gestion des Pensions non implémentée. Fournissez les champs nécessaires.")
