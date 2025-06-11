import pandas as pd
from datetime import datetime
import json
with open("param.json", "r", encoding="utf-8") as f:
    contrats = json.load(f)



def fin_mois(date_str): # renvoie la date de fin du mois
    date = pd.to_datetime(date_str, dayfirst=True) #convertit la date en objet
    return (date + pd.offsets.MonthEnd(0)) # MonthEnd(0) fais qu'on tombe sur le dernier jour du mois

'''calcul de l'age exact'''
def age_exact(date_naissance_str, date_rente_str):

    # Conversion des dates
    date_naissance = pd.to_datetime(date_naissance_str, dayfirst=True)
    date_reference = pd.to_datetime(date_rente_str, dayfirst=True)

    # Calcul de la fraction du mois de naissance
    fraction_mois_naissance = round((date_naissance.days_in_month - date_naissance.day + 1) / date_naissance.days_in_month, 3)

    # Calcul du nombre de mois écoulés
    date_ref_moins1 = date_reference - pd.DateOffset(months=1)
    mois_entiers = (date_ref_moins1.year - date_naissance.year) * 12 + (date_ref_moins1.month - date_naissance.month)

    # Calcul de la fraction du mois actuel
    fraction_mois_actuel = round((date_reference.day - 1) / date_reference.days_in_month, 3)

    # Calcul final
    return round((fraction_mois_naissance + mois_entiers + fraction_mois_actuel) / 12, 3)

'''calcul de l age du conjoint ou du rentier'''
def calcul_age_participant(contrats, personne="rentier"):
    personnes = {"rentier": "Date de naissance", "conjoint": "Naissance conjoint"}

    # Vérification du paramètre personne
    if personne not in personnes:
        raise ValueError("Le paramètre 'personne' doit être 'rentier' ou 'conjoint'.")

    # Conversion des dates
    date_naissance = pd.to_datetime(contrats[personnes[personne]], dayfirst=True)
    date_debut = pd.to_datetime(contrats["Date d effet de la rente"], dayfirst=True)

    # Calcul de l'âge exact
    age_exact_val = age_exact(date_naissance, date_debut)
    age_entier = int(age_exact_val)

    # Vérification de la validité de l'année de naissance
    annee_naissance = date_naissance.year
    if not (1900 <= annee_naissance <= 2005):
        raise ValueError(f"Année de naissance invalide pour {personne} : {annee_naissance}")

    return age_exact_val, age_entier, age_exact_val - age_entier, annee_naissance