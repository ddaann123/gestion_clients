import sqlite3
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        from .models import init_database
        init_database(db_path)
    
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
        """Récupère tous les détails des produits."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT nom, prix_base, devise_base, prix_transport, devise_transport, type_produit, couverture_1_pouce
                FROM produits
            """)
            return cursor.fetchall()
    
    def get_produit_ratios(self, produit_nom):
        """Récupère les ratios et la valeur par défaut pour un produit."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, ratio, est_defaut
                FROM produit_ratios
                WHERE produit_nom = ?
            """, (produit_nom,))
            return cursor.fetchall()
    
    def add_produit(self, nom, prix_base, devise_base, prix_transport, devise_transport, type_produit, couverture_1_pouce, ratios=None):
        """Ajoute un produit et ses ratios (si type Ratio)."""
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
        """Met à jour un produit et ses ratios (si type Ratio)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    UPDATE produits
                    SET nom = ?, prix_base = ?, devise_base = ?, prix_transport = ?, devise_transport = ?, type_produit = ?, couverture_1_pouce = ?
                    WHERE nom = ?
                """, (nom, prix_base, devise_base, prix_transport, devise_transport, type_produit, couverture_1_pouce, old_nom))
                
                # Supprimer les anciens ratios
                cursor.execute("DELETE FROM produit_ratios WHERE produit_nom = ?", (old_nom,))
                
                # Ajouter les nouveaux ratios si type Ratio
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
        """Supprime un produit (les ratios sont supprimés automatiquement via CASCADE)."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM produits WHERE nom = ?", (nom,))
            conn.commit()
