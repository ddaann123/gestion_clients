@echo off
cd C:\gestion_clients
start /B C:\Users\danle\AppData\Local\Programs\Python\Python313\pythonw.exe formulaire_chantier.py
echo Script Flask exécuté à %date% %time% >> C:\Users\danle\flask_log.txt

