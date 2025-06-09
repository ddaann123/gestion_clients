# calculations/submission_calcs.py
import math
import logging

logging.basicConfig(level=logging.DEBUG)

def parse_epaisseur(epaisseur):
    """Convertit une épaisseur (ex. '1-1/2"') en valeur numérique en pouces."""
    epaisseur_clean = epaisseur.replace('"', '').replace(' ', '')
    if '-' in epaisseur_clean:
        parts = epaisseur_clean.split('-')
        num = float(parts[0])
        if '/' in parts[1]:
            frac = parts[1].split('/')
            num += float(frac[0]) / float(frac[1])
        return num
    elif '/' in epaisseur_clean:
        parts = epaisseur_clean.split('/')
        return float(parts[0]) / float(parts[1])
    return float(epaisseur_clean)

def calculer_quantite_sacs(superficie, produit, epaisseur, ratio, db_manager):
    """Calcule le nombre de sacs nécessaires pour une soumission."""
    try:
        superficie = float(superficie.replace(",", "").strip())
        if superficie <= 0:
            return 0, 0, 0, 0, 0

        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT couverture_1_pouce, type_produit FROM produits WHERE nom = ?", (produit,))
            data = cursor.fetchone()
            if not data:
                raise ValueError(f"Produit '{produit}' non trouvé")

            couverture, type_produit = data
            epaisseur_num = parse_epaisseur(epaisseur)

            if type_produit == "COUVERTURE":
                sacs = math.ceil(superficie * (epaisseur_num / 1.0) / couverture)
                sable_tm = 0
            else:
                ratio_num = float(ratio.split(":")[0]) / float(ratio.split(":")[1])
                couverture = (ratio_num + 0.54) / (epaisseur_num / 12)
                sacs = math.ceil(superficie / couverture)
                sable_tm = sacs * ratio_num * 0.04994

            voyages = math.ceil(sable_tm / 10) if sable_tm > 0 else 0
            cursor.execute("SELECT prix_tonne FROM sable WHERE fournisseur = ?", ("Sablière A",))
            prix_sable_data = cursor.fetchone()
            prix_sable = (prix_sable_data[0] * sable_tm) if prix_sable_data and sable_tm > 0 else 0
            cursor.execute("SELECT prix_voyage FROM transport WHERE transporteur = ?", ("JEAN-YVES COTE",))
            prix_transport_data = cursor.fetchone()
            prix_transport = (prix_transport_data[0] * voyages) if prix_transport_data and voyages > 0 else 0

            logging.debug(f"Calcul sacs : superficie={superficie}, produit={produit}, sacs={sacs}")
            return sacs, sable_tm, voyages, prix_sable, prix_transport
    except Exception as e:
        logging.error(f"Erreur calculer_quantite_sacs : {e}")
        return 0, 0, 0, 0, 0