import sqlite3
from contextlib import contextmanager

def init_database(db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        

        # Table clients
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                courriel TEXT,
                telephone TEXT,
                adresse TEXT
            )
        """)
        
        # Table contacts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                nom TEXT NOT NULL,
                telephone TEXT,
                courriel TEXT,
                FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
            )
        """)
        
        # Table produits
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produits (
                nom TEXT PRIMARY KEY,
                prix_base REAL,
                devise_base TEXT CHECK(devise_base IN ('USD', 'CAD')),
                prix_transport REAL,
                devise_transport TEXT CHECK(devise_transport IN ('USD', 'CAD')),
                type_produit TEXT CHECK(type_produit IN ('RATIO', 'COUVERTURE')),
                couverture_1_pouce REAL
            )
        """)
        
        # Table produit_ratios (nouveau)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produit_ratios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produit_nom TEXT NOT NULL,
                ratio REAL NOT NULL,
                est_defaut BOOLEAN DEFAULT 0,
                FOREIGN KEY (produit_nom) REFERENCES produits(nom) ON DELETE CASCADE
            )
        """)
        
        # Table soumissions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_number TEXT UNIQUE,
                year INTEGER,
                sequence INTEGER,
                client_name TEXT,
                etat TEXT CHECK(etat IN ('brouillon', 'finalisé'))
            )
        """)
        
        # Nouvelle table sable
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sable (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transporteur TEXT NOT NULL,
                camion INTEGER NOT NULL,
                ville TEXT NOT NULL,
                prix_voyage REAL NOT NULL,
                prix_sable REAL NOT NULL
            )
        """)
        
        # Table main_doeuvre
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS main_doeuvre (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metier TEXT NOT NULL UNIQUE,
                taux_horaire_chantier REAL NOT NULL,
                taux_horaire_transport REAL NOT NULL
            )
        """)
        
        conn.commit()
