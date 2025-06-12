
import webbrowser

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