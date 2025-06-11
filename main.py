import time

start_time = time.time() 


from attendus import ax
from attendus import rente_brute
from attendus import rente_brute_periodique
from attendus import calcul_rente_nette
import json
with open("param.json", "r", encoding="utf-8") as f:
    contrats = json.load(f)
from calcul_LX_LY_colonne import get_LXc_rentier
LXc_rentier_main = get_LXc_rentier()


'''calcul des attendus'''
resultat_ax = ax(LXc_rentier_main, contrats['Terme'], contrats['fractionnement'])
rente_brute_resultat = rente_brute(contrats, resultat_ax)
rente_brute_periodique_resultat = rente_brute_periodique(rente_brute_resultat, contrats["fractionnement"])
rente_nette = calcul_rente_nette(rente_brute_periodique_resultat, contrats["frais sur arrerage"])


'''affichage des resultats'''
print("Résultat attendu :", resultat_ax)
print("Rente brute :", rente_brute_resultat)
print("Rente brute périodique :", rente_brute_periodique_resultat)
print("Rente nette :", rente_nette)

end_time = time.time()  # Fin du chrono

print("Temps d'exécution :", end_time - start_time, "secondes")