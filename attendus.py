from calcul_LX_LY_colonne import get_LXc_rentier
import json
import numpy as np
with open("param.json", "r", encoding="utf-8") as f:
    contrats = json.load(f)

LXc_rentier_main = get_LXc_rentier()


'''calcul des ax'''
def ax(LXc_rentier, terme, fractionnement):
    if terme not in ["Echu", "Avance"]:
        raise ValueError("Le paramètre 'terme' doit être 'Echu' ou 'Avance'.")
    somme_valeurs = (
        LXc_rentier["at_bis"].iloc[1:].sum()  # Exclut le premier élément si 'Echu'
        if terme == "Echu"
        else LXc_rentier["at_bis"].sum())
    
    return somme_valeurs / fractionnement

# Application 
resultat_ax = ax(LXc_rentier_main, contrats['Terme'], contrats['fractionnement'])

# Affichage du résultat
#print("Résultat attendu :", resultat_ax)

'''calcul de la rente brute'''
def rente_brute(contrats, resultat_ax):
    try:
        return np.where(resultat_ax != 0, contrats["CC"] / resultat_ax, 0)
    except ZeroDivisionError:
        print("⚠️ Attention : `resultat_ax` est à zéro. Retourne 0 par précaution.")
        return 0

# Application
rente_brute_resultat = rente_brute(contrats, resultat_ax)

# Affichage des résultats
#print("Rente brute :", rente_brute_resultat)

'''calcul rente brute periodique'''
def rente_brute_periodique(rente_brute_resultat, fractionnement):
    return rente_brute_resultat / fractionnement if fractionnement != 0 else 0  # Évite la division par zéro

# Application
rente_brute_periodique_resultat = rente_brute_periodique(rente_brute_resultat, contrats["fractionnement"])

# Affichage du résultat
#print("Rente brute périodique :", rente_brute_periodique)

'''calcul de la rente nette'''
def calcul_rente_nette(rente_brute_periodique_resultat, frais_sur_arrerage):
    return rente_brute_periodique_resultat / (1 + frais_sur_arrerage)

# Application 
rente_nette = calcul_rente_nette(rente_brute_periodique_resultat, contrats["frais sur arrerage"])

# Affichage du résultat
#print("Rente nette :", rente_nette)
