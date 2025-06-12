
import time
import json
from attendus import ax, rente_brute, rente_brute_periodique, calcul_rente_nette
from calcul_LX_LY_colonne import get_LXc_rentier

# Chronométrage précis
start_time = time.perf_counter()

# Chargement des paramètres de contrats
with open("param.json", "r", encoding="utf-8") as f:
    contrats = json.load(f)

# Initialisation des données
LXc_rentier_main = get_LXc_rentier()

# Calcul des attendus
resultat_ax = ax(LXc_rentier_main, contrats['Terme'], contrats['fractionnement'])
rente_brute_resultat = rente_brute(contrats, resultat_ax)
rente_brute_periodique_resultat = rente_brute_periodique(rente_brute_resultat, contrats["fractionnement"])
rente_nette = calcul_rente_nette(rente_brute_periodique_resultat, contrats["frais sur arrerage"])

# Affichage des résultats
print(f"Résultat attendu : {resultat_ax}")
print(f"Rente brute : {rente_brute_resultat}")
print(f"Rente brute périodique : {rente_brute_periodique_resultat}")
print(f"Rente nette : {rente_nette}")

# Fin du chronométrage
end_time = time.perf_counter()
print(f"Temps d'exécution : {end_time - start_time:.6f} secondes")
