@echo off
curl "https://www.duckdns.org/update?domains=pbl-beton.duckdns.org&token=4c3abc80-de2c-4882-a7a6-0b584371f798&ip="
echo Mise à jour DuckDNS effectuée à %date% %time% >> C:\gestion_clients\duckdns_log.txt