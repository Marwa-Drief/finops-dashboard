# 📊 **RÉCAPITULATIF COMPLET DU PROJET FINOPS DASHBOARD MULTI-CLOUD**

---

## 🎯 **Vue d'Ensemble**

**Nom** : FinOps Dashboard - Analyse des Coûts Cloud Multi-Compte AWS + Azure

**Objectif** : Pipeline ETL automatisé pour analyser, optimiser et visualiser les coûts cloud multi-providers

**Valeur Business** : Réduction des coûts cloud de 15-30% via identification des optimisations et anomalies

**Niveau** : Projet professionnel production-ready

---

## 🏗️ **Architecture Technique Complète**

```
┌──────────────────────────────────────────────────────────────┐
│                   ARCHITECTURE GLOBALE                        │
└──────────────────────────────────────────────────────────────┘

┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   AWS COST  │         │   AZURE     │         │   AIRFLOW   │
│  EXPLORER   │────────▶│   BILLING   │────────▶│  SCHEDULER  │
│     API     │         │     API     │         │   (Docker)  │
└─────────────┘         └─────────────┘         └─────────────┘
       │                       │                        │
       │                       │                        │
       ▼                       ▼                        ▼
┌──────────────────────────────────────────────────────────────┐
│              EXTRACTION MULTI-CLOUD (Python)                  │
│         extract_multicloud_costs.py (AWS + Azure)            │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
                 ┌────────────────┐
                 │   DATA/RAW/    │
                 │  CSV Brutes    │
                 └────────┬───────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│           TRANSFORMATION (Pandas + Enrichissement)            │
│              transform_costs.py (ETL Logic)                   │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
                 ┌────────────────┐
                 │DATA/PROCESSED/ │
                 │ CSV + KPIs JSON│
                 └────────┬───────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
          ▼                               ▼
  ┌──────────────┐              ┌──────────────┐
  │   AMAZON S3  │              │  STREAMLIT   │
  │   (Archive)  │              │  DASHBOARD   │
  │  Multi-Date  │              │ (localhost)  │
  └──────────────┘              └──────────────┘

```

---

## 📁 **Structure Complète du Projet**

```
finops-dashboard/
│
├── 📂 venv/                                    # Environnement virtuel Python 3.11
│
├── 📂 data/
│   ├── raw/                                    # Données brutes extraites
│   │   ├── cloud_costs_YYYYMMDD_HHMMSS.csv   # AWS brut
│   │   └── multicloud_costs_YYYYMMDD.csv     # AWS + Azure unifié
│   └── processed/                              # Données transformées
│       ├── costs_enriched_*.csv               # Données enrichies complètes
│       ├── daily_costs_*.csv                  # Agrégation journalière
│       ├── top10_services_*.csv               # Top services
│       ├── monthly_evolution_*.csv            # Évolution mensuelle
│       ├── category_summary_*.csv             # Par catégorie
│       └── kpis_*.json                        # KPIs calculés
│
├── 📂 scripts/                                 # Scripts Python ETL
│   ├── data_simulator.py                      # Générateur données test multi-cloud
│   ├── extract_costs.py                       # Extraction AWS seul
│   ├── extract_azure_costs.py                 # Extraction Azure seul
│   ├── extract_multicloud_costs.py            # Extraction unifiée AWS+Azure
│   ├── transform_costs.py                     # Transformation Pandas
│   ├── s3_uploader.py                         # Upload vers S3
│   ├── check_data.py                          # Vérification données
│   └── check_s3.py                            # Vérification S3
│
├── 📂 airflow/                                 # Apache Airflow (Orchestration)
│   ├── dags/                                   # DAGs (Workflows)
│   │   ├── finops_pipeline_dag.py             # DAG principal ETL
│   │   └── s3_cleanup_dag.py                  # Nettoyage S3 (30j)
│   ├── logs/                                   # Logs Airflow
│   ├── plugins/                                # Plugins customs
│   ├── config/                                 # Configuration
│   ├── docker-compose.yaml                     # Orchestration Docker
│   ├── Dockerfile                              # Image custom avec deps
│   ├── requirements.txt                        # Dépendances Airflow
│   └── .env                                    # Variables env Airflow
│
├── 📂 logs/                                    # Logs du pipeline Python
│   ├── pipeline.log                            # Logs exécution
│   ├── execution_history.json                  # Historique runs
│   └── report_*.txt                            # Rapports générés
│
├── 📄 .env                                     # Credentials (racine)
├── 📄 .gitignore                               # Fichiers à ignorer Git
├── 📄 dashboard.py                             # Dashboard Streamlit multi-cloud
├── 📄 pipeline_orchestrator.py                 # Orchestrateur Python simple
├── 📄 run_pipeline_now.py                      # Exécution manuelle pipeline
├── 📄 view_pipeline_stats.py                   # Statistiques pipeline
├── 📄 start_pipeline.bat                       # Lanceur Windows
├── 📄 test_aws_connection.py                   # Test connexion AWS
├── 📄 test_aws_connection_v2.py                # Test avancé AWS
└── 📄 README.md                                # Documentation complète

```

---

## 🔧 **Stack Technique Complète**

### **Backend & ETL**

| Technologie | Version | Usage |
| --- | --- | --- |
| **Python** | 3.11 | Langage principal |
| **boto3** | 1.34.34 | SDK AWS (Cost Explorer) |
| **azure-mgmt-costmanagement** | Latest | SDK Azure Billing |
| **azure-identity** | Latest | Authentification Azure |
| **pandas** | 2.1.4 | Manipulation de données |
| **Apache Airflow** | 2.7.3 | Orchestration pipelines |
| **Docker Compose** | Latest | Conteneurisation |

### **Storage & Data**

| Technologie | Usage |
| --- | --- |
| **CSV** | Stockage local données brutes/transformées |
| **JSON** | KPIs et métadonnées |
| **Amazon S3** | Archive cloud long terme |
| **PostgreSQL** | Base de données Airflow |

### **Visualisation & Reporting**

| Technologie | Version | Usage |
| --- | --- | --- |
| **Streamlit** | 1.29.0 | Dashboard interactif web |
| **Plotly** | 5.18.0 | Graphiques interactifs |
| **Recharts** | - | Alternative visualisation |

### **DevOps & Infrastructure**

| Technologie | Usage |
| --- | --- |
| **Docker Desktop** | Conteneurisation Airflow |
| **WSL2** | Environnement Linux (optionnel) |
| **Git** | Contrôle de version |
| **python-dotenv** | Gestion secrets |

### **Cloud Providers**

| Provider | Services Utilisés |
| --- | --- |
| **AWS** | Cost Explorer API, S3, IAM |
| **Azure** | Cost Management API, Service Principal, Entra ID |

---

## 🔄 **Workflow du Pipeline ETL Complet**

### **Pipeline Automatisé (Airflow) - Exécution Quotidienne**

```
┌─────────────────────────────────────────────────────────┐
│  AIRFLOW SCHEDULER (Tous les jours à 8h00)             │
└─────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┬───────────────┐
        │               │               │               │
        ▼               ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   ÉTAPE 1    │ │   ÉTAPE 2    │ │   ÉTAPE 3    │ │   ÉTAPE 4    │
│  EXTRACTION  │→│TRANSFORMATION│→│  UPLOAD S3   │→│NOTIFICATION  │
│  MULTI-CLOUD │ │   (Pandas)   │ │   (boto3)    │ │   (Logs)     │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘

```

### **Détail des Étapes**

### **1️⃣ EXTRACTION MULTI-CLOUD** (`extract_multicloud_costs.py`)

**Sources** :

- **AWS Cost Explorer API** : Coûts réels par service, région, compte
- **Azure Cost Management API** : Coûts réels par service, région, subscription

**Processus** :

```python
# AWS
aws_df = extract_aws_costs(start_date, end_date)
# Colonnes : Date, Cloud='AWS', Service, Region, Cost, Currency

# Azure
azure_df = extract_azure_costs(start_date, end_date)
# Colonnes : Date, Cloud='Azure', Service, Region, Cost, Currency

# Fusion
combined_df = pd.concat([aws_df, azure_df])

```

**Gestion des Erreurs** :

- Si AWS échoue → Données simulées AWS
- Si Azure échoue → Ligne placeholder Azure (coût $0)
- Si tout échoue → Alerte et arrêt pipeline

**Output** : `data/raw/multicloud_costs_YYYYMMDD_HHMMSS.csv`

---

### **2️⃣ TRANSFORMATION** (`transform_costs.py`)

**A. Nettoyage**

```python
- Suppression doublons
- Suppression coûts négatifs
- Gestion valeurs manquantes
- Normalisation formats (dates, montants)

```

**B. Enrichissement**

```python
# Dimensions temporelles
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['MonthName'] = df['Date'].dt.strftime('%B')
df['Week'] = df['Date'].dt.isocalendar().week
df['DayOfWeek'] = df['Date'].dt.dayofweek
df['DayName'] = df['Date'].dt.strftime('%A')
df['IsWeekend'] = df['DayOfWeek'].isin([5, 6])
df['YearMonth'] = df['Date'].dt.to_period('M')

# Catégorisation des services
categories = {
    'Compute': ['EC2', 'Lambda', 'Virtual Machines', 'Functions'],
    'Storage': ['S3', 'EBS', 'Storage Accounts'],
    'Database': ['RDS', 'DynamoDB', 'SQL Database', 'Cosmos DB'],
    'Networking': ['VPC', 'CloudFront', 'CDN', 'Virtual Network'],
    'Analytics': ['Athena', 'EMR', 'Kinesis'],
    'Security': ['IAM', 'KMS', 'GuardDuty'],
    'Management': ['CloudWatch', 'Config']
}
df['ServiceCategory'] = df['Service'].apply(categorize)

```

**C. Agrégations**

```python
# 1. Coûts journaliers totaux
daily_costs = df.groupby('Date')['Cost'].sum()

# 2. Coûts par service et jour
service_daily = df.groupby(['Date', 'Service'])['Cost'].sum()

# 3. Coûts mensuels par compte
monthly_account = df.groupby(['YearMonth', 'AccountName'])['Cost'].sum()

# 4. Coûts par catégorie
category_costs = df.groupby(['Date', 'ServiceCategory'])['Cost'].sum()

# 5. Coûts par cloud
cloud_costs = df.groupby(['Date', 'Cloud'])['Cost'].sum()

# 6. Coûts par région
region_costs = df.groupby(['Date', 'Region'])['Cost'].sum()

```

**D. Calcul des KPIs**

```python
kpis = {
    'total_cost': df['Cost'].sum(),
    'avg_daily_cost': daily_costs.mean(),
    'trend_pct': ((last_month - first_month) / first_month) * 100,
    'anomaly_count': len(anomalies),  # Jours > 2σ
    'weekend_pct': (weekend_costs / total_cost) * 100,
    'top_service': top_services.iloc[0],
    'top_cloud': df.groupby('Cloud')['Cost'].sum().idxmax()
}

```

**E. Détection d'Anomalies**

```python
# Méthode statistique (z-score)
mean = daily_costs.mean()
std = daily_costs.std()
threshold = mean + (2 * std)
anomalies = daily_costs[daily_costs > threshold]

```

**Output** :

- `data/processed/costs_enriched_*.csv` (données complètes)
- `data/processed/daily_costs_*.csv`
- `data/processed/top10_services_*.csv`
- `data/processed/monthly_evolution_*.csv`
- `data/processed/category_summary_*.csv`
- `data/processed/kpis_*.json`

---

### **3️⃣ UPLOAD S3** (`s3_uploader.py`)

**Organisation S3** :

```
s3://finops-dashboard-data/
├── processed/
│   └── daily/
│       └── 2025-10-26/
│           ├── costs_enriched_20251026_083015.csv
│           └── daily_costs_20251026_083015.csv
├── reports/
│   └── 2025-10-26/
│       ├── top10_services_20251026_083015.csv
│       └── monthly_evolution_20251026_083015.csv
└── kpis/
    └── 2025-10-26/
        └── kpis_20251026_083015.json

```

**Code** :

```python
s3_client = boto3.client('s3')
s3_client.upload_file(
    local_path='data/processed/costs_enriched_*.csv',
    bucket='finops-dashboard-data',
    key=f'processed/daily/{today}/costs_enriched_{timestamp}.csv'
)

```

**Rétention** : DAG de cleanup supprime fichiers > 30 jours

---

### **4️⃣ NOTIFICATION** (`send_notification_task`)

**Rapport généré** :

```
╔══════════════════════════════════════════════════════════╗
║           RAPPORT FINOPS - 26/10/2025 08:30           ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  💰 Coût Total        : $6,842.50                       ║
║  📊 Coût Moyen/Jour   : $75.19                          ║
║  📈 Tendance          : +12.3%                          ║
║  ⚠️  Anomalies         : 3 jours                         ║
║                                                          ║
║  ☁️  AWS              : $4,505.25 (65.8%)               ║
║  ☁️  Azure            : $2,337.25 (34.2%)               ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

```

**Logging** :

- `logs/pipeline.log` : Logs détaillés
- `logs/execution_history.json` : Historique des runs
- `logs/report_*.txt` : Rapports texte

---

## 📊 **Dashboard Streamlit - Fonctionnalités Complètes**

### **Interface Utilisateur**

```
┌─────────────────────────────────────────────────────────┐
│  💰 FinOps Dashboard - Multi-Cloud Cost Analysis        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [📊 4 KPI CARDS]                                       │
│   ┌──────────┬──────────┬──────────┬──────────┐        │
│   │ Coût     │ Coût Moy │ Tendance │ Anomalies│        │
│   │ Total    │ /Jour    │ +12.3%   │    3     │        │
│   └──────────┴──────────┴──────────┴──────────┘        │
│                                                          │
├─────────────────────────────────────────────────────────┤
│  [☁️ COMPARAISON MULTI-CLOUD]                          │
│   ┌────────────────┬────────────────┐                  │
│   │ Graphique Pie  │ Tableau Stats  │                  │
│   │ AWS vs Azure   │ Par Cloud      │                  │
│   └────────────────┴────────────────┘                  │
│                                                          │
├─────────────────────────────────────────────────────────┤
│  [📈 6 GRAPHIQUES INTERACTIFS]                          │
│   ┌────────────────┬────────────────┐                  │
│   │ Évolution      │ Répartition    │                  │
│   │ Journalière    │ Services       │                  │
│   └────────────────┴────────────────┘                  │
│   ┌────────────────┬────────────────┐                  │
│   │ Par Catégorie  │ Par Compte     │                  │
│   │ (Barres)       │ (Aires)        │                  │
│   └────────────────┴────────────────┘                  │
│   ┌────────────────┬────────────────┐                  │
│   │ Hebdomadaire   │ Tendance       │                  │
│   │ (Barres)       │ Mensuelle      │                  │
│   └────────────────┴────────────────┘                  │
│                                                          │
├─────────────────────────────────────────────────────────┤
│  [📋 TOP 10 SERVICES]                                   │
│   Tableau détaillé avec coûts, moyennes, parts         │
│                                                          │
├─────────────────────────────────────────────────────────┤
│  [💾 EXPORT CSV]                                        │
│   Boutons téléchargement données filtrées              │
└─────────────────────────────────────────────────────────┘

[🔍 SIDEBAR FILTRES]
  📅 Période (date picker)
  ☁️  Cloud (AWS / Azure / Tous)
  💼 Compte (select)
  📦 Catégorie (select)

```

### **Graphiques Détaillés**

**1. Évolution Journalière** (`plot_daily_costs`)

- Type : Line chart
- Axe X : Date
- Axe Y : Coût USD
- Features : Zoom, hover détails, markers

**2. Répartition Services** (`plot_service_breakdown`)

- Type : Donut chart
- Top 10 services
- Affichage : % + montant

**3. Coûts par Catégorie** (`plot_category_costs`)

- Type : Horizontal bar chart
- Catégories : Compute, Storage, Database, etc.
- Couleurs : Gradient blues

**4. Comparaison Comptes** (`plot_account_comparison`)

- Type : Stacked area chart
- Multi-comptes AWS/Azure
- Évolution temporelle

**5. Analyse Hebdomadaire** (`plot_weekday_analysis`)

- Type : Bar chart
- Lundi-Dimanche
- Couleurs : Semaine (bleu) vs Weekend (orange)

**6. Tendance Mensuelle** (`plot_monthly_trend`)

- Type : Line chart with markers
- Évolution sur plusieurs mois
- Indicateur de croissance

**7. Comparaison Multi-Cloud** (`plot_cloud_comparison`)

- Type : Pie chart
- AWS vs Azure
- Couleurs : AWS (orange) / Azure (bleu)

### **Fonctionnalités Avancées**

**Filtres Dynamiques** :

```python
# Tous les filtres se cumulent
filtered_df = df[
    (df['Date'] >= start_date) &
    (df['Date'] <= end_date) &
    (df['Cloud'] == selected_cloud) &  # Si != 'Tous'
    (df['AccountName'] == selected_account) &  # Si != 'Tous'
    (df['ServiceCategory'] == selected_category)  # Si != 'Toutes'
]

```

**Export CSV** :

```python
# Export données filtrées
csv_data = filtered_df.to_csv(index=False)
st.download_button("Télécharger CSV", csv_data)

# Export top 10 services
top10_csv = top_services.to_csv()
st.download_button("Télécharger Top 10", top10_csv)

```

**Cache Streamlit** :

```python
@st.cache_data
def load_latest_data():
    # Cache les données pour éviter rechargements
    return df, kpis, monthly_df

```

---

## ☁️ **Configuration Cloud**

### **AWS - Services Utilisés**

**1. Cost Explorer**

- API : `ce:GetCostAndUsage`
- Granularité : Daily / Monthly
- Dimensions : Service, Region, LinkedAccount
- Gratuit : 12 mois Free Tier
- Activation : 24-48h de délai

**2. Amazon S3**

- Bucket : `finops-dashboard-data`
- Régions : `us-east-1` (recommandé)
- Stockage : ~250 KB/mois (données CSV)
- Coût : ~$0.01/mois

**3. IAM (Identity and Access Management)**

- Utilisateur : `finops_user`
- Policies :
    
    ```json
    {  "Version": "2012-10-17",  "Statement": [    {      "Effect": "Allow",      "Action": [        "ce:GetCostAndUsage",        "ce:GetCostForecast",        "ce:GetDimensionValues"      ],      "Resource": "*"    },    {      "Effect": "Allow",      "Action": [        "s3:PutObject",        "s3:GetObject",        "s3:ListBucket"      ],      "Resource": [        "arn:aws:s3:::finops-dashboard-data",        "arn:aws:s3:::finops-dashboard-data/*"      ]    }  ]}
    
    ```
    

**Credentials** :

```
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtn...
AWS_REGION=us-east-1
S3_BUCKET_NAME=finops-dashboard-data

```

---

### **Azure - Services Utilisés**

**1. Cost Management API**

- Endpoint : `https://management.azure.com/subscriptions/{id}/providers/Microsoft.CostManagement/query`
- Scope : Subscription level
- Granularité : Daily
- Dimensions : ServiceName, ResourceLocation, SubscriptionName

**2. Service Principal (App Registration)**

- Nom : `finops-cost-reader`
- Type : Application
- Authentification : Client Secret
- Permissions : Cost Management Reader

**3. Azure Active Directory (Entra ID)**

- Tenant ID : Organisation Azure
- Client ID : Application ID
- Client Secret : Généré lors création

**Credentials** :

```
AZURE_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AZURE_CLIENT_SECRET=votre_secret_azure
AZURE_SUBSCRIPTION_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

```

**Configuration RBAC** :

```
Subscription → Access Control (IAM)
→ Add role assignment
→ Role: Cost Management Reader
→ Assign to: finops-cost-reader

```

---

## 🤖 **Orchestration Airflow - Configuration Complète**

### **Architecture Airflow**

```
┌─────────────────────────────────────────────────────────┐
│                  AIRFLOW WEBSERVER                       │
│              http://localhost:8080                       │
│           (Interface Web + API REST)                     │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                  AIRFLOW SCHEDULER                       │
│         (Déclenchement des DAGs selon schedule)          │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                   POSTGRESQL DB                          │
│          (Métadonnées, état des DAGs, logs)             │
└─────────────────────────────────────────────────────────┘

```

### **DAG Principal : `finops_cost_analysis_pipeline`**

**Configuration** :

```python
default_args = {
    'owner': 'finops-team',
    'depends_on_past': False,
    'email': ['admin@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'finops_cost_analysis_pipeline',
    default_args=default_args,
    description='Pipeline ETL multi-cloud cost analysis',
    schedule_interval='0 8 * * *',  # Tous les jours à 8h
    start_date=days_ago(1),
    catchup=False,
    tags=['finops', 'aws', 'azure', 'costs'],
)

```

**Tâches** :

```python
# Tâche 1 : Extraction
task_extract = PythonOperator(
    task_id='extract_costs_task',
    python_callable=extract_costs,
    dag=dag,
)

# Tâche 2 : Transformation
task_transform = PythonOperator(
    task_id='transform_costs_task',
    python_callable=transform_costs,
    dag=dag,
)

# Tâche 3 : Upload S3
task_upload = PythonOperator(
    task_id='upload_to_s3_task',
    python_callable=upload_to_s3,
    dag=dag,
)

# Tâche 4 : Notification
task_notify = PythonOperator(
    task_id='send_notification_task',
    python_callable=send_notification,
    dag=dag,
)

# Dépendances
task_extract >> task_transform >> task_upload >> task_notify

```

**Gestion des Erreurs** :

- Retry automatique : 2 fois, délai 5 min
- Email en cas d'échec (si configuré)
- Logs détaillés dans Airflow UI

---

### **DAG Secondaire : `finops_s3_cleanup`**

**Configuration** :

```python
schedule_interval='0 2 * * 0'  # Dimanche à 2h du matin

```

**Fonction** :

```python
def cleanup_old_files(**context):
    """Supprime fichiers S3 > 30 jours"""
    cutoff_date = datetime.now() - timedelta(days=30)
    s3 = boto3.client('s3')

    response = s3.list_objects_v2(Bucket=bucket)
    for obj in response['Contents']:
        if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
            s3.delete_object(Bucket=bucket, Key=obj['Key'])

```

---

### **Docker Compose Airflow**

**Services** :

```yaml
services:
  postgres:         # Base de données
  airflow-webserver:  # Interface web (port 8080)
  airflow-scheduler:  # Planificateur
  airflow-init:     # Initialisation DB + user admin

```

**Volumes Montés** :

```yaml
volumes:
  - ./dags:/opt/airflow/dags              # DAGs
  - ./logs:/opt/airflow/logs              # Logs
  - ./plugins:/opt/airflow/plugins        # Plugins
  - ../data:/opt/airflow/data             # Données
  - ../scripts:/opt/airflow/scripts       # Scripts Python

```

---

## 📈 **Données Collectées & Métriques**

### **Schema des Données Brutes**

```python
# Structure CSV brut (data/raw/)
{
    'Date': '2025-10-26',              # Date YYYY-MM-DD
    'Cloud': 'AWS',                    # AWS | Azure
    'Service': 'Amazon EC2',           # Nom du service
    'Region': 'us-east-1',             # Région cloud
    'AccountName': 'Production',       # Nom du compte
    'AccountId': '123456789012',       # ID du compte
    'Cost': 15.50,                     # Coût en USD
    'Currency': 'USD'                  # Devise
}

```

### **Schema des Données Enrichies**

```python
# Structure CSV enrichi (data/processed/)
{
    # Colonnes originales
    'Date': datetime,
    'Cloud': str,
    'Service': str,
    'Region': str,
    'AccountName': str,
    'AccountId': str,
    'Cost': float,
    'Currency': str,

    # Dimensions temporelles ajoutées
    'Year': int,                       # 2025
    'Month': int,

```
