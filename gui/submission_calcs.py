
import webbrowser

def calculate_distance(ville):
    if not ville:
        return
    # Construire l'URL pour Google Maps avec l'origine (ville entrée) et la destination (Victoriaville)
    origin = ville.replace(" ", "+")  # Remplacer les espaces par des "+"
    destination = "Victoriaville,+QC,+Canada"
    url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}"
    webbrowser.open(url)


