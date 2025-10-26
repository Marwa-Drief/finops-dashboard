"""
Générateur de données de coûts cloud simulées
Simule des données AWS réalistes pour développement
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class CloudCostSimulator:
    """Génère des données de coûts cloud réalistes"""
    
    def __init__(self, start_date, end_date):
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        
        # Services AWS typiques
        self.services = [
            'Amazon EC2', 'Amazon S3', 'Amazon RDS', 
            'AWS Lambda', 'Amazon CloudFront', 'Amazon DynamoDB',
            'Amazon ECS', 'Amazon VPC', 'AWS Data Transfer'
        ]
        
        # Coûts moyens par service (USD/jour)
        self.service_base_costs = {
            'Amazon EC2': 15.0,
            'Amazon S3': 5.0,
            'Amazon RDS': 10.0,
            'AWS Lambda': 2.0,
            'Amazon CloudFront': 8.0,
            'Amazon DynamoDB': 3.0,
            'Amazon ECS': 12.0,
            'Amazon VPC': 1.0,
            'AWS Data Transfer': 4.0
        }
        
        # Régions AWS
        self.regions = ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']
        
        # Comptes simulés (pour multi-compte)
        self.accounts = {
            '123456789012': 'Production',
            '123456789013': 'Development',
            '123456789014': 'Testing'
        }
    
    def generate_daily_costs(self):
        """Génère des coûts journaliers"""
        
        date_range = pd.date_range(self.start_date, self.end_date, freq='D')
        data = []
        
        for date in date_range:
            for service in self.services:
                for account_id, account_name in self.accounts.items():
                    
                    # Coût de base avec variation aléatoire
                    base_cost = self.service_base_costs[service]
                    
                    # Variation journalière (-20% à +30%)
                    variation = random.uniform(0.8, 1.3)
                    
                    # Augmentation en semaine vs weekend
                    if date.weekday() < 5:  # Lundi-Vendredi
                        weekday_multiplier = 1.2
                    else:  # Weekend
                        weekday_multiplier = 0.6
                    
                    # Tendance mensuelle (croissance progressive)
                    days_since_start = (date - self.start_date).days
                    growth_factor = 1 + (days_since_start * 0.001)
                    
                    # Calcul du coût final
                    daily_cost = base_cost * variation * weekday_multiplier * growth_factor
                    
                    # Arrondir à 2 décimales
                    daily_cost = round(daily_cost, 2)
                    
                    # Région aléatoire
                    region = random.choice(self.regions)
                    
                    data.append({
                        'Date': date.strftime('%Y-%m-%d'),
                        'AccountId': account_id,
                        'AccountName': account_name,
                        'Service': service,
                        'Region': region,
                        'Cost': daily_cost,
                        'Currency': 'USD'
                    })
        
        df = pd.DataFrame(data)
        return df
    
    def generate_monthly_summary(self, daily_df):
        """Génère un résumé mensuel à partir des données journalières"""
        
        daily_df['Month'] = pd.to_datetime(daily_df['Date']).dt.to_period('M')
        
        monthly = daily_df.groupby(['Month', 'AccountId', 'AccountName', 'Service']).agg({
            'Cost': 'sum',
            'Region': 'first'
        }).reset_index()
        
        monthly['Month'] = monthly['Month'].astype(str)
        monthly['Cost'] = monthly['Cost'].round(2)
        
        return monthly


def generate_sample_data(months=3):
    """
    Fonction principale pour générer des données de test
    
    Args:
        months: Nombre de mois de données à générer
    """
    
    # Calculer les dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)
    
    print(f"🎲 Génération de données simulées...")
    print(f"📅 Période : {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}\n")
    
    # Créer le simulateur
    simulator = CloudCostSimulator(start_date, end_date)
    
    # Générer les données
    print("⏳ Génération des coûts journaliers...")
    daily_costs = simulator.generate_daily_costs()
    
    print("⏳ Génération du résumé mensuel...")
    monthly_costs = simulator.generate_monthly_summary(daily_costs)
    
    # Statistiques
    total_cost = daily_costs['Cost'].sum()
    nb_records = len(daily_costs)
    
    print(f"\n✅ Données générées avec succès !")
    print(f"   📊 Nombre d'enregistrements : {nb_records:,}")
    print(f"   💰 Coût total simulé : ${total_cost:,.2f}")
    print(f"   📅 Services : {len(simulator.services)}")
    print(f"   🏢 Comptes : {len(simulator.accounts)}")
    
    return daily_costs, monthly_costs


if __name__ == "__main__":
    # Test du générateur
    daily, monthly = generate_sample_data(months=3)
    
    print("\n📄 Aperçu des données journalières (5 premières lignes) :")
    print(daily.head())
    
    print("\n📄 Aperçu des données mensuelles (5 premières lignes) :")
    print(monthly.head())