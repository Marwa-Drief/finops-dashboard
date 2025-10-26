"""
Script de vérification des données extraites
"""

import pandas as pd
import os
import glob

def check_latest_data():
    """Vérifie le dernier fichier CSV extrait"""
    
    # Trouver le dernier fichier
    csv_files = glob.glob('data/raw/*.csv')
    
    if not csv_files:
        print("❌ Aucun fichier de données trouvé!")
        return
    
    latest_file = max(csv_files, key=os.path.getctime)
    
    print("="*60)
    print(f"📁 Fichier analysé : {latest_file}")
    print("="*60 + "\n")
    
    # Charger les données
    df = pd.read_csv(latest_file)
    
    # Statistiques générales
    print("📊 STATISTIQUES GÉNÉRALES")
    print("-" * 60)
    print(f"Nombre total de lignes : {len(df):,}")
    print(f"Période couverte : {df['Date'].min()} → {df['Date'].max()}")
    print(f"Coût total : ${df['Cost'].sum():,.2f}")
    print(f"Coût moyen par jour : ${df.groupby('Date')['Cost'].sum().mean():,.2f}")
    
    # Par compte (si disponible)
    if 'AccountName' in df.columns:
        print("\n💼 RÉPARTITION PAR COMPTE")
        print("-" * 60)
        account_summary = df.groupby('AccountName')['Cost'].sum().sort_values(ascending=False)
        for account, cost in account_summary.items():
            percentage = (cost / df['Cost'].sum()) * 100
            print(f"{account:20s} : ${cost:10,.2f} ({percentage:5.1f}%)")
    
    # Par service
    print("\n🔧 TOP 5 SERVICES LES PLUS COÛTEUX")
    print("-" * 60)
    service_summary = df.groupby('Service')['Cost'].sum().sort_values(ascending=False).head(5)
    for service, cost in service_summary.items():
        percentage = (cost / df['Cost'].sum()) * 100
        print(f"{service:25s} : ${cost:10,.2f} ({percentage:5.1f}%)")
    
    # Par région
    if 'Region' in df.columns:
        print("\n🌍 RÉPARTITION PAR RÉGION")
        print("-" * 60)
        region_summary = df.groupby('Region')['Cost'].sum().sort_values(ascending=False)
        for region, cost in region_summary.items():
            percentage = (cost / df['Cost'].sum()) * 100
            print(f"{region:20s} : ${cost:10,.2f} ({percentage:5.1f}%)")
    
    print("\n" + "="*60)
    print("✅ Analyse terminée")
    print("="*60)

if __name__ == "__main__":
    check_latest_data()