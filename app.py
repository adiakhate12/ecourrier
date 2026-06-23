import logging
import os
import sqlite3
from flask import Flask, jsonify, redirect, render_template, request, session
import init_db 

# Configuration
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dgb_mfb_secure_session_key_2026")
DB_NAME = "ecourrier.db"

# --- AJOUT CRUCIAL : La fonction manquante ---
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
# ---------------------------------------------

# Initialisation automatique de la base au démarrage
def initialize_app():
    if not os.path.exists(DB_NAME):
        logging.info("Base de données non trouvée, initialisation...")
        init_db.init_db()
    else:
        logging.info("Base de données déjà existante.")

initialize_app()

# --- ROUTES ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        matricule = request.form.get("matricule")
        password = request.form.get("password")
        conn = get_db_connection() # Maintenant elle est trouvée !
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

@app.route("/agent")
def espace_agent():
    if not session.get("logged_in") or session.get("role") != "Solde": return redirect("/login")
    conn = get_db_connection()
    dossiers = conn.execute("SELECT * FROM Dossier").fetchall()
    agents = conn.execute("SELECT * FROM Utilisateur WHERE role != 'Usager'").fetchall()
    conn.close()
    return render_template("agent.html", dossiers=dossiers, agents=agents)

# ... (tes autres routes restent identiques)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)