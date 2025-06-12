import pandas as pd
from datetime import datetime
import json
with open("param.json", "r", encoding="utf-8") as f:
    contrats = json.load(f)
from calcul_age import calcul_age_participant


'''calcul la periode'''
age_periode =0
rentier=calcul_age_participant(contrats, "rentier")
conjoint = calcul_age_participant(contrats,"conjoint")
age_periode = max(rentier[0], conjoint[0]) + 120 * 12  # 120 ans * 12 mois


def generer_dates_flux(date_effet_str):
    date_effet = pd.Timestamp(datetime.strptime(date_effet_str, "%d/%m/%Y"))  # Convertir en Timestamp
    date_effet = date_effet + pd.DateOffset(months=-1)  # Décale d'un mois

    if contrats['fractionnement']==12 :
        flux_mois = pd.date_range(start=date_effet, periods = int(age_periode) , freq='ME')  # fin de mois
    elif contrats['fractionnement'] == 4 :
        flux_mois = pd.date_range(start=date_effet, periods = int(age_periode/3) , freq='3ME')  # fin de 3 mois
    elif contrats['fractionnement'] == 2 :
        flux_mois = pd.date_range(start=date_effet, periods = int(age_periode/6 ), freq='6ME')  # fin de 6 mois
    elif contrats['fractionnement'] == 1 :
        flux_mois = pd.date_range(start=date_effet, periods = int(age_periode/12) , freq='YE')  # fin d annee
    else:
        raise ValueError("Fractionnement invalide")  # si l'utilisateur n'a pas rempli correctement
    
    if date_effet.month != 1 or date_effet.day != 1:
        date_effet = pd.Timestamp(contrats['Date d effet de la rente'])  # Force le bon début  
    flux_mois = flux_mois[1:] # effacer le mois de decalage
    return [date_effet] + list(flux_mois) #retourne les flux 




dates = generer_dates_flux(contrats['Date d effet de la rente'])
dates_formattees = [d.strftime('%d/%m/%Y') for d in dates] #met dans un autres formats

#print(dates_formattees)
'''


def generer_dates_flux(date_effet_str, contrats):
    """Génère une liste de dates de fin de période selon le fractionnement."""
    date_effet = pd.to_datetime(date_effet_str, dayfirst=True) - pd.DateOffset(months=1)

    # Définition de la période maximale (âge maximal sur 120 ans)
    age_periode = max(calcul_age_participant(contrats, "rentier")[0], 
                      calcul_age_participant(contrats, "conjoint")[0]) + 120 * 12

    # Mappage des fréquences
    freq_map = {12: 'ME', 4: '3ME', 2: '6ME', 1: 'YE'}
    fractionnement = contrats.get("fractionnement", None)

    if fractionnement not in freq_map:
        raise ValueError("Fractionnement invalide")

    flux_mois = pd.date_range(start=date_effet, periods=int(age_periode / (12 / fractionnement)), freq=freq_map[fractionnement])

    # Assurer que la date de début est bien celle du contrat
    flux_mois = [pd.to_datetime(contrats['Date d effet de la rente'], dayfirst=True)] + list(flux_mois[1:])

    return flux_mois

# Génération des dates et formatage
dates = generer_dates_flux(contrats['Date d effet de la rente'], contrats)
dates_formattees = [d.strftime('%d/%m/%Y') for d in dates]  # Formatage des dates

#print(dates_formattees)
'''