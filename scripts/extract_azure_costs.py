"""
Module d'extraction des coûts Azure via Cost Management API
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd
from azure.identity import ClientSecretCredential
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.costmanagement.models import (
    QueryDefinition, 
    QueryTimePeriod, 
    TimeframeType,
    QueryDataset,
    QueryAggregation,
    QueryGrouping
)
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AzureCostExtractor:
    """Extracteur de coûts Azure Cost Management"""
    
    def __init__(self):
        """Initialise la connexion Azure"""
        
        # Credentials Azure
        tenant_id = os.getenv('AZURE_TENANT_ID')
        client_id = os.getenv('AZURE_CLIENT_ID')
        client_secret = os.getenv('AZURE_CLIENT_SECRET')
        subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        
        if not all([tenant_id, client_id, client_secret, subscription_id]):
            raise ValueError("Credentials Azure manquants dans .env")
        
        # Authentification
        self.credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        # Client Cost Management
        self.client = CostManagementClient(
            credential=self.credential,
            base_url='https://management.azure.com'
        )
        
        self.subscription_id = subscription_id
        self.scope = f"/subscriptions/{subscription_id}"
    
    def extract_costs(self, start_date, end_date):
        """
        Extrait les coûts Azure pour une période
        
        Args:
            start_date: Date de début (YYYY-MM-DD)
            end_date: Date de fin (YYYY-MM-DD)
        
        Returns:
            DataFrame avec les coûts
        """
        
        logger.info(f"☁️  Extraction Azure : {start_date} → {end_date}")
        
        try:
            # Définir la requête
            query = QueryDefinition(
                type="ActualCost",
                timeframe=TimeframeType.CUSTOM,
                time_period=QueryTimePeriod(
                    from_property=datetime.strptime(start_date, '%Y-%m-%d'),
                    to=datetime.strptime(end_date, '%Y-%m-%d')
                ),
                dataset=QueryDataset(
                    granularity="Daily",
                    aggregation={
                        "totalCost": QueryAggregation(name="Cost", function="Sum")
                    },
                    grouping=[
                        QueryGrouping(type="Dimension", name="ServiceName"),
                        QueryGrouping(type="Dimension", name="ResourceLocation"),
                        QueryGrouping(type="Dimension", name="SubscriptionName")
                    ]
                )
            )
            
            # Exécuter la requête
            logger.info("⏳ Requête Azure Cost Management en cours...")
            result = self.client.query.usage(scope=self.scope, parameters=query)
            
            # Extraire les données
            data = []
            
            if hasattr(result, 'rows') and result.rows:
                columns = [col.name for col in result.columns]
                
                for row in result.rows:
                    row_dict = dict(zip(columns, row))
                    
                    # Normaliser les données
                    data.append({
                        'Date': pd.to_datetime(row_dict.get('UsageDate', row_dict.get('Date'))).strftime('%Y-%m-%d'),
                        'Cloud': 'Azure',
                        'Service': row_dict.get('ServiceName', 'Unknown'),
                        'Region': row_dict.get('ResourceLocation', 'Unknown'),
                        'AccountName': row_dict.get('SubscriptionName', 'Azure Subscription'),
                        'AccountId': self.subscription_id,
                        'Cost': float(row_dict.get('Cost', row_dict.get('totalCost', 0))),
                        'Currency': row_dict.get('Currency', 'USD')
                    })
            
            df = pd.DataFrame(data)
            
            if len(df) > 0:
                logger.info(f"✅ {len(df)} enregistrements Azure extraits")
                logger.info(f"💰 Coût total Azure : ${df['Cost'].sum():.2f}")
            else:
                logger.warning("⚠️  Aucune donnée Azure trouvée pour cette période")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction Azure : {e}")
            # Retourner un DataFrame vide en cas d'erreur
            return pd.DataFrame(columns=['Date', 'Cloud', 'Service', 'Region', 
                                        'AccountName', 'AccountId', 'Cost', 'Currency'])


def main():
    """Test du module"""
    
    print("="*60)
    print("🔵 TEST EXTRACTION AZURE COSTS")
    print("="*60 + "\n")
    
    # Dates de test
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    try:
        extractor = AzureCostExtractor()
        df = extractor.extract_costs(start_str, end_str)
        
        if len(df) > 0:
            print("\n📊 Aperçu des données :")
            print(df.head(10))
            
            print("\n📈 Statistiques :")
            print(f"Total enregistrements : {len(df)}")
            print(f"Services uniques : {df['Service'].nunique()}")
            print(f"Régions : {df['Region'].nunique()}")
            print(f"Coût total : ${df['Cost'].sum():.2f}")
        else:
            print("\n⚠️  Aucune donnée disponible")
        
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()