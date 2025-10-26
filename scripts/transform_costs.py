"""
Module de transformation des données de coûts cloud
Nettoie, enrichit et agrège les données pour l'analyse
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import glob


class CostTransformer:
    """Classe pour transformer et enrichir les données de coûts"""
    
    def __init__(self, input_file=None):
        """
        Args:
            input_file: Chemin vers le fichier CSV à transformer
                       Si None, prend le dernier fichier dans data/raw/
        """
        if input_file is None:
            # Trouver le dernier fichier
            csv_files = glob.glob('data/raw/*.csv')
            if not csv_files:
                raise FileNotFoundError("Aucun fichier de données trouvé dans data/raw/")
            input_file = max(csv_files, key=os.path.getctime)
        
        print(f"📂 Chargement : {input_file}")
        self.df = pd.read_csv(input_file)
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        
        print(f"✅ {len(self.df):,} lignes chargées\n")
    
    def clean_data(self):
        """Nettoie les données (valeurs manquantes, doublons, etc.)"""
        
        print("🧹 NETTOYAGE DES DONNÉES")
        print("-" * 60)
        
        initial_rows = len(self.df)
        
        # 1. Supprimer les doublons
        duplicates = self.df.duplicated().sum()
        self.df = self.df.drop_duplicates()
        print(f"   ♻️  Doublons supprimés : {duplicates}")
        
        # 2. Supprimer les lignes avec coûts négatifs
        negative_costs = (self.df['Cost'] < 0).sum()
        self.df = self.df[self.df['Cost'] >= 0]
        print(f"   ⛔ Coûts négatifs supprimés : {negative_costs}")
        
        # 3. Gérer les valeurs manquantes
        missing_values = self.df.isnull().sum().sum()
        self.df = self.df.fillna({
            'Service': 'Unknown',
            'Region': 'Unknown',
            'AccountName': 'Unknown'
        })
        print(f"   🔧 Valeurs manquantes traitées : {missing_values}")
        
        # 4. Arrondir les coûts à 2 décimales
        self.df['Cost'] = self.df['Cost'].round(2)
        
        final_rows = len(self.df)
        print(f"   📊 Lignes conservées : {final_rows:,} / {initial_rows:,}")
        print()
        
        return self
    
    def add_time_dimensions(self):
        """Ajoute des dimensions temporelles pour l'analyse"""
        
        print("📅 AJOUT DE DIMENSIONS TEMPORELLES")
        print("-" * 60)
        
        # Extraire les composantes de date
        self.df['Year'] = self.df['Date'].dt.year
        self.df['Month'] = self.df['Date'].dt.month
        self.df['MonthName'] = self.df['Date'].dt.strftime('%B')
        self.df['Week'] = self.df['Date'].dt.isocalendar().week
        self.df['DayOfWeek'] = self.df['Date'].dt.dayofweek
        self.df['DayName'] = self.df['Date'].dt.strftime('%A')
        self.df['IsWeekend'] = self.df['DayOfWeek'].isin([5, 6])
        
        # Période Year-Month pour agrégations
        self.df['YearMonth'] = self.df['Date'].dt.to_period('M').astype(str)
        
        print(f"   ✅ Colonnes ajoutées : Year, Month, Week, DayOfWeek, etc.")
        print(f"   📆 Période couverte : {self.df['Date'].min().date()} → {self.df['Date'].max().date()}")
        print()
        
        return self
    
    def categorize_services(self):
        """Catégorise les services AWS par type"""
        
        print("🏷️  CATÉGORISATION DES SERVICES")
        print("-" * 60)
        
        # Définir les catégories
        categories = {
            'Compute': ['EC2', 'Lambda', 'ECS', 'Fargate', 'Batch'],
            'Storage': ['S3', 'EBS', 'EFS', 'Glacier'],
            'Database': ['RDS', 'DynamoDB', 'ElastiCache', 'Redshift'],
            'Networking': ['VPC', 'CloudFront', 'Route53', 'Data Transfer', 'NAT Gateway'],
            'Analytics': ['Athena', 'EMR', 'Kinesis', 'QuickSight'],
            'Security': ['IAM', 'KMS', 'Secrets Manager', 'GuardDuty'],
            'Management': ['CloudWatch', 'Config', 'Systems Manager']
        }
        
        def get_category(service):
            """Détermine la catégorie d'un service"""
            for category, keywords in categories.items():
                if any(keyword.lower() in service.lower() for keyword in keywords):
                    return category
            return 'Other'
        
        self.df['ServiceCategory'] = self.df['Service'].apply(get_category)
        
        # Statistiques
        category_counts = self.df['ServiceCategory'].value_counts()
        print(f"   📦 Catégories créées : {len(category_counts)}")
        for cat, count in category_counts.items():
            print(f"      • {cat:15s} : {count:,} enregistrements")
        print()
        
        return self
    
    def calculate_aggregations(self):
        """Calcule différentes agrégations des coûts"""
        
        print("🔢 CALCUL DES AGRÉGATIONS")
        print("-" * 60)
        
        # 1. Coûts journaliers totaux
        self.daily_costs = self.df.groupby('Date').agg({
            'Cost': 'sum'
        }).reset_index()
        self.daily_costs.columns = ['Date', 'TotalCost']
        print(f"   ✅ Agrégation journalière : {len(self.daily_costs)} jours")
        
        # 2. Coûts par service et par jour
        self.daily_service_costs = self.df.groupby(['Date', 'Service']).agg({
            'Cost': 'sum'
        }).reset_index()
        print(f"   ✅ Coûts par service/jour : {len(self.daily_service_costs)} lignes")
        
        # 3. Coûts mensuels par compte
        if 'AccountName' in self.df.columns:
            self.monthly_account_costs = self.df.groupby(['YearMonth', 'AccountName']).agg({
                'Cost': 'sum'
            }).reset_index()
            print(f"   ✅ Coûts mensuels par compte : {len(self.monthly_account_costs)} lignes")
        
        # 4. Coûts par catégorie de service
        self.category_costs = self.df.groupby(['Date', 'ServiceCategory']).agg({
            'Cost': 'sum'
        }).reset_index()
        print(f"   ✅ Coûts par catégorie : {len(self.category_costs)} lignes")
        
        # 5. Coûts par région
        if 'Region' in self.df.columns:
            self.region_costs = self.df.groupby(['Date', 'Region']).agg({
                'Cost': 'sum'
            }).reset_index()
            print(f"   ✅ Coûts par région : {len(self.region_costs)} lignes")
        
        print()
        return self
    
    def calculate_kpis(self):
        """Calcule les KPIs métier"""
        
        print("📊 CALCUL DES KPIs")
        print("-" * 60)
        
        # KPI 1 : Coût total
        total_cost = self.df['Cost'].sum()
        print(f"   💰 Coût total : ${total_cost:,.2f}")
        
        # KPI 2 : Coût moyen journalier
        avg_daily_cost = self.daily_costs['TotalCost'].mean()
        print(f"   📈 Coût moyen/jour : ${avg_daily_cost:,.2f}")
        
        # KPI 3 : Tendance (variation entre premier et dernier mois)
        monthly_totals = self.df.groupby('YearMonth')['Cost'].sum().sort_index()
        if len(monthly_totals) >= 2:
            first_month = monthly_totals.iloc[0]
            last_month = monthly_totals.iloc[-1]
            trend = ((last_month - first_month) / first_month) * 100
            print(f"   📉 Tendance : {trend:+.1f}% (vs premier mois)")
        
        # KPI 4 : Top 3 services les plus coûteux
        top_services = self.df.groupby('Service')['Cost'].sum().sort_values(ascending=False).head(3)
        print(f"   🏆 Top 3 services :")
        for i, (service, cost) in enumerate(top_services.items(), 1):
            pct = (cost / total_cost) * 100
            print(f"      {i}. {service:25s} : ${cost:10,.2f} ({pct:.1f}%)")
        
        # KPI 5 : Détection d'anomalies (jours avec coûts > 2x la moyenne)
        mean_cost = self.daily_costs['TotalCost'].mean()
        std_cost = self.daily_costs['TotalCost'].std()
        threshold = mean_cost + (2 * std_cost)
        
        self.daily_costs['IsAnomaly'] = self.daily_costs['TotalCost'] > threshold
        anomalies = self.daily_costs[self.daily_costs['IsAnomaly']]
        
        print(f"   ⚠️  Anomalies détectées : {len(anomalies)} jours")
        if len(anomalies) > 0:
            print(f"      (coûts > ${threshold:,.2f})")
        
        # KPI 6 : Répartition weekend vs semaine
        weekend_costs = self.df[self.df['IsWeekend'] == True]['Cost'].sum()
        weekday_costs = self.df[self.df['IsWeekend'] == False]['Cost'].sum()
        print(f"   📅 Répartition :")
        print(f"      Semaine : ${weekday_costs:,.2f} ({weekday_costs/total_cost*100:.1f}%)")
        print(f"      Weekend : ${weekend_costs:,.2f} ({weekend_costs/total_cost*100:.1f}%)")
        
        # Stocker les KPIs dans un dictionnaire
        self.kpis = {
            'total_cost': total_cost,
            'avg_daily_cost': avg_daily_cost,
            'trend_pct': trend if len(monthly_totals) >= 2 else 0,
            'anomaly_count': len(anomalies),
            'weekend_pct': (weekend_costs / total_cost) * 100
        }
        
        print()
        return self
    
    def create_summary_report(self):
        """Crée un rapport récapitulatif détaillé"""
        
        print("📋 CRÉATION DU RAPPORT RÉCAPITULATIF")
        print("-" * 60)
        
        # Top 10 services
        top10_services = self.df.groupby('Service').agg({
            'Cost': 'sum'
        }).sort_values('Cost', ascending=False).head(10)
        top10_services['Percentage'] = (top10_services['Cost'] / self.df['Cost'].sum()) * 100
        top10_services = top10_services.round(2)
        
        # Évolution mensuelle
        monthly_evolution = self.df.groupby('YearMonth').agg({
            'Cost': 'sum'
        }).reset_index()
        monthly_evolution.columns = ['Month', 'TotalCost']
        monthly_evolution['TotalCost'] = monthly_evolution['TotalCost'].round(2)
        
        # Par compte
        if 'AccountName' in self.df.columns:
            account_summary = self.df.groupby('AccountName').agg({
                'Cost': 'sum'
            }).sort_values('Cost', ascending=False)
            account_summary['Percentage'] = (account_summary['Cost'] / self.df['Cost'].sum()) * 100
            account_summary = account_summary.round(2)
        else:
            account_summary = None
        
        # Par catégorie
        category_summary = self.df.groupby('ServiceCategory').agg({
            'Cost': 'sum'
        }).sort_values('Cost', ascending=False)
        category_summary['Percentage'] = (category_summary['Cost'] / self.df['Cost'].sum()) * 100
        category_summary = category_summary.round(2)
        
        self.summary = {
            'top10_services': top10_services,
            'monthly_evolution': monthly_evolution,
            'account_summary': account_summary,
            'category_summary': category_summary
        }
        
        print(f"   ✅ Rapport créé avec {len(self.summary)} sections")
        print()
        
        return self
    
    def save_transformed_data(self):
        """Sauvegarde toutes les données transformées"""
        
        print("💾 SAUVEGARDE DES DONNÉES TRANSFORMÉES")
        print("-" * 60)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 1. Données principales enrichies
        main_file = f'data/processed/costs_enriched_{timestamp}.csv'
        self.df.to_csv(main_file, index=False)
        print(f"   ✅ Données enrichies : {main_file}")
        
        # 2. Coûts journaliers
        daily_file = f'data/processed/daily_costs_{timestamp}.csv'
        self.daily_costs.to_csv(daily_file, index=False)
        print(f"   ✅ Coûts journaliers : {daily_file}")
        
        # 3. Top 10 services
        top10_file = f'data/processed/top10_services_{timestamp}.csv'
        self.summary['top10_services'].to_csv(top10_file)
        print(f"   ✅ Top 10 services : {top10_file}")
        
        # 4. Évolution mensuelle
        monthly_file = f'data/processed/monthly_evolution_{timestamp}.csv'
        self.summary['monthly_evolution'].to_csv(monthly_file, index=False)
        print(f"   ✅ Évolution mensuelle : {monthly_file}")
        
        # 5. Résumé par catégorie
        category_file = f'data/processed/category_summary_{timestamp}.csv'
        self.summary['category_summary'].to_csv(category_file)
        print(f"   ✅ Résumé par catégorie : {category_file}")
        
        # 6. KPIs en JSON
        import json
        kpi_file = f'data/processed/kpis_{timestamp}.json'
        with open(kpi_file, 'w') as f:
            json.dump(self.kpis, f, indent=2)
        print(f"   ✅ KPIs : {kpi_file}")
        
        print()
        return self


def main():
    """Pipeline de transformation complet"""
    
    print("="*60)
    print("🔄 TRANSFORMATION DES DONNÉES DE COÛTS CLOUD")
    print("="*60 + "\n")
    
    try:
        # Créer le transformateur
        transformer = CostTransformer()
        
        # Exécuter le pipeline de transformation
        transformer \
            .clean_data() \
            .add_time_dimensions() \
            .categorize_services() \
            .calculate_aggregations() \
            .calculate_kpis() \
            .create_summary_report() \
            .save_transformed_data()
        
        print("="*60)
        print("✅ TRANSFORMATION TERMINÉE AVEC SUCCÈS")
        print("="*60)
        print("\n📁 Fichiers disponibles dans data/processed/")
        print("🎯 Prochaine étape : Visualisation avec Streamlit\n")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de la transformation : {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()