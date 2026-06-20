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