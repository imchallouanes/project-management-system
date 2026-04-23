import sqlite3

def create_db():
    conn = sqlite3.connect("gestion_nb.db")
    cursor = conn.cursor()
    
    # --- TABLE FACTURES ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS factures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client TEXT,
            conditions TEXT,
            date TEXT,
            total REAL,
            objet TEXT,
            proforma TEXT
        )
    """)
    
    # --- TABLE LIGNES FACTURE ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lignes_facture (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            facture_id INTEGER,
            article TEXT,
            unite TEXT,
            quantite REAL,
            prix_u REAL,
            total_ligne REAL,
            FOREIGN KEY(facture_id) REFERENCES factures(id)
        )
    """)

    # --- TABLE PROJETS ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            facture_id INTEGER,
            nom_projet TEXT,
            client TEXT,
            total REAL,
            duree TEXT,
            statut TEXT DEFAULT 'En cours',
            documents TEXT, 
            date_creation TEXT,
            FOREIGN KEY(facture_id) REFERENCES factures(id)
        )
    """)

    # --- TABLE RH (EMPLOYÉS) ---
    # On crée la table de base
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            poste TEXT,
            salaire_base REAL DEFAULT 0
        )
    """)

    # --- PATCH : Ajout des colonnes manquantes si la table existait déjà ---
    # Cette partie vérifie si 'photo' et 'date_entree' existent, sinon elle les ajoute
    cursor.execute("PRAGMA table_info(employes)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if "photo" not in columns:
        cursor.execute("ALTER TABLE employes ADD COLUMN photo TEXT")
        print("Colonne 'photo' ajoutée.")
    
    if "date_entree" not in columns:
        cursor.execute("ALTER TABLE employes ADD COLUMN date_entree TEXT")
        print("Colonne 'date_entree' ajoutée.")

    # --- TABLE POINTAGE ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pointage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employe_id INTEGER,
            date TEXT,
            heure_entree TEXT,
            heure_sortie TEXT,
            etat TEXT, 
            frais_mission REAL DEFAULT 0,
            prime REAL DEFAULT 0,
            acompte REAL DEFAULT 0,
            commentaire TEXT,
            FOREIGN KEY(employe_id) REFERENCES employes(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("Base de données initialisée avec succès.")

if __name__ == "__main__":
    create_db()