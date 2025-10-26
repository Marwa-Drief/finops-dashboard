"""
Extracteur unifié multi-cloud : AWS + Azure
"""

import pandas as pd
from datetime import datetime, timedelta
import os
from extract_costs import CostExtractor as AWSExtractor
from extract_azure_costs import AzureCostExtractor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiCloudExtractor:
    """Extracteur unifié AWS + Azure"""
    
    def __init__(self, use_simulation=False):
        self.use_simulation = use_simulation
        self.aws_extractor = AWSExtractor(use_simulation=use_simulation)
        
        # Tenter d'initialiser Azure (optionnel si credentials manquants)
        try:
            self.azure_extractor = AzureCostExtractor()
            self.azure_enabled = True
        except Exception as e:
            logger.warning(f"⚠️  Azure non configuré : {e}")
            self.azure_enabled = False
    
    def extract_all_clouds(self, start_date, end_date):
        """
        Extrait les coûts de tous les clouds configurés
        
        Returns:
            DataFrame unifié avec colonne 'Cloud'
        """
        
        logger.info("="*60)
        logger.info("🌐 EXTRACTION MULTI-CLOUD")
        logger.info("="*60)
        
        all_data = []
        
        # 1. Extraction AWS
        logger.info("\n🟠 Extraction AWS...")
        try:
            aws_df = self.aws_extractor.extract_costs(start_date, end_date)
            if len(aws_df) > 0:
                if 'Cloud' not in aws_df.columns:
                    aws_df['Cloud'] = 'AWS'
                all_data.append(aws_df)
                logger.info(f"✅ AWS : {len(aws_df)} enregistrements, ${aws_df['Cost'].sum():.2f}")
            else:
                logger.warning("⚠️  AWS : Aucune donnée")
        except Exception as e:
            logger.error(f"❌ Erreur AWS : {e}")
        
        # 2. Extraction Azure
        if self.azure_enabled:
            logger.info("\n🔵 Extraction Azure...")
            try:
                azure_df = self.azure_extractor.extract_costs(start_date, end_date)
                
                if len(azure_df) > 0:
                    all_data.append(azure_df)
                    logger.info(f"✅ Azure : {len(azure_df)} enregistrements, ${azure_df['Cost'].sum():.2f}")
                else:
                    logger.warning("⚠️  Azure : Aucune donnée réelle, ajout d'une ligne fictive")
                    azure_placeholder = pd.DataFrame([{
                        'Date': start_date,
                        'Cloud': 'Azure',
                        'Service': 'No Data',
                        'Region': 'N/A',
                        'AccountName': 'Azure Subscription',
                        'AccountId': 'azure-sub-1',
                        'Cost': 0.00,
                        'Currency': 'USD'
                    }])
                    all_data.append(azure_placeholder)
                    
            except Exception as e:
                logger.error(f"❌ Erreur Azure : {e}")
                azure_placeholder = pd.DataFrame([{
                    'Date': start_date,
                    'Cloud': 'Azure',
                    'Service': 'Configuration Error',
                    'Region': 'N/A',
                    'AccountName': 'Azure Subscription',
                    'AccountId': 'azure-sub-1',
                    'Cost': 0.00,
                    'Currency': 'USD'
                }])
                all_data.append(azure_placeholder)
        else:
            logger.info("\n⚠️  Azure désactivé (credentials manquants)")
            azure_placeholder = pd.DataFrame([{
                'Date': start_date,
                'Cloud': 'Azure',
                'Service': 'Not Configured',
                'Region': 'N/A',
                'AccountName': 'Azure Subscription',
                'AccountId': 'not-configured',
                'Cost': 0.00,
                'Currency': 'USD'
            }])
            all_data.append(azure_placeholder)
        
        # 3. Fusion des données
        if not all_data:
            logger.error("❌ Aucune donnée extraite d'aucun cloud")
            return pd.DataFrame()
        
        logger.info("\n🔗 Fusion des données...")
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Normaliser les colonnes
        combined_df['Date'] = pd.to_datetime(combined_df['Date'])
        
        # Statistiques globales
        logger.info("\n" + "="*60)
        logger.info("📊 RÉSUMÉ MULTI-CLOUD")
        logger.info("="*60)
        logger.info(f"Total enregistrements : {len(combined_df):,}")
        logger.info(f"Coût total : ${combined_df['Cost'].sum():,.2f}")
        
        # Par cloud
        for cloud in combined_df['Cloud'].unique():
            cloud_data = combined_df[combined_df['Cloud'] == cloud]
            logger.info(f"  {cloud} : ${cloud_data['Cost'].sum():,.2f} ({len(cloud_data):,} records)")
        
        return combined_df
    
    def save_to_csv(self, df, filename):
        """Sauvegarde les données unifiées"""
        raw_dir = os.path.join('data', 'raw')
        os.makedirs(raw_dir, exist_ok=True)
        filepath = os.path.join(raw_dir, filename)
        df.to_csv(filepath, index=False)
        logger.info(f"\n💾 Données sauvegardées : {filepath}")


def main():
    """Extraction multi-cloud complète"""
    
    USE_SIMULATION = False  # Changez selon vos besoins
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    extractor = MultiCloudExtractor(use_simulation=USE_SIMULATION)
    df = extractor.extract_all_clouds(start_str, end_str)
    
    if len(df) > 0:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'multicloud_costs_{timestamp}.csv'
        extractor.save_to_csv(df, filename)
        print("\n✅ Extraction multi-cloud terminée avec succès !")
    else:
        print("\n❌ Aucune donnée extraite")


if __name__ == "__main__":
    main()
