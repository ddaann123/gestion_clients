from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json
import sqlite3
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__, static_folder="static")

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

# Fonction globale pour obtenir le nom de l'employé
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

# Configuration email via variables d’environnement
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS", "dlegare@planchersbetonleger.com")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")  # Utilise le mot de passe d’application
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT", "dlegare@planchersbetonleger.com")

def send_email(data):
    print(f"[DEBUG] Début de send_email pour soumission : {data['soumission']}")
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD or not EMAIL_RECIPIENT:
        print(f"[ERREUR] Configuration email invalide : EMAIL_ADDRESS={EMAIL_ADDRESS}, EMAIL_PASSWORD={EMAIL_PASSWORD}, EMAIL_RECIPIENT={EMAIL_RECIPIENT}")
        return
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_RECIPIENT
    msg['Subject'] = f"Feuille de travail - {data['client']} - {data['date_travaux']}"

    # Corps HTML
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ width: 80%; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
            h2 {{ color: #2c3e50; }}
            table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f5f5f5; }}
            .highlight {{ background-color: #ecf0f1; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Feuille de travail - {data['client']} - {data['date_travaux']}</h2>
            <p><strong>Date des travaux :</strong> {data['date_travaux']}</p>
            <h3>Détails du chantier :</h3>
            <ul>
                <li><strong>Client :</strong> {data['client']}</li>
                <li><strong>Adresse :</strong> {data['adresse_reel']}</li>
                <li><strong>Produit :</strong> {data['produit']}</li>
                <li><strong>Produit différent :</strong> {data['produit_diff']}</li>
                <li><strong>Superficie :</strong> {data['superficie']} pi²</li>
                <li><strong>Épaisseur moyenne :</strong> {data['thickness']}</li>
                <li><strong>Nombre de sacs prévus :</strong> {data['nb_sacs_prevus']}</li>
                <li><strong>Sacs utilisés :</strong> {data['sacs_utilises']}</li>
                <li><strong>Transporteur de sable :</strong> {data['sable_transporter']}</li>
                <li><strong>Sable théorique :</strong> {data['sable_total']} tm</li>
                <li><strong>Sable commandé :</strong> {data['sable_commande']} tm</li>
                <li><strong>Surplus de sable :</strong> {data['sable_utilise']} tm</li>
                <li><strong>Type de membrane :</strong> {data['type_membrane']}</li>
                <li><strong>Nombre de rouleaux installés :</strong> {data['nb_rouleaux_installes']}</li>
                <li><strong>Installation membrane :</strong> {data['membrane_posee']}</li>
                <li><strong>Marches :</strong> {data['marches_reel']}</li>
                <li><strong>Notes :</strong> {data['notes']}</li>
                <li><strong>Notes bureau :</strong> {data['notes_bureau']}</li>
            </ul>

            <h3>Heures de chantier :</h3>
            <table>
                <tr>
                    <th>Employé</th>
                    <th>Présence</th>
                    <th>Véhicule</th>
                    <th>Chauffeur Aller</th>
                    <th>Chauffeur Retour</th>
                    <th>Heure Début</th>
                    <th>Heure Fin</th>
                    <th>Temps Transport</th>
                    <th>Heures Entrepôt</th>
                    <th>Heures Chantier</th>
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
                        <td>{calculate_work_hours(info['heure_debut'], info['heure_fin']) if info['heure_debut'] and info['heure_fin'] else 'N/A'}</td>
                    </tr>
                """ for employe, info in data['heures_chantier'].items() if info['heure_debut'] or info['heure_fin']])}
            </table>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_body, 'html'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            print(f"[DEBUG] Tentative de login SMTP avec {EMAIL_ADDRESS}")
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"✅ Email envoyé à {EMAIL_RECIPIENT} pour soumission {data['soumission']}")
    except Exception as e:
        print(f"[ERREUR] Échec de l'envoi de l'email : {str(e)}")

def calculate_work_hours(start_time, end_time):
    if not start_time or not end_time:
        return "N/A"
    try:
        # Convertir les heures au format HH:MM en objets datetime
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        # Calculer la différence
        diff = end - start
        # Retourner en heures et minutes
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
    return render_template("formulaire.html", formulaires=formulaires)

@app.route("/submit", methods=["POST"])
def submit():
    print("Début de la fonction submit")
    try:
        # Récupérer les données du formulaire
        data = {
            "soumission": request.form.get("soumission"),
            "client": request.form.get("client"),
            "superficie": request.form.get("superficie"),
            "produit": request.form.get("produit", ""),
            "produit_diff": request.form.get("produit_diff", ""),
            "sable_total": request.form.get("sable_total", ""),
            "sable_transporter": request.form.get("sable_transporter", ""),
            "sable_commande": request.form.get("sable_commande", ""),
            "sacs_utilises": request.form.get("sacs_utilises"),
            "sable_utilise": request.form.get("sable_utilise"),
            "membrane_posee": request.form.get("membrane_posee"),
            "nb_rouleaux_installes": request.form.get("nb_rouleaux_installes"),
            "marches_reel": request.form.get("marches_reel"),
            "notes": request.form.get("notes_chantier"),
            "date_travaux": request.form.get("date_travaux"),
            "adresse_reel": request.form.get("adresse_reel", ""),
            "type_membrane": request.form.get("type_membrane", ""),
            "nb_sacs_prevus": request.form.get("nb_sacs_prevus", ""),
            "thickness": request.form.get("thickness", ""),
            "notes_bureau": request.form.get("notes_bureau", ""),
            "heures_chantier": {}
        }

        print(f"[DEBUG] Données reçues : {data}")

        # Récupérer les données de la table Heures chantier
        for i in range(1, 12):  # Jusqu'à 11 employés
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

        # Sauvegarde des données dans donnees_chantier.txt
        with open("donnees_chantier.txt", "a", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
            f.write('\n')

        # Envoi de l'email
        print(f"[DEBUG] Appel de send_email avant exécution")
        send_email(data)
        print(f"[DEBUG] Appel de send_email terminé")

        # Sauvegarde dans la base de données
        try:
            with sqlite3.connect("database/clients.db") as conn:
                cursor = conn.cursor()
                init_chantiers_reels("database/clients.db")
                
                chantiers_data = {
                    "soumission_reel": data["soumission"],
                    "client_reel": data["client"],
                    "superficie_reel": data["superficie"],
                    "produit_reel": data["produit"],
                    "produit_diff": data["produit_diff"],
                    "sable_total_reel": data["sable_total"],
                    "sable_transporter_reel": data["sable_transporter"],
                    "sable_commande_reel": data["sable_commande"],
                    "sacs_utilises_reel": data["sacs_utilises"],
                    "sable_utilise_reel": data["sable_utilise"],
                    "membrane_posee_reel": data["membrane_posee"],
                    "nb_rouleaux_installes_reel": data["nb_rouleaux_installes"],
                    "marches_reel": data["marches_reel"],
                    "notes_reel": data["notes"],
                    "date_travaux": data["date_travaux"],
                    "date_soumission": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "donnees_json": json.dumps({"heures_chantier": data["heures_chantier"]}, ensure_ascii=False),
                    "adresse_reel": data["adresse_reel"],
                    "type_membrane": data["type_membrane"],
                    "nb_sacs_prevus": data["nb_sacs_prevus"],
                    "thickness": data["thickness"],
                    "notes_bureau": data["notes_bureau"]
                }
                
                print(f"[DEBUG] Données à insérer : {chantiers_data}")
                columns = [
                    "soumission_reel", "client_reel", "superficie_reel", "produit_reel",
                    "produit_diff", "sable_total_reel", "sable_transporter_reel",
                    "sable_commande_reel", "sacs_utilises_reel", "sable_utilise_reel",
                    "membrane_posee_reel", "nb_rouleaux_installes_reel", "marches_reel",
                    "notes_reel", "date_travaux", "date_soumission", "donnees_json",
                    "adresse_reel", "type_membrane", "nb_sacs_prevus",
                    "thickness", "notes_bureau"
                ]
                values = [chantiers_data.get(col, "") for col in columns]
                
                query = f"""
                    INSERT INTO chantiers_reels ({", ".join(columns)})
                    VALUES ({", ".join(["?" for _ in columns])})
                """
                print(f"[DEBUG] Requête SQL : {query} avec valeurs : {values}")
                cursor.execute(query, values)
                conn.commit()
                print(f"✅ Données insérées dans la table chantiers_reels pour soumission : {data['soumission']}")
        except Exception as e:
            print(f"[ERREUR] Impossible d'insérer dans la table chantiers_reels : {str(e)}")

        # Supprimer le formulaire correspondant dans formulaires.json
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