import sqlite3

DB_NAME = "ecourrier.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Suppression des anciennes tables
    cursor.execute("DROP TABLE IF EXISTS Document")
    cursor.execute("DROP TABLE IF EXISTS Dossier")
    cursor.execute("DROP TABLE IF EXISTS Utilisateur")

    # 1. Nouvelle Table Utilisateur
    cursor.execute("""
        CREATE TABLE Utilisateur (
            matricule TEXT PRIMARY KEY,
            mot_de_passe TEXT NOT NULL,
            nom_complet TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # Insertion des comptes de test
    comptes_test = [
        ("611234/A", "Usager@2026", "Moussa Ndiaye", "Usager"),
        ("ADM/001", "Dgb@2026", "Astou Diakhate", "Solde"),
        ("COU/002", "Courrier@2026", "Agent Courrier Physique", "Courrier"),
        ("CAL/003", "Call@2026", "Agent Call Center", "CallCenter"),
        # Ajout de ton matricule personnel
        ("102224/Z", "DGB_2026_Secure", "Astou Diakhaté", "Solde"),
    ]

    cursor.executemany("""
        INSERT INTO Utilisateur (matricule, mot_de_passe, nom_complet, role)
        VALUES (?, ?, ?, ?)
    """, comptes_test)

    # 2. Table Dossier
    cursor.execute("""
        CREATE TABLE Dossier (
            id_dos INTEGER PRIMARY KEY AUTOINCREMENT,
            num_dos TEXT UNIQUE NOT NULL,
            reference_dossier TEXT NOT NULL,
            matricule_usager TEXT NOT NULL,
            nom_dos TEXT NOT NULL,
            description TEXT,
            type_depot TEXT NOT NULL,
            mail_expediteur TEXT,
            id_statut_actuel INTEGER DEFAULT 1,
            qr_code_path TEXT,
            date_depot TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (matricule_usager) REFERENCES Utilisateur (matricule)
        )
    """)

    # 3. Table Document
    cursor.execute("""
        CREATE TABLE Document (
            id_doc INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_fichier TEXT NOT NULL,
            type TEXT NOT NULL,
            chemin TEXT NOT NULL,
            taille INTEGER,
            id_dos INTEGER,
            FOREIGN KEY (id_dos) REFERENCES Dossier (id_dos) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()
    print("Base de données initialisée avec succès avec ton matricule !")

if __name__ == "__main__":
    init_db()