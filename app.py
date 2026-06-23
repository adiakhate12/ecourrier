import logging
import os
import sqlite3
from flask import Flask, jsonify, redirect, render_template, request, session
import init_db  # Importe ton fichier init_db.py

# Configuration
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dgb_mfb_secure_session_key_2026")
DB_NAME = "ecourrier.db"

# Initialisation automatique de la base au démarrage
def initialize_app():
    if not os.path.exists(DB_NAME):
        logging.info("Base de données non trouvée, initialisation...")
        init_db.init_db()
    else:
        logging.info("Base de données déjà existante.")

# Appel de l'initialisation
initialize_app()

# ... reste de ton code (UPLOAD_FOLDER, routes, etc.)
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
    return jsonify({"message": "Dossier enregistré"}), 201

if __name__ == "__main__":
    # Port dynamique pour Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)