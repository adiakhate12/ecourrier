<<<<<<< HEAD
import os
import sqlite3
import logging
from flask import Flask, jsonify, redirect, render_template, request, session
import qrcode
from werkzeug.utils import secure_filename

# Configuration du logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Utilise une variable d'environnement pour la sécurité (recommandé)
app.secret_key = os.environ.get("SECRET_KEY", "dgb_mfb_secure_session_key_2026")

# Configuration des dossiers
DB_NAME = "ecourrier.db"
UPLOAD_FOLDER = os.path.join("static", "uploads")
QR_CODE_DIR = os.path.join("static", "qrcodes")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_CODE_DIR, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# --- ROUTES ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/depot")
def depot():
    return render_template("depot.html")

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
            if user["role"] == "Solde": return redirect("/agent")
            if user["role"] == "Courrier": return redirect("/agent/courrier")
            if user["role"] == "CallCenter": return redirect("/agent/callcenter")
            return redirect("/")
        return render_template("login.html", error="Identifiants incorrects.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# --- API & AGENTS (Raccourcis pour l'exemple) ---
@app.route("/agent")
def espace_agent():
    if not session.get("logged_in") or session.get("role") != "Solde": return redirect("/login")
    return render_template("agent.html")

# --- LANCEMENT SERVEUR ---
if __name__ == "__main__":
    # Render définit dynamiquement le port via la variable PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
=======
import logging
import os
import sqlite3
import uuid
from datetime import datetime
from flask import Flask, jsonify, redirect, render_template, request, session
import qrcode
from werkzeug.utils import secure_filename

# Configuration
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
app.secret_key = "dgb_mfb_secure_session_key_2026"
DB_NAME = "ecourrier.db"

UPLOAD_FOLDER = os.path.join("static", "uploads")
QR_CODE_DIR = os.path.join("static", "qrcodes")
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_CODE_DIR, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# --- ROUTES DE NAVIGATION ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/depot")
def depot():
    return render_template("depot.html")

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
            if user["role"] == "Solde": return redirect("/agent")
            if user["role"] == "Courrier": return redirect("/agent/courrier")
            if user["role"] == "CallCenter": return redirect("/agent/callcenter")
            return redirect("/")
        return render_template("login.html", error="Identifiants incorrects.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# --- VUES AGENTS & GESTION ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        matricule = request.form.get("matricule")
        password = request.form.get("password")
        nom = request.form.get("nom_complet")
        role = request.form.get("role")
        if role in ['Solde', 'Courrier', 'CallCenter']:
            if not session.get("logged_in") or session.get("role") != "Solde":
                return "Accès refusé", 403
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO Utilisateur (matricule, mot_de_passe, nom_complet, role) VALUES (?, ?, ?, ?)",
                         (matricule, password, nom, role))
            conn.commit()
            return redirect("/agent")
        except sqlite3.IntegrityError:
            return "Erreur : Ce matricule existe déjà.", 400
        finally:
            conn.close()
    return render_template("register.html")

@app.route("/agent")
def espace_agent():
    if not session.get("logged_in") or session.get("role") != "Solde": return redirect("/login")
    conn = get_db_connection()
    dossiers = conn.execute("SELECT d.*, doc.chemin AS chemin_doc FROM Dossier d LEFT JOIN Document doc ON d.id_dos = doc.id_dos ORDER BY d.id_dos DESC").fetchall()
    agents = conn.execute("SELECT * FROM Utilisateur WHERE role != 'Usager'").fetchall()
    conn.close()
    return render_template("agent.html", dossiers=dossiers, agents=agents)

@app.route("/agent/courrier")
def vue_agent_courrier():
    if not session.get("logged_in") or session.get("role") not in ["Courrier", "Solde"]: return redirect("/login")
    return render_template("agent_courrier.html")

@app.route("/agent/callcenter")
def vue_agent_callcenter():
    if not session.get("logged_in") or session.get("role") not in ["CallCenter", "Solde"]: return redirect("/login")
    return render_template("agent_call.html")

# --- API CORE ---
@app.route("/api/ecourrier/dossier/deposer", methods=["POST"])
def deposer_dossier():
    # Ton code de dépôt complet ici...
    return jsonify({"message": "Dossier enregistré"}), 201

if __name__ == "__main__":
    app.run(debug=True, port=5000)
>>>>>>> 17c4e1a30e0059df1894a570e877a0aa65c0bbc5
