import pandas as pd
from datetime import datetime
import json
with open("param.json", "r", encoding="utf-8") as f:
    contrats = json.load(f)



def fin_mois(date_str): # renvoie la date de fin du mois
    date = pd.to_datetime(date_str, dayfirst=True) #convertit la date en objet
    return (date + pd.offsets.MonthEnd(0)).date() # MonthEnd(0) fais qu'on tombe sur le dernier jour du mois



def age_exact(date_naissance_str, date_rente_str):
    #conversion des chaines en dates
    date_naissance = pd.to_datetime(date_naissance_str, dayfirst=True)
    date_reference = pd.to_datetime(date_rente_str, dayfirst=True)
    
    #Fraction du mois de naissance
    fin_mois_naissance = fin_mois(date_naissance).day
    fraction_mois_naissance = round((fin_mois_naissance- date_naissance.day + 1) / fin_mois_naissance, 3)

    #nombre de mois entiers
    date_ref_moins1 = fin_mois(date_reference - pd.DateOffset(months=1))
    mois_entiers = (date_ref_moins1.year - date_naissance.year) * 12 + (date_ref_moins1.month - date_naissance.month)

    #fraction du mois de la date de reference (calcul du nombre de jour dans les mois non entier)
    jour_du_mois_ref = date_reference.day
    jours_dans_mois_ref = fin_mois(date_reference).day
    fraction_mois_actuel = round((jour_du_mois_ref - 1) / jours_dans_mois_ref, 3)

    #total âge exact en années
    age_exact_par_calcul = round((fraction_mois_naissance + mois_entiers + fraction_mois_actuel) / 12, 3)
    return age_exact_par_calcul



def calcul_age_participant(contrats, personne="rentier"):
    #choix de la personne reniter ou conjoint
    if personne == "rentier":
        cle_naissance = "Date de naissance"
    elif personne == "conjoint":
        cle_naissance = "Naissance conjoint"
    else:
        raise ValueError("Le paramètre 'personne' doit être 'rentier' ou 'conjoint'.")
    
    #debut de la rente
    cle_debut = "Date d effet de la rente"

    # Conversion des dates
    date_naissance = datetime.strptime(contrats[cle_naissance], "%d/%m/%Y")
    date_debut = datetime.strptime(contrats[cle_debut], "%d/%m/%Y")

    # Calcul des âges
    age_exact_val = age_exact(date_naissance, date_debut)
    age_entier = int(age_exact_val)
    age_decimal = age_exact_val - age_entier
    annee_naissance = date_naissance.year

    # Vérification que l'annee est dans la table
    if not (1900 <= annee_naissance <= 2005):
        print(f"Année de naissance invalide pour le {personne}.")

    return (
        age_exact_val,
        age_entier,
        age_decimal,
        annee_naissance
    )
