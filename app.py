import logging
import uuid
import datetime
import qrcode
from werkzeug.utils import secure_filename
import os
import sqlite3
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dgb_mfb_secure_session_key_2026")

# Configuration des dossiers
DB_NAME = "ecourrier.db"
UPLOAD_FOLDER = 'static/uploads'
QR_FOLDER = 'static/qrcodes'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO)

def init_db():
    """Initialise la base de données et les tables nécessaires au démarrage"""
    conn = sqlite3.connect(DB_NAME)
    # Création de la table Dossier si elle n'existe pas
    conn.execute('''CREATE TABLE IF NOT EXISTS Dossier (
                        id_dos INTEGER PRIMARY KEY AUTOINCREMENT,
                        num_dos TEXT,
                        matricule_usager TEXT,
                        nom_dos TEXT,
                        id_statut_actuel INTEGER,
                        type_depot TEXT,
                        id_user_depose INTEGER
                    )''')
    # Ajoute ici ta table Utilisateur si elle n'est pas déjà créée manuellement
    conn.commit()
    conn.close()
    print("Base de données initialisée.")

# Initialisation au démarrage
init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        matricule = request.form.get("matricule")
        password = request.form.get("password")
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM Utilisateur WHERE matricule = ? AND mot_de_passe = ?", (matricule, password)).fetchone()
        conn.close()
        if user:
            session["logged_in"] = True
            session["matricule"] = user["matricule"]
            session["nom_complet"] = user["nom_complet"]
            session["role"] = user["role"]
            if user["role"] == "Solde": return redirect(url_for('espace_agent_solde'))
            if user["role"] == "Courrier": return redirect(url_for('agent_courrier'))
            if user["role"] == "CallCenter": return redirect(url_for('agent_callcenter'))
            return redirect("/")
        return render_template("login.html", error="Identifiants incorrects.")
    return render_template("login.html")

@app.route("/agent")
def espace_agent_solde():
    if not session.get("logged_in") or session.get("role") != "Solde": return redirect(url_for('login'))
    conn = get_db_connection()
    dossiers = conn.execute("SELECT * FROM Dossier").fetchall()
    agents = conn.execute("SELECT * FROM Utilisateur WHERE role != 'Usager'").fetchall()
    conn.close()
    return render_template("agent.html", dossiers=dossiers, agents=agents)

@app.route("/agent/courrier")
def agent_courrier():
    if not session.get("logged_in") or session.get("role") != "Courrier": return redirect(url_for('login'))
    conn = get_db_connection()
    courriers = conn.execute('SELECT * FROM Dossier').fetchall()
    conn.close()
    return render_template('agent_courrier.html', courriers=courriers)

@app.route("/depot")
def afficher_formulaire():
    return render_template("depot.html")

@app.route("/agent/callcenter")
def agent_callcenter():
    if not session.get("logged_in") or session.get("role") != "CallCenter": return redirect(url_for('login'))
    return render_template("callcenter.html")

@app.route('/update_status/<int:id>', methods=['POST'])
def update_status(id):
    if not session.get("logged_in"): return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('UPDATE Dossier SET id_statut_actuel = ? WHERE id_dos = ?', (2, id))
    conn.commit()
    conn.close()
    return redirect(url_for('agent_courrier'))

@app.route("/api/ecourrier/dossier/deposer", methods=["POST"])
def deposer_dossier():
    matricule = request.form.get("matricule")
    objet = request.form.get("objet")
    type_depot = request.form.get("type_depot")
    fichier = request.files.get('fichier')
    
    if fichier and matricule and objet and type_depot:
        filename = secure_filename(fichier.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        fichier.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
        
        date_str = datetime.datetime.now().strftime("%d/%m/%Y")
        conn = get_db_connection()
        count = conn.execute("SELECT COUNT(*) FROM Dossier").fetchone()[0] + 1
        num_ticket = f"{date_str}-{count:04d}"
        
        qr_file_name = f"{num_ticket.replace('/', '-')}.png"
        qr_path_full = os.path.join(QR_FOLDER, qr_file_name)
        # Utilisation de l'URL publique de ton projet Render
        qr = qrcode.make(f"https://ecourrier.onrender.com/suivi/{num_ticket}")
        qr.save(qr_path_full)
        
        conn.execute(
            "INSERT INTO Dossier (num_dos, matricule_usager, nom_dos, id_statut_actuel, type_depot, id_user_depose) VALUES (?, ?, ?, ?, ?, ?)",
            (num_ticket, matricule, objet, 1, type_depot, 1) 
        )
        conn.commit()
        conn.close()
        
        return render_template("succes.html", ticket=num_ticket, qr_image=qr_file_name)
    
    return "Erreur lors de l'enregistrement.", 400

@app.route("/suivi/<ticket>")
def suivi_dossier(ticket):
    return f"Statut pour {ticket} : En cours de traitement."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)import logging
import uuid
import datetime
import qrcode
from werkzeug.utils import secure_filename
import os
import sqlite3
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dgb_mfb_secure_session_key_2026")

# Configuration des dossiers
DB_NAME = "ecourrier.db"
UPLOAD_FOLDER = 'static/uploads'
QR_FOLDER = 'static/qrcodes'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO)

def init_db():
    """Initialise la base de données et les tables nécessaires au démarrage"""
    conn = sqlite3.connect(DB_NAME)
    # Création de la table Dossier si elle n'existe pas
    conn.execute('''CREATE TABLE IF NOT EXISTS Dossier (
                        id_dos INTEGER PRIMARY KEY AUTOINCREMENT,
                        num_dos TEXT,
                        matricule_usager TEXT,
                        nom_dos TEXT,
                        id_statut_actuel INTEGER,
                        type_depot TEXT,
                        id_user_depose INTEGER
                    )''')
    # Ajoute ici ta table Utilisateur si elle n'est pas déjà créée manuellement
    conn.commit()
    conn.close()
    print("Base de données initialisée.")

# Initialisation au démarrage
init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        matricule = request.form.get("matricule")
        password = request.form.get("password")
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM Utilisateur WHERE matricule = ? AND mot_de_passe = ?", (matricule, password)).fetchone()
        conn.close()
        if user:
            session["logged_in"] = True
            session["matricule"] = user["matricule"]
            session["nom_complet"] = user["nom_complet"]
            session["role"] = user["role"]
            if user["role"] == "Solde": return redirect(url_for('espace_agent_solde'))
            if user["role"] == "Courrier": return redirect(url_for('agent_courrier'))
            if user["role"] == "CallCenter": return redirect(url_for('agent_callcenter'))
            return redirect("/")
        return render_template("login.html", error="Identifiants incorrects.")
    return render_template("login.html")

@app.route("/agent")
def espace_agent_solde():
    if not session.get("logged_in") or session.get("role") != "Solde": return redirect(url_for('login'))
    conn = get_db_connection()
    dossiers = conn.execute("SELECT * FROM Dossier").fetchall()
    agents = conn.execute("SELECT * FROM Utilisateur WHERE role != 'Usager'").fetchall()
    conn.close()
    return render_template("agent.html", dossiers=dossiers, agents=agents)

@app.route("/agent/courrier")
def agent_courrier():
    if not session.get("logged_in") or session.get("role") != "Courrier": return redirect(url_for('login'))
    conn = get_db_connection()
    courriers = conn.execute('SELECT * FROM Dossier').fetchall()
    conn.close()
    return render_template('agent_courrier.html', courriers=courriers)

@app.route("/depot")
def afficher_formulaire():
    return render_template("depot.html")

@app.route("/agent/callcenter")
def agent_callcenter():
    if not session.get("logged_in") or session.get("role") != "CallCenter": return redirect(url_for('login'))
    return render_template("callcenter.html")

@app.route('/update_status/<int:id>', methods=['POST'])
def update_status(id):
    if not session.get("logged_in"): return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('UPDATE Dossier SET id_statut_actuel = ? WHERE id_dos = ?', (2, id))
    conn.commit()
    conn.close()
    return redirect(url_for('agent_courrier'))

@app.route("/api/ecourrier/dossier/deposer", methods=["POST"])
def deposer_dossier():
    matricule = request.form.get("matricule")
    objet = request.form.get("objet")
    type_depot = request.form.get("type_depot")
    fichier = request.files.get('fichier')
    
    if fichier and matricule and objet and type_depot:
        filename = secure_filename(fichier.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        fichier.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
        
        date_str = datetime.datetime.now().strftime("%d/%m/%Y")
        conn = get_db_connection()
        count = conn.execute("SELECT COUNT(*) FROM Dossier").fetchone()[0] + 1
        num_ticket = f"{date_str}-{count:04d}"
        
        qr_file_name = f"{num_ticket.replace('/', '-')}.png"
        qr_path_full = os.path.join(QR_FOLDER, qr_file_name)
        # Utilisation de l'URL publique de ton projet Render
        qr = qrcode.make(f"https://ecourrier.onrender.com/suivi/{num_ticket}")
        qr.save(qr_path_full)
        
        conn.execute(
            "INSERT INTO Dossier (num_dos, matricule_usager, nom_dos, id_statut_actuel, type_depot, id_user_depose) VALUES (?, ?, ?, ?, ?, ?)",
            (num_ticket, matricule, objet, 1, type_depot, 1) 
        )
        conn.commit()
        conn.close()
        
        return render_template("succes.html", ticket=num_ticket, qr_image=qr_file_name)
    
    return "Erreur lors de l'enregistrement.", 400

@app.route("/suivi/<ticket>")
def suivi_dossier(ticket):
    return f"Statut pour {ticket} : En cours de traitement."

# ... (garde tout le reste de ton code jusqu'à la fin de la fonction suivi_dossier)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)