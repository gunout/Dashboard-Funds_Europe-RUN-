import pandas as pd
from datetime import datetime

def process_funds_data(raw_data):
    """Traite et uniformise les données brutes des différentes sources"""
    
    if not raw_data:
        return pd.DataFrame()
    
    # Conversion en DataFrame
    df = pd.DataFrame(raw_data)
    
    # Nettoyage et uniformisation
    df = clean_data(df)
    
    # Validation des données
    df = validate_data(df)
    
    return df

def clean_data(df):
    """Nettoie et uniformise les données"""
    
    # Standardisation des programmes
    programme_mapping = {
        'FEDER': 'FEDER',
        'FSE': 'FSE', 
        'FEADER': 'FEADER',
        'FSE+': 'FSE',
        'INTERREG': 'INTERREG',
        'ERDF': 'FEDER',
        'ESF': 'FSE'
    }
    
    df['programme'] = df['programme'].map(programme_mapping).fillna('FEDER')
    
    # Nettoyage des montants
    df['montant_total'] = pd.to_numeric(df['montant_total'], errors='coerce').fillna(0)
    df['montant_paye'] = pd.to_numeric(df['montant_paye'], errors='coerce').fillna(0)
    df['taux_realisation'] = pd.to_numeric(df['taux_realisation'], errors='coerce').fillna(0)
    
    # S'assurer que le montant payé ne dépasse pas le montant total
    df['montant_paye'] = df[['montant_paye', 'montant_total']].min(axis=1)
    
    # Nettoyage des statuts
    statut_mapping = {
        'terminé': 'Terminé',
        'en cours': 'En cours',
        'finalisation': 'En finalisation',
        'en finalisation': 'En finalisation',
        'completed': 'Terminé',
        'in progress': 'En cours'
    }
    
    df['statut'] = df['statut'].str.lower().map(statut_mapping).fillna('En cours')
    
    return df

def validate_data(df):
    """Valide la cohérence des données"""
    
    # Filtrer les projets avec des montants aberrants
    df = df[df['montant_total'] > 1000]  # Au moins 1000€
    df = df[df['montant_total'] < 100000000]  # Moins de 100 millions
    
    # S'assurer que le taux de réalisation est entre 0 et 100
    df['taux_realisation'] = df['taux_realisation'].clip(0, 100)
    
    return df