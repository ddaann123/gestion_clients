
import webbrowser
import math
from fractions import Fraction

def calculate_distance(ville):
    if not ville:
        return
    # Construire l'URL pour Google Maps avec l'origine (ville entrée) et la destination (Victoriaville)
    origin = ville.replace(" ", "+")  # Remplacer les espaces par des "+"
    destination = "Victoriaville,+QC,+Canada"
    url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}"
    webbrowser.open(url)


# c:\gestion_clients\gui\submission_calcs.py
def calculate_surface_per_mob(total_surface, mobilizations):
    try:
        if mobilizations == 0:
            return "Erreur"
        return f"{total_surface / mobilizations:.1f}"
    except ValueError:
        return "Erreur"
    

def get_truck_tonnages(db_manager, transporter):
    """Retourne une liste triée des tonnages (camion) pour un transporteur donné."""
    sable_data = db_manager.get_sable()
    truck_tonnages = sorted(set(row[2] for row in sable_data if row[1] == transporter))  # Colonne 2 est camion
    return truck_tonnages if truck_tonnages else []

def calculate_prix_par_sac(product_name, usd_cad_rate, db_manager):
    """
    Calcule le prix par sac en CAD pour un produit donné.
    Formule : (prix_base + prix_transport), converti en CAD si nécessaire.
    """
    try:
        usd_cad_rate = float(usd_cad_rate)
        produits = db_manager.get_produit_details()
        produit = next((p for p in produits if p[0] == product_name), None)
        if not produit:
            return "0.00"

        nom, prix_base, devise_base, prix_transport, devise_transport, _, _ = produit

        # Conversion en CAD
        prix_base_cad = prix_base * usd_cad_rate if devise_base == "USD" else prix_base
        prix_transport_cad = prix_transport * usd_cad_rate if devise_transport == "USD" else prix_transport

        total = prix_base_cad + prix_transport_cad
        return f"{total:.2f}"
    except Exception:
        return "Erreur"



def calculate_total_sacs(superficie, epaisseur_pouces, produit_nom, ratio_str, db_manager):
    try:
        

        superficie = float(superficie)
        epaisseur_str = epaisseur_pouces.replace('"', '').replace(',', '.').strip()

        # Traitement robuste de l'épaisseur
        if "-" in epaisseur_str:
            parts = epaisseur_str.split("-")
            if len(parts) == 2:
                epaisseur = float(parts[0]) + float(Fraction(parts[1]))
            else:
                epaisseur = float(epaisseur_str)
        else:
            try:
                epaisseur = float(epaisseur_str)
            except:
                epaisseur = float(Fraction(epaisseur_str))

        

        produits = db_manager.get_produit_details()
        produit = next((p for p in produits if p[0] == produit_nom), None)
        if not produit:
            
            return "0"

        type_produit = produit[5]
        couverture_1_pouce = produit[6]
        

        if type_produit == "COUVERTURE":
            if not couverture_1_pouce or couverture_1_pouce <= 0:
                
                return "Erreur"
            sacs = math.ceil(superficie * (epaisseur / 1.0) / couverture_1_pouce)
            
            return str(sacs)

        else:  # RATIO
            if not ratio_str:
                
                return "Erreur"

            try:
                if ":" in ratio_str:
                    parts = ratio_str.split(":")
                    ratio_num = float(parts[0]) / float(parts[1])
                else:
                    ratio_num = float(ratio_str)
                if ratio_num <= 0:
                    
                    return "Erreur"
            except Exception as e:
                
                return "Erreur"

            couverture = (ratio_num + 0.54) / (epaisseur / 12)
            if couverture <= 0:
                
                return "Erreur"
            sacs = math.ceil(superficie / couverture)
            
            return str(sacs)

    except Exception as e:
        
        return "Erreur"


def calculate_prix_total_sacs(prix_par_sac, nb_sacs):
    try:
        prix = float(prix_par_sac)
        sacs = float(nb_sacs)
        total = prix * sacs
        return f"{total:.2f}"
    except Exception as e:
        
        return "Erreur"



def calculer_quantite_sable(nb_sacs_str, ratio_str):
    try:
        if not nb_sacs_str or not ratio_str:
            
            return "0"

        nb_sacs = int(nb_sacs_str)
        if nb_sacs <= 0:
            
            return "0"

        if ":" in ratio_str:
            parts = ratio_str.split(":")
            ratio = float(parts[0]) / float(parts[1])
        else:
            ratio = float(ratio_str)

        if ratio <= 0:
            
            return "0"

        sable_tm = math.ceil(nb_sacs * ratio * 0.04994)
        
        return str(sable_tm)

    except Exception as e:
        
        return "0"


def calculer_nombre_voyages_sable(sable_tm_str, tonnage_camion_str):
    try:
        sable_tm = float(sable_tm_str.replace(",", "."))
        tonnage_camion = float(tonnage_camion_str.replace(",", "."))

        if tonnage_camion <= 0:
            raise ValueError("Tonnage camion invalide")

        voyages = math.ceil(sable_tm / tonnage_camion)
        
        return str(voyages)
    except Exception as e:
        
        return ""

def calculer_prix_total_sable(db_manager, sable_str, voyages_str, transporteur, type_camion):

    

    try:
        if not sable_str or not voyages_str or not transporteur or not type_camion:
            return "0.00"

        sable = float(sable_str)
        voyages = int(voyages_str)

        # Extraire les données de la table 'sable'
        sable_data = db_manager.get_sable()
        prix_voyage = 0
        prix_sable = 0

        for row in sable_data:
            
            if row[1] == transporteur and row[2] == int(type_camion):
                prix_voyage = float(row[4])  # Prix par voyage
                prix_sable = float(row[5])   # Prix par tonne
                break

        total = voyages * prix_voyage + sable * prix_sable
        
        return f"{total:.2f}"

    except Exception as e:
        
        return "Erreur"

import math

def calculer_heures_chantier(superficie_str):
    try:
        superficie = float(superficie_str.replace(",", ""))
        if superficie <= 0:
            return "0"
        heures = (superficie / ((453.68 * math.log(superficie) - 2486.6)))+1
        heures_arrondies = max(4, math.ceil(heures))
        return str(heures_arrondies)
    except Exception:
        return "0"

import math

def calculer_heures_transport(distance_str):
    try:
        
        distance = float(distance_str.replace(",", ""))
        if distance <= 0:
            return "0"
        heures = math.ceil((distance * 2) / 90)
        
        return str(heures)
    except Exception as e:
        
        return "0"


def calculer_prix_total_machinerie(db_manager, type_machinerie, heures_chantier, heures_transport):
    try:


        machinerie_data = db_manager.get_machinerie()
        taux_horaire = next((float(row[2]) for row in machinerie_data if row[1] == type_machinerie), None)

        

        if taux_horaire is None:
            return "0.00"

        heures_chantier = float(heures_chantier.replace(",", ".") or 0)
        heures_transport = float(heures_transport.replace(",", ".") or 0)
        heures_total = heures_chantier + heures_transport

        

        total = taux_horaire * heures_total
        

        return f"{total:.2f}"

    except Exception as e:
        print(f"[ERREUR] calculer_prix_total_machinerie : {e}")
        return "Erreur"

def calculer_prix_total_pension(db_manager, type_pension, nombre_hommes):
    try:


        if not type_pension or not nombre_hommes:
            
            return "0.00"

        pensions = db_manager.get_pensions()
        

        montant_journalier = next(
            (float(row[2]) for row in pensions if row[1] == type_pension), None
        )
        

        if montant_journalier is None:
            
            return "0.00"

        nombre = int(nombre_hommes)
        total = nombre * montant_journalier
        
        return f"{total:.2f}"

    except Exception as e:
        
        return "Erreur"



def valider_entree_numerique(widget, value, champ_nom="Valeur"):
    try:
        float(value.replace('$', '').replace(',', '').strip())
        widget.config(background="white")
        return True
    except:
        widget.config(background="salmon")
        return False


