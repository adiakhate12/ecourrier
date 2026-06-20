-- ==========================================
-- SCRIPT DE CRÉATION DE LA BASE eCOURRIER (SQLite)
-- Ministère des Finances et du Budget (DGB)
-- ==========================================

CREATE TABLE IF NOT EXISTS Statut (
    id_statut INTEGER PRIMARY KEY AUTOINCREMENT,
    libelle VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS Utilisateur (
    id_user INTEGER PRIMARY KEY AUTOINCREMENT,
    nom VARCHAR(150) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    mot_de_passe VARCHAR(255) NOT NULL,
    telephone VARCHAR(20),
    role VARCHAR(50) NOT NULL, -- 'Usager', 'Agent Courrier', 'Agent Traitant'
    statut VARCHAR(30) DEFAULT 'Actif',
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Dossier (
    id_dos INTEGER PRIMARY KEY AUTOINCREMENT,
    num_dos VARCHAR(50) NOT NULL UNIQUE,
    nom_dos VARCHAR(150) NOT NULL,
    description TEXT,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_modification DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_user_depose INTEGER NOT NULL,
    id_statut_actuel INTEGER NOT NULL,
    qr_code_path VARCHAR(255),
    FOREIGN KEY (id_user_depose) REFERENCES Utilisateur(id_user),
    FOREIGN KEY (id_statut_actuel) REFERENCES Statut(id_statut)
);

CREATE TABLE IF NOT EXISTS Traitement (
    id_traitement INTEGER PRIMARY KEY AUTOINCREMENT,
    date_traitement DATETIME DEFAULT CURRENT_TIMESTAMP,
    commentaire TEXT,
    action VARCHAR(100) NOT NULL,
    id_dos INTEGER NOT NULL,
    id_user_agent INTEGER NOT NULL,
    id_statut_cible INTEGER NOT NULL,
    FOREIGN KEY (id_dos) REFERENCES Dossier(id_dos) ON DELETE CASCADE,
    FOREIGN KEY (id_user_agent) REFERENCES Utilisateur(id_user),
    FOREIGN KEY (id_statut_cible) REFERENCES Statut(id_statut)
);

CREATE TABLE IF NOT EXISTS Document (
    id_document INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_fichier VARCHAR(255) NOT NULL,
    type VARCHAR(50),
    chemin VARCHAR(255) NOT NULL,
    taille INTEGER,
    date_upload DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_dos INTEGER NOT NULL,
    FOREIGN KEY (id_dos) REFERENCES Dossier(id_dos) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Notification (
    id_notification INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT NOT NULL,
    date_envoi DATETIME DEFAULT CURRENT_TIMESTAMP,
    lu BOOLEAN DEFAULT 0,
    id_user INTEGER NOT NULL,
    id_dos INTEGER NOT NULL,
    FOREIGN KEY (id_user) REFERENCES Utilisateur(id_user) ON DELETE CASCADE,
    FOREIGN KEY (id_dos) REFERENCES Dossier(id_dos) ON DELETE CASCADE
);

-- Insertion des statuts initiaux du workflow
INSERT OR IGNORE INTO Statut (id_statut, libelle, description) VALUES
(1, 'En attente', 'Dossier déposé par l''usager, en attente de vérification.'),
(2, 'Vérifié', 'Dossier validé par l''agent courrier et attribué.'),
(3, 'Rejeté', 'Dossier incomplet ou contenant des doublons.'),
(4, 'Traité', 'Dossier finalisé et validé (prêt pour paiement).');