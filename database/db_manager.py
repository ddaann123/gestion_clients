import sqlite3
from contextlib import contextmanager
import json
import os
import ast
from datetime import datetime
import logging

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, "../database/clients.db")
        else:
            base_dir = os.path.dirname(os.path.abspath(db_path))
        self.db_path = os.path.abspath(db_path)
        self.txt_path = os.path.abspath(os.path.join(base_dir, "../donnees_chantier.txt"))
        from .models import init_database
        init_database(self.db_path)
        self.sync_txt_to_db()
        print(f"[DEBUG] Base de données utilisée : {self.db_path}")
        print(f"[DEBUG] Fichier texte utilisé : {self.txt_path}")

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def get_cursor(self):
        conn = sqlite3.connect(self.db_path)
        return conn, conn.cursor()

    def close(self):
        pass

    def read_txt_file(self):
        """
        Lit donnees_chantier.txt, gérant à la fois le format JSON et le format ligne par ligne.
        Retourne une liste de dictionnaires avec les clés normalisées.
        """
        if not os.path.exists(self.txt_path):
            print(f"[DEBUG] Fichier {self.txt_path} non trouvé")
            return []

        data = []
        key_mapping = {
            "soumission": "soumission_reel",
            "client": "client_reel",
            "superficie": "superficie_reel",
            "produit": "produit_reel",
            "sable_total": "sable_total_reel",
            "sable_transporter": "sable_transporter_reel",
            "sable_commande": "sable_commande_reel",
            "sacs_utilises": "sacs_utilises_reel",
            "sable_utilise": "sable_utilise_reel",
            "membrane_posee": "membrane_posee_reel",
            "nb_rouleaux_installes": "nb_rouleaux_installes_reel"
        }

        try:
            with open(self.txt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    print(f"[DEBUG] Fichier {self.txt_path} vide")
                    return []

                # Essayer de parser comme JSON
                try:
                    data = json.loads(content)
                    if not isinstance(data, list):
                        print(f"[DEBUG] Fichier {self.txt_path} n'est pas une liste JSON")
                        data = []
                    else:
                        # Normaliser les clés pour les entrées JSON
                        for entry in data:
                            normalized_entry = {}
                            for old_key, new_key in key_mapping.items():
                                normalized_entry[new_key] = entry.get(old_key, entry.get(new_key, ""))
                            for key in entry:
                                if key not in key_mapping and key not in normalized_entry:
                                    normalized_entry[key] = entry[key]
                            if "donnees_json" not in normalized_entry:
                                normalized_entry["donnees_json"] = json.dumps({"heures_chantier": normalized_entry.get("heures_chantier", {})})
                            data[data.index(entry)] = normalized_entry
                        print(f"[DEBUG] {len(data)} entrées lues depuis {self.txt_path} (format JSON)")
                        return data
                except json.JSONDecodeError:
                    print(f"[DEBUG] Fichier {self.txt_path} n'est pas un JSON valide, tentative de lecture ligne par ligne")

                # Réinitialiser le curseur et lire ligne par ligne
                f.seek(0)
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = ast.literal_eval(line)
                        if not isinstance(entry, dict):
                            print(f"[DEBUG] Ligne ignorée (pas un dictionnaire) : {line[:50]}...")
                            continue
                        normalized_entry = {}
                        for old_key, new_key in key_mapping.items():
                            normalized_entry[new_key] = entry.get(old_key, "")
                        for key in entry:
                            if key not in key_mapping and key not in normalized_entry:
                                normalized_entry[key] = entry[key]
                        if "donnees_json" not in normalized_entry:
                            normalized_entry["donnees_json"] = json.dumps({"heures_chantier": normalized_entry.get("heures_chantier", {})})
                        data.append(normalized_entry)
                    except (SyntaxError, ValueError) as e:
                        print(f"[DEBUG] Erreur de parsing de la ligne : {line[:50]}... ({e})")
                        continue

                # Réécrire le fichier en JSON valide si des données ont été lues
                if data:
                    with open(self.txt_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"[DEBUG] Fichier {self.txt_path} converti en JSON valide")
                else:
                    print(f"[DEBUG] Aucune donnée valide trouvée dans {self.txt_path}")

                print(f"[DEBUG] {len(data)} entrées lues depuis {self.txt_path} (format ligne par ligne)")
                return data
        except Exception as e:
            print(f"[DEBUG] Erreur lors de la lecture de {self.txt_path} : {e}")
            return []

    def sync_txt_to_db(self):
        """
        Synchronise les données de donnees_chantier.txt avec la table chantiers_reels.
        Supprime les duplicatas en gardant la dernière entrée par soumission_reel.
        """
        try:
            data = self.read_txt_file()
            if not data:
                print(f"[DEBUG] Aucun donnée valide dans {self.txt_path}")
                return

            unique_data = {}
            for entry in data:
                soumission_reel = entry.get("soumission_reel")
                if soumission_reel:
                    date_travaux = entry.get("date_travaux", "01-01-1900")
                    try:
                        date_travaux_dt = datetime.strptime(date_travaux, "%d-%m-%Y")
                    except ValueError:
                        date_travaux_dt = datetime(1900, 1, 1)
                    if soumission_reel not in unique_data or \
                       date_travaux_dt > datetime.strptime(unique_data[soumission_reel].get("date_travaux", "01-01-1900"), "%d-%m-%Y"):
                        unique_data[soumission_reel] = entry

            # Réécrire donnees_chantier.txt sans duplicatas
            with open(self.txt_path, 'w', encoding='utf-8') as f:
                json.dump(list(unique_data.values()), f, indent=2, ensure_ascii=False)
            print(f"[DEBUG] Fichier {self.txt_path} mis à jour avec {len(unique_data)} entrées uniques")

            # Vider la table chantiers_reels
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM chantiers_reels")
                conn.commit()

            # Insérer les données dans chantiers_reels
            for entry in unique_data.values():
                self.insert_work_sheet(entry)
            print(f"[DEBUG] Table chantiers_reels synchronisée avec {len(unique_data)} entrées")

        except Exception as e:
            print(f"[DEBUG] Erreur lors de la synchronisation de {self.txt_path} vers chantiers_reels : {e}")

    def delete_work_sheet(self, soumission_reel):
        """
        Supprime une feuille de travail de chantiers_reels et de donnees_chantier.txt.
        Retourne True si la suppression est réussie, False sinon.
        """
        try:
            # Supprimer de la table chantiers_reels
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM chantiers_reels WHERE soumission_reel = ?", (soumission_reel,))
                conn.commit()
                if cursor.rowcount > 0:
                    print(f"[DEBUG] Feuille {soumission_reel} supprimée de chantiers_reels")
                else:
                    print(f"[DEBUG] Aucune feuille trouvée dans chantiers_reels pour soumission_reel={soumission_reel}")

            # Supprimer de donnees_chantier.txt
            data = self.read_txt_file()
            initial_count = len(data)
            updated_data = [entry for entry in data if entry.get("soumission_reel") != soumission_reel]
            if len(updated_data) < initial_count:
                with open(self.txt_path, 'w', encoding='utf-8') as f:
                    json.dump(updated_data, f, indent=2, ensure_ascii=False)
                print(f"[DEBUG] Feuille {soumission_reel} supprimée de {self.txt_path}")
                return True
            else:
                print(f"[DEBUG] Aucune feuille trouvée dans {self.txt_path} pour soumission_reel={soumission_reel}")
                # Si aucune donnée n'a été lue à cause d'un format incorrect, forcer la réécriture du fichier
                if not data:
                    with open(self.txt_path, 'w', encoding='utf-8') as f:
                        json.dump([], f, indent=2, ensure_ascii=False)
                    print(f"[DEBUG] Fichier {self.txt_path} réinitialisé à vide en raison d'un format incorrect")
                    return True
                return False
        except Exception as e:
            print(f"[DEBUG] Erreur lors de la suppression de {soumission_reel} : {e}")
            return False

    def search_work_sheets(self, criteres=None, limit=None):
        """
        Recherche les feuilles de travail dans chantiers_reels selon les critères fournis.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT soumission_reel, client_reel, adresse_reel, date_travaux, date_soumission
                FROM chantiers_reels
                WHERE 1=1
            """
            params = []
            if criteres:
                for key, value in criteres.items():
                    query += f" AND {key} LIKE ?"
                    params.append(f"%{value}%")
            query += " ORDER BY date_travaux DESC"
            if limit:
                query += f" LIMIT ?"
                params.append(limit)
            cursor.execute(query, params)
            results = cursor.fetchall()
            print(f"[DEBUG] Résultats bruts de search_work_sheets : {results}")
            return results

    def charger_feuille(self, soumission_reel):
        """
        Charge les données d'une feuille de travail depuis chantiers_reels.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chantiers_reels WHERE soumission_reel = ?", (soumission_reel,))
            row = cursor.fetchone()
            if not row:
                print(f"[DEBUG] Aucune feuille trouvée dans chantiers_reels pour soumission_reel={soumission_reel}")
                return None
            colonnes = [desc[0] for desc in cursor.description]
            data = dict(zip(colonnes, row))
            print(f"[DEBUG] Feuille chargée pour soumission_reel={soumission_reel} : {data}")
            return data

    def insert_work_sheet(self, data):
        """
        Insère une feuille de travail dans chantiers_reels et met à jour donnees_chantier.txt.
        """
        columns = [
            "soumission_reel", "client_reel", "superficie_reel", "produit_reel", "produit_diff",
            "sable_total_reel", "sable_transporter_reel", "sable_commande_reel", "sacs_utilises_reel",
            "sable_utilise_reel", "membrane_posee_reel", "nb_rouleaux_installes_reel", "marches_reel",
            "notes_reel", "date_travaux", "date_soumission", "donnees_json", "adresse_reel",
            "type_membrane", "nb_sacs_prevus", "thickness", "notes_bureau"
        ]
        default_values = {
            "soumission_reel": "",
            "client_reel": "",
            "superficie_reel": "",
            "produit_reel": "",
            "produit_diff": "",
            "sable_total_reel": "",
            "sable_transporter_reel": "",
            "sable_commande_reel": "",
            "sacs_utilises_reel": "",
            "sable_utilise_reel": "",
            "membrane_posee_reel": "",
            "nb_rouleaux_installes_reel": "",
            "marches_reel": "",
            "notes_reel": "",
            "date_travaux": "",
            "date_soumission": "",
            "donnees_json": json.dumps({"heures_chantier": data.get("heures_chantier", {})}),
            "adresse_reel": "",
            "type_membrane": "",
            "nb_sacs_prevus": "",
            "thickness": "",
            "notes_bureau": ""
        }
        try:
            values = [data.get(col, default_values[col]) for col in columns]
            with self.get_connection() as conn:
                cursor = conn.cursor()
                query = f"""
                    INSERT OR REPLACE INTO chantiers_reels ({", ".join(columns)})
                    VALUES ({", ".join(["?" for _ in columns])})
                """
                cursor.execute(query, values)
                conn.commit()
                print(f"[DEBUG] Feuille insérée/mise à jour dans chantiers_reels : {data.get('soumission_reel')}")

            # Mettre à jour donnees_chantier.txt
            txt_data = self.read_txt_file()
            txt_data = [entry for entry in txt_data if entry.get("soumission_reel") != data.get("soumission_reel")]
            txt_data.append(data)
            with open(self.txt_path, 'w', encoding='utf-8') as f:
                json.dump(txt_data, f, indent=2, ensure_ascii=False)
            print(f"[DEBUG] Feuille insérée/mise à jour dans {self.txt_path} : {data.get('soumission_reel')}")

        except Exception as e:
            print(f"[DEBUG] Erreur lors de l'insertion de {data.get('soumission_reel')} : {e}")



    
    def get_produits(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nom FROM produits")
            return [row[0] for row in cursor.fetchall()]

    def get_sable(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, transporteur, camion, ville, prix_voyage, prix_sable FROM sable")
            return cursor.fetchall()

    def add_sable(self, transporteur, camion, ville, prix_voyage, prix_sable):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sable (transporteur, camion, ville, prix_voyage, prix_sable)
                VALUES (?, ?, ?, ?, ?)
            """, (transporteur, camion, ville, prix_voyage, prix_sable))
            conn.commit()

    def update_sable(self, sable_id, transporteur, camion, ville, prix_voyage, prix_sable):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE sable SET transporteur = ?, camion = ?, ville = ?, prix_voyage = ?, prix_sable = ?
                WHERE id = ?
            """, (transporteur, camion, ville, prix_voyage, prix_sable, sable_id))
            conn.commit()

    def delete_sable(self, sable_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sable WHERE id = ?", (sable_id,))
            conn.commit()

    def get_clients(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nom, courriel, telephone, adresse FROM clients")
            return cursor.fetchall()

    def search_clients(self, query):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nom, courriel, telephone, adresse FROM clients WHERE nom LIKE ?", (f"%{query}%",))
            return cursor.fetchall()

    def add_client(self, nom, courriel="", telephone="", adresse=""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clients (nom, courriel, telephone, adresse)
                VALUES (?, ?, ?, ?)
            """, (nom, courriel, telephone, adresse))
            conn.commit()

    def update_client(self, client_id, nom, courriel, telephone, adresse):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE clients SET nom = ?, courriel = ?, telephone = ?, adresse = ?
                WHERE id = ?
            """, (nom, courriel, telephone, adresse, client_id))
            conn.commit()

    def delete_client(self, client_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            conn.commit()

    def get_contacts(self, client_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nom, telephone, courriel FROM contacts WHERE client_id = ?", (client_id,))
            return cursor.fetchall()

    def add_contact(self, client_id, nom, telephone="", courriel=""):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM contacts WHERE client_id = ?", (client_id,))
            count = cursor.fetchone()[0]
            if count >= 10:
                raise ValueError("Limite de 10 contacts par client atteinte")
            cursor.execute("""
                INSERT INTO contacts (client_id, nom, telephone, courriel)
                VALUES (?, ?, ?, ?)
            """, (client_id, nom, telephone, courriel))
            conn.commit()

    def update_contact(self, contact_id, nom, telephone, courriel):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE contacts SET nom = ?, telephone = ?, courriel = ?
                WHERE id = ?
            """, (nom, telephone, courriel, contact_id))
            conn.commit()

    def delete_contact(self, contact_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
            conn.commit()

    def get_contact_by_name(self, nom):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT telephone, courriel FROM contacts
                WHERE LOWER(nom) = LOWER(?)
            """, (nom,))
            return cursor.fetchone()

    def get_main_doeuvre(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, metier, taux_horaire_chantier, taux_horaire_transport FROM main_doeuvre")
            return cursor.fetchall()

    def add_main_doeuvre(self, metier, taux_horaire_chantier, taux_horaire_transport):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO main_doeuvre (metier, taux_horaire_chantier, taux_horaire_transport)
                VALUES (?, ?, ?)
            """, (metier, taux_horaire_chantier, taux_horaire_transport))
            conn.commit()

    def update_main_doeuvre(self, main_doeuvre_id, metier, taux_horaire_chantier, taux_horaire_transport):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE main_doeuvre SET metier = ?, taux_horaire_chantier = ?, taux_horaire_transport = ?
                WHERE id = ?
            """, (metier, taux_horaire_chantier, taux_horaire_transport, main_doeuvre_id))
            conn.commit()

    def delete_main_doeuvre(self, main_doeuvre_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM main_doeuvre WHERE id = ?", (main_doeuvre_id,))
            conn.commit()

    def get_produit_details(self):
        """Récupère les détails des produits depuis la table produits."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT nom, prix_base, devise_base, prix_transport, devise_transport, type_produit, couverture_1_pouce
                    FROM produits
                """)
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des détails des produits : {e}")
            return []

    def get_produit_ratios(self, produit_nom):
        """Récupère les ratios des produits depuis la table produit_ratios."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, ratio, est_defaut
                    FROM produit_ratios
                    WHERE produit_nom = ?
                """, (produit_nom,))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des ratios des produits : {e}")
            return []

    def add_produit(self, nom, prix_base, devise_base, prix_transport, devise_transport, type_produit, couverture_1_pouce, ratios=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO produits (nom, prix_base, devise_base, prix_transport, devise_transport, type_produit, couverture_1_pouce)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (nom, prix_base, devise_base, prix_transport, devise_transport, type_produit, couverture_1_pouce))
                
                if type_produit == "RATIO" and ratios:
                    if len(ratios) < 1:
                        raise ValueError("Au moins un ratio est requis pour un produit de type Ratio")
                    default_count = sum(1 for _, is_default in ratios if is_default)
                    if default_count != 1:
                        raise ValueError("Exactement un ratio doit être marqué comme par défaut")
                    
                    for ratio, is_default in ratios:
                        cursor.execute("""
                            INSERT INTO produit_ratios (produit_nom, ratio, est_defaut)
                            VALUES (?, ?, ?)
                        """, (nom, ratio, 1 if is_default else 0))
                
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e

    def update_produit(self, old_nom, nom, prix_base, devise_base, prix_transport, devise_transport, type_produit, couverture_1_pouce, ratios=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    UPDATE produits
                    SET nom = ?, prix_base = ?, devise_base = ?, prix_transport = ?, devise_transport = ?, type_produit = ?, couverture_1_pouce = ?
                    WHERE nom = ?
                """, (nom, prix_base, devise_base, prix_transport, devise_transport, type_produit, couverture_1_pouce, old_nom))
                
                cursor.execute("DELETE FROM produit_ratios WHERE produit_nom = ?", (old_nom,))
                
                if type_produit == "RATIO" and ratios:
                    if len(ratios) < 1:
                        raise ValueError("Au moins un ratio est requis pour un produit de type Ratio")
                    default_count = sum(1 for _, is_default in ratios if is_default)
                    if default_count != 1:
                        raise ValueError("Exactement un ratio doit être marqué comme par défaut")
                    
                    for ratio, is_default in ratios:
                        cursor.execute("""
                            INSERT INTO produit_ratios (produit_nom, ratio, est_defaut)
                            VALUES (?, ?, ?)
                        """, (nom, ratio, 1 if is_default else 0))
                
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e

    def delete_produit(self, nom):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM produits WHERE nom = ?", (nom,))
            conn.commit()

    def get_pensions(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, type_pension, montant_par_jour FROM pensions")
            return cursor.fetchall()

    def add_pension(self, type_pension, montant_par_jour):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO pensions (type_pension, montant_par_jour)
                    VALUES (?, ?)
                """, (type_pension, montant_par_jour))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def update_pension(self, pension_id, type_pension, montant_par_jour):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE pensions SET type_pension = ?, montant_par_jour = ?
                    WHERE id = ?
                """, (type_pension, montant_par_jour, pension_id))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def delete_pension(self, pension_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM pensions WHERE id = ?", (pension_id,))
            conn.commit()

    def get_machinerie(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, type_machinerie, taux_horaire FROM machinerie")
            return cursor.fetchall()

    def add_machinerie(self, type_machinerie, taux_horaire):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO machinerie (type_machinerie, taux_horaire)
                    VALUES (?, ?)
                """, (type_machinerie, taux_horaire))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def update_machinerie(self, machinerie_id, type_machinerie, taux_horaire):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE machinerie SET type_machinerie = ?, taux_horaire = ?
                    WHERE id = ?
                """, (type_machinerie, taux_horaire, machinerie_id))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def delete_machinerie(self, machinerie_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM machinerie WHERE id = ?", (machinerie_id,))
            conn.commit()

    def get_apprets_scellants(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nom_produit, prix, format_litres, couverture_pi2 FROM apprets_scellants")
            return cursor.fetchall()

    def add_apprets_scellants(self, nom_produit, prix, format_litres, couverture_pi2):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO apprets_scellants (nom_produit, prix, format_litres, couverture_pi2)
                    VALUES (?, ?, ?, ?)
                """, (nom_produit, prix, format_litres, couverture_pi2))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def update_apprets_scellants(self, apprets_scellants_id, nom_produit, prix, format_litres, couverture_pi2):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE apprets_scellants SET nom_produit = ?, prix = ?, format_litres = ?, couverture_pi2 = ?
                    WHERE id = ?
                """, (nom_produit, prix, format_litres, couverture_pi2, apprets_scellants_id))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def delete_apprets_scellants(self, apprets_scellants_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM apprets_scellants WHERE id = ?", (apprets_scellants_id,))
            conn.commit()

    def get_membranes(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, modele_membrane, couverture_pi2, prix_rouleau, prix_pi2_membrane, pose_pi2_sans_divisions, pose_pi2_avec_divisions FROM membranes")
            return cursor.fetchall()

    def add_membranes(self, modele_membrane, couverture_pi2, prix_rouleau, prix_pi2_membrane, pose_pi2_sans_divisions, pose_pi2_avec_divisions):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO membranes (modele_membrane, couverture_pi2, prix_rouleau, prix_pi2_membrane, pose_pi2_sans_divisions, pose_pi2_avec_divisions)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (modele_membrane, couverture_pi2, prix_rouleau, prix_pi2_membrane, pose_pi2_sans_divisions, pose_pi2_avec_divisions))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def update_membranes(self, membranes_id, modele_membrane, couverture_pi2, prix_rouleau, prix_pi2_membrane, pose_pi2_sans_divisions, pose_pi2_avec_divisions):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE membranes SET modele_membrane = ?, couverture_pi2 = ?, prix_rouleau = ?, prix_pi2_membrane = ?, pose_pi2_sans_divisions = ?, pose_pi2_avec_divisions = ?
                    WHERE id = ?
                """, (modele_membrane, couverture_pi2, prix_rouleau, prix_pi2_membrane, pose_pi2_sans_divisions, pose_pi2_avec_divisions, membranes_id))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def delete_membranes(self, membranes_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM membranes WHERE id = ?", (membranes_id,))
            conn.commit()

    def insert_submission(self, data: dict):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            values = list(data.values())

            try:
                cursor.execute(f"""
                    INSERT INTO submissions ({columns}) VALUES ({placeholders})
                """, values)
                conn.commit()
            except sqlite3.IntegrityError as e:
                if "submission_number" in str(e):
                    raise ValueError(f"Le numéro de soumission « {data.get('submission_number')} » existe déjà.")
                else:
                    raise

    def search_submissions(self, filters, limit=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT submission_number, client_name, contact, projet, ville, etat, date_submission
                FROM submissions
                WHERE 1=1
            """
            params = []
            if filters.get("submission_number"):
                query += " AND submission_number LIKE ?"
                params.append(f"%{filters['submission_number']}%")
            if filters.get("client_name"):
                query += " AND client_name LIKE ?"
                params.append(f"%{filters['client_name']}%")
            if filters.get("contact"):
                query += " AND contact LIKE ?"
                params.append(f"%{filters['contact']}%")
            if filters.get("projet"):
                query += " AND projet LIKE ?"
                params.append(f"%{filters['projet']}%")
            if filters.get("ville"):
                query += " AND ville LIKE ?"
                params.append(f"%{filters['ville']}%")
            if filters.get("etat") in ("brouillon", "finalisé"):
                query += " AND etat = ?"
                params.append(filters["etat"])
            if filters.get("date_debut"):
                query += " AND date_submission >= ?"
                params.append(filters["date_debut"])
            if filters.get("date_fin"):
                query += " AND date_submission <= ?"
                params.append(filters["date_fin"])
            query += " ORDER BY date_submission DESC"
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)
            cursor.execute(query, params)
            return cursor.fetchall()

    def charger_soumission(self, submission_number):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM submissions WHERE submission_number = ?
            """, (submission_number,))
            row = cursor.fetchone()
            if not row:
                return None
            colonnes = [desc[0] for desc in cursor.description]
            data = dict(zip(colonnes, row))
            return data

    def marquer_soumission_inactive(self, submission_number):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE submissions
                SET is_active = 0
                WHERE submission_number = ?
            """, (submission_number,))
            conn.commit()

    def supprimer_soumission(self, submission_number):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM submissions WHERE submission_number = ?", (submission_number,))
            conn.commit()

    def get_membrane_by_nom(self, nom_membrane):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT prix_pi2_membrane, pose_pi2_sans_divisions, pose_pi2_avec_divisions
                FROM membranes
                WHERE LOWER(modele_membrane) = ?
            """, (nom_membrane.strip().lower(),))
            return cursor.fetchone()

    def get_all_contacts_with_clients(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT contacts.id, contacts.nom, contacts.telephone, contacts.courriel,
                    clients.nom AS client_name
                FROM contacts
                JOIN clients ON contacts.client_id = clients.id
            """)
            rows = cursor.fetchall()
            return [
                {"id": row[0], "nom": row[1], "telephone": row[2], "courriel": row[3], "client_name": row[4]}
                for row in rows
            ]

    def get_submission_by_number(self, submission_number):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM submissions WHERE submission_number = ? AND is_active = 1
            """, (submission_number,))
            return cursor.fetchone()

    def update_submission(self, submission_number, data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                UPDATE submissions
                SET revision = ?,
                    is_active = ?,
                    etat = ?,
                    year = ?,
                    sequence = ?,
                    date_submission = ?,
                    client_name = ?,
                    contact = ?,
                    projet = ?,
                    ville = ?,
                    distance = ?,
                    area = ?,
                    product = ?,
                    ratio = ?,
                    usd_cad_rate = ?,
                    thickness = ?,
                    subfloor = ?,
                    membrane = ?,
                    pose_membrane = ?,
                    sealant = ?,
                    prix_par_sac = ?,
                    total_sacs = ?,
                    prix_total_sacs = ?,
                    sable_total = ?,
                    voyages_sable = ?,
                    prix_total_sable = ?,
                    mobilisations = ?,
                    surface_per_mob = ?,
                    type_main = ?,
                    type_pension = ?,
                    type_machinerie = ?,
                    nb_hommes = ?,
                    heures_chantier = ?,
                    heures_transport = ?,
                    prix_total_pension = ?,
                    prix_total_machinerie = ?,
                    prix_total_heures_chantier = ?,
                    prix_total_heures_transport = ?,
                    ajustement1_nom = ?,
                    ajustement1_valeur = ?,
                    ajustement2_nom = ?,
                    ajustement2_valeur = ?,
                    ajustement3_nom = ?,
                    ajustement3_valeur = ?,
                    reperes_nivellement = ?,
                    sous_total_ajustements = ?,
                    sous_total_fournisseurs = ?,
                    sous_total_main_machinerie = ?,
                    total_prix_coutants = ?,
                    admin_profit_pct = ?,
                    admin_profit_montant = ?,
                    prix_vente_client = ?,
                    prix_unitaire = ?,
                    prix_total_immeuble = ?,
                    prix_pi2_ajuste = ?,
                    prix_total_ajuste = ?,
                    notes_json = ?,
                    surfaces_json = ?,
                    sable_transporter = ?,
                    truck_tonnage = ?,
                    transport_sector = ?
                WHERE submission_number = ?
            """
            params = [
                data["revision"],
                data["is_active"],
                data["etat"],
                data["year"],
                data["sequence"],
                data["date_submission"],
                data["client_name"],
                data["contact"],
                data["projet"],
                data["ville"],
                data["distance"],
                data["area"],
                data["product"],
                data["ratio"],
                data["usd_cad_rate"],
                data["thickness"],
                data["subfloor"],
                data["membrane"],
                data["pose_membrane"],
                data["sealant"],
                data["prix_par_sac"],
                data["total_sacs"],
                data["prix_total_sacs"],
                data["sable_total"],
                data["voyages_sable"],
                data["prix_total_sable"],
                data["mobilisations"],
                data["surface_per_mob"],
                data["type_main"],
                data["type_pension"],
                data["type_machinerie"],
                data["nb_hommes"],
                data["heures_chantier"],
                data["heures_transport"],
                data["prix_total_pension"],
                data["prix_total_machinerie"],
                data["prix_total_heures_chantier"],
                data["prix_total_heures_transport"],
                data["ajustement1_nom"],
                data["ajustement1_valeur"],
                data["ajustement2_nom"],
                data["ajustement2_valeur"],
                data["ajustement3_nom"],
                data["ajustement3_valeur"],
                data["reperes_nivellement"],
                data["sous_total_ajustements"],
                data["sous_total_fournisseurs"],
                data["sous_total_main_machinerie"],
                data["total_prix_coutants"],
                data["admin_profit_pct"],
                data["admin_profit_montant"],
                data["prix_vente_client"],
                data["prix_unitaire"],
                data["prix_total_immeuble"],
                data["prix_pi2_ajuste"],
                data["prix_total_ajuste"],
                data["notes_json"],
                data["surfaces_json"],
                data["sable_transporter"],
                data["truck_tonnage"],
                data["transport_sector"],
                submission_number
            ]
            cursor.execute(query, params)
            conn.commit()

    def get_submission_details(self, submission_number, columns):
        """
        Récupère les valeurs des colonnes spécifiées pour une soumission donnée.
        Args:
            submission_number (str): Le numéro de soumission (ex. 'S25-214').
            columns (list): Liste des colonnes à récupérer (ex. ['product', 'total_sacs']).
        Returns:
            dict: Dictionnaire avec les colonnes demandées et leurs valeurs, ou None si non trouvé.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Construire la liste des colonnes pour la requête
            columns_str = ", ".join(columns)
            query = f"""
                SELECT {columns_str}
                FROM submissions
                WHERE submission_number = ? AND is_active = 1
            """
            try:
                cursor.execute(query, (submission_number,))
                result = cursor.fetchone()
                if result:
                    # Retourner un dictionnaire avec les colonnes comme clés
                    return dict(zip(columns, result))
                return {}
            except sqlite3.Error as e:
                print(f"[ERREUR] Impossible de récupérer les détails de la soumission {submission_number} : {e}")
                return {}
            



    def check_cost_exists(self, submission_number, date_travaux):
        """Vérifie si une entrée existe dans la table costs pour submission_number et date_travaux."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id FROM costs WHERE submission_number = ? AND date_travaux = ?",
                    (submission_number, date_travaux)
                )
                return cursor.fetchone() is not None
        except Exception as e:
            logging.error(f"Erreur lors de la vérification de l'existence du coût : {e}")
            return False

    def save_costs(self, submission_number, date_travaux, client, adresse, surface, facture_no, montant_facture_av_tx, total_reel, profit):
        """Sauvegarde les données dans la table costs."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO costs (
                        submission_number, date_travaux, client, adresse, surface,
                        facture_no, montant_facture_av_tx, total_reel, profit
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    submission_number, date_travaux, client, adresse, surface,
                    facture_no, montant_facture_av_tx, total_reel, profit
                ))
                conn.commit()
                logging.info(f"Données sauvegardées pour submission_number={submission_number}, date_travaux={date_travaux}")
        except sqlite3.IntegrityError as e:
            logging.error(f"Erreur d'intégrité lors de la sauvegarde dans la table costs : {e}")
            raise
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde dans la table costs : {e}")
            raise

    def get_recent_costs(self, limit=25):
        """Récupère les limit derniers enregistrements de la table costs."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT submission_number, date_travaux, client, adresse, surface,
                           facture_no, montant_facture_av_tx, total_reel, profit
                    FROM costs
                    ORDER BY date_travaux DESC
                    LIMIT ?
                """, (limit,))
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Erreur lors de la récupération des coûts : {e}")
            return []

    def search_costs(self, submission_number="", facture_no="", client="", adresse="", date_from="", date_to=""):
        """Recherche les coûts selon les critères donnés."""
        try:
            query = """
                SELECT submission_number, date_travaux, client, adresse, surface,
                       facture_no, montant_facture_av_tx, total_reel, profit
                FROM costs
                WHERE 1=1
            """
            params = []
            if submission_number:
                query += " AND submission_number LIKE ?"
                params.append(f"%{submission_number}%")
            if facture_no:
                query += " AND facture_no LIKE ?"
                params.append(f"%{facture_no}%")
            if client:
                query += " AND client LIKE ?"
                params.append(f"%{client}%")
            if adresse:
                query += " AND adresse LIKE ?"
                params.append(f"%{adresse}%")
            if date_from:
                query += " AND date_travaux >= ?"
                params.append(date_from)
            if date_to:
                query += " AND date_travaux <= ?"
                params.append(date_to)
            query += " ORDER BY date_travaux DESC"
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logging.error(f"Erreur lors de la recherche des coûts : {e}")
            return []

    def delete_cost(self, submission_number):
        """Supprime un enregistrement de la table costs."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM costs WHERE submission_number = ?", (submission_number,))
                conn.commit()
                logging.info(f"Coût supprimé pour submission_number={submission_number}")
        except Exception as e:
            logging.error(f"Erreur lors de la suppression du coût : {e}")
            raise

    def update_cost(self, submission_number, client, adresse, date_travaux, facture_no, montant_facture_av_tx, total_reel, profit):
        """Met à jour un enregistrement dans la table costs."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE costs
                    SET client = ?, adresse = ?, date_travaux = ?, facture_no = ?,
                        montant_facture_av_tx = ?, total_reel = ?, profit = ?
                    WHERE submission_number = ?
                """, (
                    client, adresse, date_travaux, facture_no,
                    montant_facture_av_tx, total_reel, profit, submission_number
                ))
                conn.commit()
                logging.info(f"Coût mis à jour pour submission_number={submission_number}")
        except Exception as e:
            logging.error(f"Erreur lors de la mise à jour du coût : {e}")
            raise

    def get_main_doeuvre_details(self, metier):
        """Récupère taux_horaire_chantier et taux_horaire_transport depuis la table main_doeuvre."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT taux_horaire_chantier, taux_horaire_transport FROM main_doeuvre WHERE metier = ?", (metier,))
                result = cursor.fetchone()
                return {
                    "taux_horaire_chantier": result[0] if result else 0.0,
                    "taux_horaire_transport": result[1] if result else 0.0
                }
        except Exception as e:
            logging.error(f"Erreur dans get_main_doeuvre_details: {e}")
            return {"taux_horaire_chantier": 0.0, "taux_horaire_transport": 0.0}

    def get_machinerie_details(self, type_machinerie):
        """Récupère taux_horaire depuis la table machinerie."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT taux_horaire FROM machinerie WHERE type_machinerie = ?", (type_machinerie,))
                result = cursor.fetchone()
                return {"taux_horaire": result[0] if result else 0.0}
        except Exception as e:
            logging.error(f"Erreur dans get_machinerie_details: {e}")
            return {"taux_horaire": 0.0}

    def get_appret_details(self):
        """Récupère les détails des apprêts depuis la table apprets_scellants."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nom_produit, couverture_pi2, prix FROM apprets_scellants")
                return cursor.fetchall()
        except Exception:
            return []

    def get_membrane_details(self):
        """Récupère les détails des membranes depuis la table membranes."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT modele_membrane, couverture_pi2, prix_rouleau FROM membranes")
                return cursor.fetchall()
        except Exception:
            return []

    def get_submission_details(self, submission_number):
        """Récupère les détails d'une soumission depuis la table submissions."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                columns = ["product", "prix_par_sac", "sable_transporter", "truck_tonnage", 
                           "transport_sector", "sealant", "prix_total_heures_chantier", 
                           "prix_total_heures_transport", "prix_total_machinerie", 
                           "prix_total_pension", "type_main", "type_machinerie"]
                query = f"SELECT {', '.join(columns)} FROM submissions WHERE submission_number = ?"
                cursor.execute(query, (submission_number,))
                result = cursor.fetchone()
                if result:
                    return dict(zip(columns, result))
                logging.warning(f"Aucune soumission trouvée pour submission_number={submission_number}")
                return {}
        except Exception as e:
            logging.error(f"Erreur dans get_submission_details: {e}")
            return {}

    def get_sable(self):
        """Récupère les données de la table sable."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sable")
                return cursor.fetchall()
        except Exception:
            return []

