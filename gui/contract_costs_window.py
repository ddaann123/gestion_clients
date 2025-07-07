import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from datetime import datetime
import logging
import sqlite3
import re

# Configurer le logging
logging.basicConfig(level=logging.DEBUG)

class ContractCostsWindow:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db_manager = db_manager
        self.window = ttkb.Toplevel(parent)
        self.window.title("Sommaire des coûts de contrat")
        self.window.geometry("1000x700")

        # Frame principal
        main_frame = ttkb.Frame(self.window)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Titre principal
        tk.Label(main_frame, text="SOMMAIRE DES COÛTS DE CONTRAT", font=("Arial", 16, "bold")).pack(pady=10)

        # Section recherche
        search_frame = ttkb.LabelFrame(main_frame, text="Recherche", padding=10)
        search_frame.pack(fill="x", pady=5)

        # Champs de recherche en 2 colonnes et 6 lignes
        search_labels = ["No. soumission", "Facture no.", "Date de:", "Client", "Adresse", "Date à:"]
        self.search_vars = {}
        for idx, label in enumerate(search_labels):
            row = idx % 3  # 0, 1, 2 pour les lignes
            col = (idx // 3) * 2  # 0 pour gauche, 2 pour droite
            tk.Label(search_frame, text=label).grid(row=row, column=col, padx=5, pady=5, sticky="e")
            var = tk.StringVar()
            entry = tk.Entry(search_frame, textvariable=var, width=20)
            entry.grid(row=row, column=col+1, padx=5, pady=5, sticky="w")
            self.search_vars[label] = var
            if label in ["Date de:", "Date à:"]:
                entry.insert(0, "DD-MM-YYYY")
                entry.bind("<FocusIn>", lambda event, e=entry: e.delete(0, tk.END) if e.get() == "DD-MM-YYYY" else None)

        # Bouton de recherche
        tk.Button(search_frame, text="Rechercher", command=self.search_costs).grid(row=3, column=0, columnspan=4, pady=5)

        # Section résultats
        results_frame = ttkb.LabelFrame(main_frame, text="Résultats", padding=10)
        results_frame.pack(fill="both", expand=True, pady=5)

        # Treeview pour afficher les résultats
        self.costs_tree = ttkb.Treeview(
            results_frame,
            columns=("No. Soumission", "Client", "Adresse", "Date des travaux", "Facture no.", "Montant facture", "Coût de contrat", "Profit"),
            show="headings"
        )
        headers = ["No. Soumission", "Client", "Adresse", "Date des travaux", "Facture no.", "Montant facture", "Coût de contrat", "Profit"]
        for header in headers:
            self.costs_tree.heading(header, text=header, anchor="w")  # Alignement à gauche
        self.costs_tree.column("No. Soumission", width=100, anchor="w")
        self.costs_tree.column("Client", width=150, anchor="w")
        self.costs_tree.column("Adresse", width=200, anchor="w")
        self.costs_tree.column("Date des travaux", width=100, anchor="w")
        self.costs_tree.column("Facture no.", width=100, anchor="w")
        self.costs_tree.column("Montant facture", width=100, anchor="e")  # Alignement à droite pour les montants
        self.costs_tree.column("Coût de contrat", width=100, anchor="e")
        self.costs_tree.column("Profit", width=100, anchor="e")
        self.costs_tree.pack(fill="both", expand=True)

        # Frame pour les totaux
        totals_frame = ttkb.LabelFrame(main_frame, text="Totaux", padding=10)
        totals_frame.pack(fill="x", pady=5)
        self.total_facture_var = tk.StringVar(value="0.00")
        self.total_cout_var = tk.StringVar(value="0.00")
        self.total_profit_var = tk.StringVar(value="0.00")
        tk.Label(totals_frame, text="Total des factures :").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        tk.Label(totals_frame, textvariable=self.total_facture_var, borderwidth=2, relief="solid", width=12).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        tk.Label(totals_frame, text="Total des coûts de contrat :").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        tk.Label(totals_frame, textvariable=self.total_cout_var, borderwidth=2, relief="solid", width=12).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        tk.Label(totals_frame, text="Total des profits :").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        tk.Label(totals_frame, textvariable=self.total_profit_var, borderwidth=2, relief="solid", width=12).grid(row=0, column=5, padx=5, pady=5, sticky="w")

        # Charger les 25 derniers coûts
        self.load_costs()

        # Boutons d'action
        action_frame = ttkb.Frame(main_frame)
        action_frame.pack(pady=10)
        ttkb.Button(action_frame, text="Supprimer ligne", command=self.delete_cost, bootstyle="danger").pack(side="left", padx=5)
        ttkb.Button(action_frame, text="Modifier ligne", command=self.edit_cost, bootstyle="primary").pack(side="left", padx=5)
        ttkb.Button(action_frame, text="Exporter en PDF", command=self.export_to_pdf, bootstyle="success").pack(side="left", padx=5)

    def validate_date(self, date_str):
        """Valide et convertit une date DD-MM-YYYY en YYYY-MM-DD."""
        if not date_str or date_str == "DD-MM-YYYY":
            return ""
        try:
            # Vérifier le format DD-MM-YYYY
            if not re.match(r"^\d{2}-\d{2}-\d{4}$", date_str):
                raise ValueError("Format de date invalide. Utilisez DD-MM-YYYY.")
            # Convertir en objet datetime pour valider
            datetime.strptime(date_str, "%d-%m-%Y")
            # Convertir en YYYY-MM-DD pour SQLite
            return datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d")
        except ValueError as e:
            logging.error(f"Erreur de validation de la date '{date_str}' : {e}")
            return None

    def load_costs(self, costs=None):
        """Charge ou actualise la liste des coûts dans le Treeview et calcule les totaux."""
        for item in self.costs_tree.get_children():
            self.costs_tree.delete(item)
        if costs is None:
            costs = self.db_manager.get_recent_costs(limit=25)
        total_facture = 0.0
        total_cout = 0.0
        total_profit = 0.0
        for cost in costs:
            montant_facture = float(cost[6]) if cost[6] is not None else 0.0
            total_reel = float(cost[7]) if cost[7] is not None else 0.0
            profit = float(cost[8]) if cost[8] is not None else 0.0
            total_facture += montant_facture
            total_cout += total_reel
            total_profit += profit
            self.costs_tree.insert("", "end", values=(
                cost[0],  # submission_number
                cost[2],  # client
                cost[3],  # adresse
                cost[1],  # date_travaux
                cost[5],  # facture_no
                f"{montant_facture:.2f}",  # montant_facture_av_tx
                f"{total_reel:.2f}",  # total_reel
                f"{profit:.2f}"  # profit
            ))
        # Mettre à jour les totaux
        self.total_facture_var.set(f"{total_facture:.2f}")
        self.total_cout_var.set(f"{total_cout:.2f}")
        self.total_profit_var.set(f"{total_profit:.2f}")

    def search_costs(self):
        """Recherche les coûts selon les critères saisis."""
        try:
            params = {
                "submission_number": self.search_vars["No. soumission"].get().strip(),
                "facture_no": self.search_vars["Facture no."].get().strip(),
                "client": self.search_vars["Client"].get().strip(),
                "adresse": self.search_vars["Adresse"].get().strip(),
                "date_from": self.validate_date(self.search_vars["Date de:"].get().strip()),
                "date_to": self.validate_date(self.search_vars["Date à:"].get().strip())
            }
            if params["date_from"] is None or params["date_to"] is None:
                messagebox.showerror("Erreur", "Format de date invalide. Utilisez DD-MM-YYYY.")
                return
            costs = self.db_manager.search_costs(**params)
            self.load_costs(costs)
        except Exception as e:
            logging.error(f"Erreur lors de la recherche des coûts : {e}")
            messagebox.showerror("Erreur", f"Erreur lors de la recherche : {str(e)}")

    def delete_cost(self):
        """Supprime l'enregistrement sélectionné dans la table costs."""
        selected = self.costs_tree.selection()
        if not selected:
            tk.messagebox.showwarning("Avertissement", "Veuillez sélectionner une ligne.")
            return
        values = self.costs_tree.item(selected[0])["values"]
        submission_number = values[0]
        date_travaux = values[3]  # Date des travaux est à l'index 3
        if tk.messagebox.askyesno("Confirmation", f"Voulez-vous supprimer le coût pour la soumission {submission_number} et la date {date_travaux} ?"):
            try:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "DELETE FROM costs WHERE submission_number = ? AND date_travaux = ?",
                        (submission_number, date_travaux)
                    )
                    conn.commit()
                self.load_costs()
                tk.messagebox.showinfo("Succès", f"Coût pour la soumission {submission_number}, date {date_travaux} supprimé.")
            except Exception as e:
                logging.error(f"Erreur lors de la suppression du coût : {e}")
                tk.messagebox.showerror("Erreur", f"Erreur lors de la suppression : {str(e)}")

    def edit_cost(self):
        """Ouvre un formulaire pour modifier l'enregistrement sélectionné."""
        selected = self.costs_tree.selection()
        if not selected:
            tk.messagebox.showwarning("Avertissement", "Veuillez sélectionner une ligne.")
            return
        cost_data = self.costs_tree.item(selected[0])["values"]
        submission_number = cost_data[0]
        date_travaux = cost_data[3]  # Date des travaux est à l'index 3
        form = CostEditForm(self.window, self.db_manager, cost_data, submission_number, date_travaux)
        self.window.wait_window(form.window)
        self.load_costs()


    def export_to_pdf(self):
        """Exporte les résultats affichés dans un PDF."""
        try:
            costs = []
            for item in self.costs_tree.get_children():
                values = self.costs_tree.item(item)["values"]
                costs.append({
                    "submission_number": values[0],
                    "client": values[1],
                    "adresse": values[2],
                    "date_travaux": values[3],
                    "facture_no": values[4],
                    "montant_facture": values[5],
                    "total_reel": values[6],
                    "profit": values[7]
                })
            if not costs:
                messagebox.showwarning("Avertissement", "Aucune donnée à exporter.")
                return

            # Générer le contenu LaTeX avec les totaux
            latex_content = self.generate_latex_content(costs)
            with open("costs_report.tex", "w", encoding="utf-8") as f:
                f.write(latex_content)
            messagebox.showinfo("Succès", "Rapport généré dans costs_report.tex. Veuillez le compiler avec un compilateur LaTeX.")
        except Exception as e:
            logging.error(f"Erreur lors de l'exportation en PDF : {e}")
            messagebox.showerror("Erreur", f"Erreur lors de l'exportation : {str(e)}")

    def generate_latex_content(self, costs):
        """Génère le contenu LaTeX pour le rapport des coûts."""
        total_facture = float(self.total_facture_var.get())
        total_cout = float(self.total_cout_var.get())
        total_profit = float(self.total_profit_var.get())
        return r"""
\documentclass[a4paper,12pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{geometry}
\geometry{margin=1in}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{pdflscape}
\begin{document}
\begin{landscape}
\section*{Sommaire des coûts de contrat}
\begin{longtable}{l l l l l r r r}
\toprule
\textbf{No. Soumission} & \textbf{Client} & \textbf{Adresse} & \textbf{Date des travaux} & \textbf{Facture no.} & \textbf{Montant facture} & \textbf{Coût de contrat} & \textbf{Profit} \\
\midrule
""" + "\n".join([
            f"{cost['submission_number']} & {cost['client']} & {cost['adresse']} & {cost['date_travaux']} & {cost['facture_no']} & {cost['montant_facture']} & {cost['total_reel']} & {cost['profit']} \\\\"
            for cost in costs
        ]) + r"""
\midrule
\textbf{Total} & & & & & """ + f"{total_facture:.2f} & {total_cout:.2f} & {total_profit:.2f} \\\\" + r"""
\bottomrule
\end{longtable}
\end{landscape}
\end{document}
"""

class CostEditForm:
    def __init__(self, parent, db_manager, cost_data, submission_number, date_travaux):
        self.parent = parent
        self.db_manager = db_manager
        self.submission_number = submission_number
        self.date_travaux = date_travaux
        self.window = ttkb.Toplevel(parent)
        self.window.title("Modifier coût de contrat")
        self.window.geometry("400x400")

        # Frame principal
        main_frame = ttkb.Frame(self.window)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Champs du formulaire
        labels = ["No. soumission", "Client", "Adresse", "Date des travaux", "Facture no.", "Montant facture", "Coût de contrat", "Profit"]
        self.entries = {}
        for idx, label in enumerate(labels):
            tk.Label(main_frame, text=label).grid(row=idx, column=0, padx=5, pady=5, sticky="e")
            var = tk.StringVar(value=str(cost_data[idx]) if cost_data[idx] is not None else "")
            entry = tk.Entry(main_frame, textvariable=var, width=30)
            entry.grid(row=idx, column=1, padx=5, pady=5, sticky="w")
            self.entries[label] = var
            if label in ["No. soumission", "Date des travaux"]:
                entry.configure(state="readonly")  # Empêche la modification des clés

        # Boutons
        button_frame = ttkb.Frame(main_frame)
        button_frame.grid(row=len(labels), column=0, columnspan=2, pady=10)
        ttkb.Button(button_frame, text="Sauvegarder", command=self.save, bootstyle="success").pack(side="left", padx=5)
        ttkb.Button(button_frame, text="Annuler", command=self.window.destroy, bootstyle="danger").pack(side="left", padx=5)

    def save(self):
        """Sauvegarde les modifications dans la table costs."""
        try:
            data = {
                "client": self.entries["Client"].get(),
                "adresse": self.entries["Adresse"].get(),
                "facture_no": self.entries["Facture no."].get(),
                "montant_facture_av_tx": float(self.entries["Montant facture"].get()) if self.entries["Montant facture"].get() else 0.0,
                "total_reel": float(self.entries["Coût de contrat"].get()) if self.entries["Coût de contrat"].get() else 0.0,
                "profit": float(self.entries["Profit"].get()) if self.entries["Profit"].get() else 0.0
            }
            try:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE costs
                        SET client = ?, adresse = ?, facture_no = ?, montant_facture_av_tx = ?, total_reel = ?, profit = ?
                        WHERE submission_number = ? AND date_travaux = ?
                    """, (
                        data["client"], data["adresse"], data["facture_no"],
                        data["montant_facture_av_tx"], data["total_reel"], data["profit"],
                        self.submission_number, self.date_travaux
                    ))
                    conn.commit()
                tk.messagebox.showinfo("Succès", "Coût modifié avec succès.")
                self.window.destroy()
            except Exception as e:
                logging.error(f"Erreur lors de la mise à jour du coût : {e}")
                tk.messagebox.showerror("Erreur", f"Erreur lors de la mise à jour : {str(e)}")
        except ValueError as e:
            logging.error(f"Erreur lors de la conversion des valeurs numériques : {e}")
            tk.messagebox.showerror("Erreur", "Veuillez vérifier les valeurs numériques (Montant facture, Coût de contrat, Profit).")