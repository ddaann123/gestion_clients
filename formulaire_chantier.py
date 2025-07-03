from flask import Flask, render_template, request, jsonify
import os
import json
import sqlite3
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__, static_folder="static")

# Chemins absolus
TXT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "donnees_chantier.txt"))
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "database", "clients.db"))

def init_chantiers_reels(db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chantiers_reels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                soumission_reel TEXT,
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
        conn.commit()
        

def get_employe_nom(i):
    employes = {
        1: "KASSIM GOSSELIN",
        2: "ALEX VALOIS",
        3: "KARL",
        4: "ANTHONY ALLAIRE",
        5: "MARC POTHIER",
        6: "NATHAN",
        7: "ANTHONY LABBÉ",
        8: "JONATHAN GRENIER"
    }
    return employes.get(i, f"Employé personnalisé {i}")

EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS", "dlegare@planchersbetonleger.com")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT", "dlegare@planchersbetonleger.com")

def send_email(data):
    
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD or not EMAIL_RECIPIENT:
        print(f"[ERREUR] Configuration email invalide : EMAIL_ADDRESS={EMAIL_ADDRESS}, EMAIL_PASSWORD={'***' if EMAIL_PASSWORD else None}, EMAIL_RECIPIENT={EMAIL_RECIPIENT}")
        return
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_RECIPIENT
    msg['Subject'] = f"Feuille de travail - {data['client_reel']} - {data['date_travaux']}"

    html_body = f"""
    <html>
        <body>
            <h2>Feuille de travail - {data['client_reel']} - {data['date_travaux']}</h2>
            <p><strong>Date des travaux :</strong> {data['date_travaux']}</p>
            <h3>Détails du chantier :</h3>
            <table border="1">
                <tr><td>Client</td><td>{data['client_reel']}</td></tr>
                <tr><td>Adresse</td><td>{data['adresse_reel']}</td></tr>
                <tr><td>Produit</td><td>{data['produit_reel']}</td></tr>
                <tr><td>Produit différent</td><td>{data['produit_diff']}</td></tr>
                <tr><td>Superficie</td><td>{data['superficie_reel']} pi²</td></tr>
                <tr><td>Épaisseur moyenne</td><td>{data['thickness']}</td></tr>
                <tr><td>Nombre de sacs prévus</td><td>{data['nb_sacs_prevus']}</td></tr>
                <tr><td>Sacs utilisés</td><td>{data['sacs_utilises_reel']}</td></tr>
                <tr><td>Transporteur de sable</td><td>{data['sable_transporter_reel']}</td></tr>
                <tr><td>Sable théorique</td><td>{data['sable_total_reel']} tm</td></tr>
                <tr><td>Sable commandé</td><td>{data['sable_commande_reel']} tm</td></tr>
                <tr><td>Surplus de sable</td><td>{data['sable_utilise_reel']} tm</td></tr>
                <tr><td>Type de membrane</td><td>{data['type_membrane']}</td></tr>
                <tr><td>Nombre rouleaux installés</td><td>{data['nb_rouleaux_installes_reel']}</td></tr>
                <tr><td>Installation membrane</td><td>{data['membrane_posee_reel']}</td></tr>
                <tr><td>Marches</td><td>{data['marches_reel']}</td></tr>
                <tr><td>Notes</td><td>{data['notes_reel']}</td></tr>
                <tr><td>Notes bureau</td><td>{data['notes_bureau']}</td></tr>
            </table>
            <h3>Heures de chantier :</h3>
            <table border="1">
                <tr>
                    <th>Employé</th><th>Présence</th><th>Véhicule</th><th>Chauffeur Aller</th><th>Chauffeur Retour</th>
                    <th>Heure Début</th><th>Heure Fin</th><th>Temps Transport</th><th>Heures Entrepôt</th><th>Heures Chantier</th>
                </tr>
                {''.join([f"""
                    <tr>
                        <td>{employe}</td>
                        <td>{'OUI' if info['presence'] == 'on' else 'N/A'}</td>
                        <td>{info['vehicule'] or 'N/A'}</td>
                        <td>{info['chauffeur_aller'] or 'N/A'}</td>
                        <td>{info['chauffeur_retour'] or 'N/A'}</td>
                        <td>{info['heure_debut'] or 'N/A'}</td>
                        <td>{info['heure_fin'] or 'N/A'}</td>
                        <td>{info['temps_transport'] or 'N/A'}</td>
                        <td>{info['heures_entrepot'] or 'N/A'}</td>
                        <td>{calculate_work_hours(info['heure_debut'], info['heure_fin'])}</td>
                    </tr>
                """ for employe, info in data['heures_chantier'].items() if info['heure_debut'] or info['heure_fin']])}
            </table>
        </body>
    </html>
    """

    msg.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"✅ Email envoyé à {EMAIL_RECIPIENT} pour soumission_reel {data['soumission_reel']}")
    except Exception as e:
        print(f"[ERREUR] Échec de l'envoi de l'email : {str(e)}")

def calculate_work_hours(start_time, end_time):
    if not start_time or not end_time:
        return "N/A"
    try:
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        diff = end - start
        hours = diff.total_seconds() / 3600
        return f"{hours:.2f} h"
    except ValueError:
        return "N/A"

@app.route("/")
def formulaire():
    try:
        with open("static/formulaires.json", "r", encoding="utf-8") as f:
            formulaires = json.load(f)
        print(f"[INFO] {len(formulaires)} formulaires chargés depuis formulaires.json")
    except Exception as e:
        print(f"[ERREUR] Impossible de lire formulaires.json : {e}")
        formulaires = []
    
    employes = {
        1: "KASSIM GOSSELIN",
        2: "ALEX VALOIS",
        3: "KARL",
        4: "ANTHONY ALLAIRE",
        5: "MARC POTHIER",
        6: "NATHAN",
        7: "ANTHONY LABBÉ",
        8: "JONATHAN GRENIER"
    }
    
    
    return render_template("formulaire.html", formulaires=formulaires, employes=employes)

@app.route("/submit", methods=["POST"])
def submit():
    

    try:
        data = {
            "soumission_reel": request.form.get("soumission"),
            "client_reel": request.form.get("client"),
            "superficie_reel": request.form.get("superficie"),
            "produit_reel": request.form.get("produit", ""),
            "produit_diff": request.form.get("produit_diff", ""),
            "sable_total_reel": request.form.get("sable_total", ""),
            "sable_transporter_reel": request.form.get("sable_transporter", ""),
            "sable_commande_reel": request.form.get("sable_commande", ""),
            "sacs_utilises_reel": request.form.get("sacs_utilises"),
            "sable_utilise_reel": request.form.get("sable_utilise"),
            "membrane_posee_reel": request.form.get("membrane_posee"),
            "nb_rouleaux_installes_reel": request.form.get("nb_rouleaux_installes"),
            "marches_reel": request.form.get("marches_reel"),
            "notes_reel": request.form.get("notes_chantier"),
            "date_travaux": request.form.get("date_travaux"),
            "adresse_reel": request.form.get("adresse_reel", ""),
            "type_membrane": request.form.get("type_membrane", ""),
            "nb_sacs_prevus": request.form.get("nb_sacs_prevus", ""),
            "thickness": request.form.get("thickness", ""),
            "notes_bureau": request.form.get("notes_bureau", ""),
            "heures_chantier": {},
            "donnees_json": ""
        }

        

        if not data["date_travaux"]:
            with open("static/formulaires.json", "r", encoding="utf-8") as f:
                formulaires = json.load(f)
                for f in formulaires:
                    if f["html"].find(data["soumission_reel"]) != -1:
                        data["date_travaux"] = f["date_travaux"]
                        
                        break
                else:
                    print("[ERREUR] Aucune correspondance trouvée pour soumission_reel dans formulaires.json")

        for i in range(1, 12):
            employe_nom = request.form.get(f"nom_custom_{i}") if i > 8 else get_employe_nom(i)
            if employe_nom:
                data["heures_chantier"][employe_nom] = {
                    "presence": request.form.get(f"presence_{i}"),
                    "vehicule": request.form.get(f"vehicule_{i}"),
                    "chauffeur_aller": request.form.get(f"chauffeur_aller_{i}"),
                    "chauffeur_retour": request.form.get(f"chauffeur_retour_{i}"),
                    "heure_debut": request.form.get(f"heure_debut_{i}"),
                    "heure_fin": request.form.get(f"heure_fin_{i}"),
                    "temps_transport": request.form.get(f"temps_transport_{i}"),
                    "heures_entrepot": request.form.get(f"heures_entrepot_{i}"),
                    "nom_custom": employe_nom if i > 8 else None
                }

        data["donnees_json"] = json.dumps({"heures_chantier": data["heures_chantier"]}, ensure_ascii=False)

        try:
            existing_data = []
            if os.path.exists(TXT_PATH):
                with open(TXT_PATH, "r", encoding="utf-8") as f:
                    try:
                        existing_data = json.load(f)
                        if not isinstance(existing_data, list):
                            
                            existing_data = []
                    except json.JSONDecodeError:
                        
                        existing_data = []
            
            existing_data.append(data)
            
            with open(TXT_PATH, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            print(f"[ERREUR] Impossible d'écrire dans {TXT_PATH} : {e}")

        
        send_email(data)
        

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                init_chantiers_reels(DB_PATH)
                
                columns = [
                    "soumission_reel", "client_reel", "superficie_reel", "produit_reel",
                    "produit_diff", "sable_total_reel", "sable_transporter_reel",
                    "sable_commande_reel", "sacs_utilises_reel", "sable_utilise_reel",
                    "membrane_posee_reel", "nb_rouleaux_installes_reel", "marches_reel",
                    "notes_reel", "date_travaux", "date_soumission", "donnees_json",
                    "adresse_reel", "type_membrane", "nb_sacs_prevus",
                    "thickness", "notes_bureau"
                ]
                values = [
                    data.get("soumission_reel", ""),
                    data.get("client_reel", ""),
                    data.get("superficie_reel", ""),
                    data.get("produit_reel", ""),
                    data.get("produit_diff", ""),
                    data.get("sable_total_reel", ""),
                    data.get("sable_transporter_reel", ""),
                    data.get("sable_commande_reel", ""),
                    data.get("sacs_utilises_reel", ""),
                    data.get("sable_utilise_reel", ""),
                    data.get("membrane_posee_reel", ""),
                    data.get("nb_rouleaux_installes_reel", ""),
                    data.get("marches_reel", ""),
                    data.get("notes_reel", ""),
                    data.get("date_travaux", ""),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    data.get("donnees_json", ""),
                    data.get("adresse_reel", ""),
                    data.get("type_membrane", ""),
                    data.get("nb_sacs_prevus", ""),
                    data.get("thickness", ""),
                    data.get("notes_bureau", "")
                ]
                
                query = f"""
                    INSERT INTO chantiers_reels ({", ".join(columns)})
                    VALUES ({", ".join(["?" for _ in columns])})
                """
                
                cursor.execute(query, values)
                conn.commit()
                
        except Exception as e:
            print(f"[ERREUR] Impossible d'insérer dans la table chantiers_reels : {str(e)}")

        try:
            with open("static/formulaires.json", "r", encoding="utf-8") as f:
                formulaires = json.load(f)
            nouvelle_liste = [f for f in formulaires if f["date_travaux"] != data["date_travaux"]]
            with open("static/formulaires.json", "w", encoding="utf-8") as f:
                json.dump(nouvelle_liste, f, indent=2, ensure_ascii=False)
            print(f"✅ Feuille soumise retirée pour date_travaux : {data['date_travaux']}")
        except Exception as e:
            print(f"[ERREUR] Impossible de mettre à jour formulaires.json : {e}")

        print(f"✅ Formulaire soumis pour date_travaux : {data['date_travaux']}")
        return jsonify({"success": True})
    except Exception as e:
        print(f"[ERREUR] Échec de la soumission : {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)