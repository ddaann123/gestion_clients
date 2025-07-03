import sqlite3
from contextlib import contextmanager

def init_database(db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()


        # Table chantiers_reels
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chantiers_reels (
                soumission_reel TEXT PRIMARY KEY,
                client_reel TEXT,
                superficie_reel TEXT,
                produit_reel TEXT,
                produit_diff TEXT,
                sable_total_reel TEXT,
                sable_transporter_reel TEXT,
                sable_commande_reel TEXT,
                sacs_utilises_reel TEXT,
                sable_utilise_reel TEXT,
                membrane_posee_reel TEXT,
                nb_rouleaux_installes_reel TEXT,
                marches_reel TEXT,
                notes_reel TEXT,
                date_travaux TEXT,
                date_soumission TEXT,
                donnees_json TEXT,
                adresse_reel TEXT,
                type_membrane TEXT,
                nb_sacs_prevus TEXT,
                thickness TEXT,
                notes_bureau TEXT
            )
        """)

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
                submission_number TEXT NOT NULL,
                revision INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,  -- 1 = active, 0 = ancienne révision
                etat TEXT CHECK(etat IN ('brouillon', 'finalisé')) NOT NULL,

                year INTEGER,
                sequence INTEGER,

                date_submission TEXT,
                client_name TEXT,
                contact TEXT,
                projet TEXT,
                ville TEXT,
                distance TEXT,

                area TEXT,
                product TEXT,
                ratio TEXT,
                usd_cad_rate TEXT,
                thickness TEXT,
                subfloor TEXT,
                membrane TEXT,
                pose_membrane TEXT,

                sealant TEXT,
                prix_par_sac TEXT,
                total_sacs TEXT,
                prix_total_sacs TEXT,
                sable_total TEXT,
                voyages_sable TEXT,
                prix_total_sable TEXT,
                mobilisations TEXT,
                surface_per_mob TEXT,

                type_main TEXT,
                type_pension TEXT,
                type_machinerie TEXT,
                nb_hommes TEXT,
                heures_chantier TEXT,
                heures_transport TEXT,
                prix_total_pension TEXT,
                prix_total_machinerie TEXT,
                prix_total_heures_chantier TEXT,
                prix_total_heures_transport TEXT,

                ajustement1_nom TEXT,
                ajustement1_valeur TEXT,
                ajustement2_nom TEXT,
                ajustement2_valeur TEXT,
                ajustement3_nom TEXT,
                ajustement3_valeur TEXT,
                reperes_nivellement TEXT,

                sous_total_ajustements TEXT,
                sous_total_fournisseurs TEXT,
                sous_total_main_machinerie TEXT,
                total_prix_coutants TEXT,

                admin_profit_pct TEXT,
                admin_profit_montant TEXT,
                prix_vente_client TEXT,
                prix_unitaire TEXT,
                prix_total_immeuble TEXT,
                prix_pi2_ajuste TEXT,
                prix_total_ajuste TEXT,

                notes_json TEXT,
                surfaces_json TEXT
            )

        """)
        
        migrer_table_submissions_si_necessaire(conn)



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

        # Table pensions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pensions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_pension TEXT NOT NULL CHECK(type_pension IN ('Aucune', 'Standard 120 km', 'Éloigné 300km')),
                montant_par_jour REAL NOT NULL
            )
        """)
        

        # Table machinerie
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS machinerie (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_machinerie TEXT NOT NULL,
                taux_horaire REAL NOT NULL
            )
        """)

        # Table apprets_scellants
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS apprets_scellants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_produit TEXT NOT NULL,
                prix REAL NOT NULL,
                format_litres REAL NOT NULL,
                couverture_pi2 REAL NOT NULL
            )
        """)
        
        # Table membranes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS membranes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                modele_membrane TEXT NOT NULL,
                couverture_pi2 REAL NOT NULL,
                prix_rouleau REAL NOT NULL,
                prix_pi2_membrane REAL NOT NULL,
                pose_pi2_sans_divisions REAL NOT NULL,
                pose_pi2_avec_divisions REAL NOT NULL
            )
        """)

        conn.commit()

def migrer_table_submissions_si_necessaire(conn):
    cursor = conn.cursor()

    # Liste des colonnes attendues (nom: définition SQL si absente)
    colonnes_attendues = {
        "revision": "ALTER TABLE submissions ADD COLUMN revision INTEGER DEFAULT 0",
        "is_active": "ALTER TABLE submissions ADD COLUMN is_active BOOLEAN DEFAULT 1",
        "sequence": "ALTER TABLE submissions ADD COLUMN sequence INTEGER",
        "notes_json": "ALTER TABLE submissions ADD COLUMN notes_json TEXT",
        "surfaces_json": "ALTER TABLE submissions ADD COLUMN surfaces_json TEXT",
        "sable_transporter": "ALTER TABLE submissions ADD COLUMN sable_transporter TEXT",
        "truck_tonnage": "ALTER TABLE submissions ADD COLUMN truck_tonnage TEXT",
        "transport_sector": "ALTER TABLE submissions ADD COLUMN transport_sector TEXT"
    }

    # Obtenir les colonnes existantes
    cursor.execute("PRAGMA table_info(submissions)")
    colonnes_existantes = {row[1] for row in cursor.fetchall()}

    # Ajouter les colonnes manquantes
    for colonne, commande_sql in colonnes_attendues.items():
        if colonne not in colonnes_existantes:
            print(f"[MIGRATION] Ajout de la colonne manquante : {colonne}")
            cursor.execute(commande_sql)

    conn.commit()

