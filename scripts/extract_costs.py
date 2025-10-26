"""
Script d'extraction des coûts cloud
Peut utiliser soit des données AWS réelles, soit des données simulées
"""

import boto3
import pandas as pd
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from data_simulator import generate_sample_data

# Charger les variables d'environnement
load_dotenv()


class CostExtractor:
    """Classe pour extraire les coûts depuis AWS ou données simulées"""
    
    def __init__(self, use_simulation=True):
        """
        Args:
            use_simulation: Si True, utilise des données simulées
                          Si False, utilise l'API AWS Cost Explorer
        """
        self.use_simulation = use_simulation
        
        if not use_simulation:
            # Initialiser le client AWS
            self.client = boto3.client(
                'ce',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
    
    def extract_costs(self, start_date, end_date, granularity='DAILY'):
        """
        Extrait les coûts pour une période donnée
        
        Args:
            start_date: Date de début (format: 'YYYY-MM-DD')
            end_date: Date de fin (format: 'YYYY-MM-DD')
            granularity: 'DAILY' ou 'MONTHLY'
        
        Returns:
            DataFrame avec les coûts
        """
        
        if self.use_simulation:
            print("🎲 Mode simulation activé")
            return self._extract_simulated_costs(start_date, end_date)
        else:
            print("☁️  Mode AWS réel activé")
            return self._extract_aws_costs(start_date, end_date, granularity)
    
    def _extract_simulated_costs(self, start_date, end_date):
        """Extrait des données simulées"""
        
        # Calculer le nombre de mois
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        months = ((end.year - start.year) * 12 + end.month - start.month) + 1
        
        # Générer les données
        daily_costs, monthly_costs = generate_sample_data(months=months)
        
        # Filtrer par dates
        daily_costs['Date'] = pd.to_datetime(daily_costs['Date'])
        mask = (daily_costs['Date'] >= start_date) & (daily_costs['Date'] <= end_date)
        
        return daily_costs[mask].reset_index(drop=True)
    
    def _extract_aws_costs(self, start_date, end_date, granularity):
        """Extrait les données depuis AWS Cost Explorer"""
        
        try:
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity=granularity,
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'DIMENSION', 'Key': 'REGION'}
                ]
            )
            
            # Transformer la réponse en DataFrame
            data = []
            for result in response['ResultsByTime']:
                date = result['TimePeriod']['Start']
                
                for group in result['Groups']:
                    service = group['Keys'][0]
                    region = group['Keys'][1]
                    cost = float(group['Metrics']['UnblendedCost']['Amount'])
                    
                    data.append({
                        'Date': date,
                        'Cloud': 'AWS',  
                        'Service': service,
                        'Region': region,
                        'Cost': cost,
                        'Currency': 'USD'
                    })
            
            df = pd.DataFrame(data)
            return df
            
        except Exception as e:
            print(f"❌ Erreur lors de l'extraction AWS : {e}")
            print("🔄 Basculement sur les données simulées...")
            return self._extract_simulated_costs(start_date, end_date)
    
    def save_to_csv(self, df, filename):
        """Sauvegarde les données dans un fichier CSV"""
        
        filepath = os.path.join('data', 'raw', filename)
        df.to_csv(filepath, index=False)
        
        print(f"💾 Données sauvegardées : {filepath}")
        print(f"   📊 {len(df)} enregistrements")
        print(f"   💰 Coût total : ${df['Cost'].sum():,.2f}")


def main():
    """Fonction principale d'extraction"""
    
    print("="*60)
    print("🚀 EXTRACTION DES COÛTS CLOUD")
    print("="*60 + "\n")
    
    # Configuration
    USE_SIMULATION = False  # Changer à False quand Cost Explorer est prêt
    
    # Dates d'extraction (3 derniers mois)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    print(f"📅 Période d'extraction : {start_str} → {end_str}")
    print(f"🔧 Mode : {'Simulation' if USE_SIMULATION else 'AWS Réel'}\n")
    
    # Créer l'extracteur
    extractor = CostExtractor(use_simulation=USE_SIMULATION)
    
    # Extraire les données
    print("⏳ Extraction en cours...\n")
    df_costs = extractor.extract_costs(start_str, end_str)
    
    # Sauvegarder
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'cloud_costs_{timestamp}.csv'
    extractor.save_to_csv(df_costs, filename)
    
    # Afficher un aperçu
    print(f"\n📊 Aperçu des données (5 premières lignes) :")
    print(df_costs.head())
    
    print("\n✅ Extraction terminée avec succès !")
    print("="*60)


if __name__ == "__main__":
    main()