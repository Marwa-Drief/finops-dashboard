#  FinOps Dashboard Multi-Cloud

##  Vue d'ensemble
**Nom** : FinOps Dashboard - Analyse des Coûts Cloud Multi-Compte (AWS + Azure)  
**Objectif** : Pipeline ETL automatisé pour analyser, optimiser et visualiser les coûts cloud multi-providers  
**Valeur Business** : Réduction des coûts cloud de 15-30% via identification des optimisations et anomalies  
**Niveau** : Projet professionnel production-ready  



##  Architecture Technique



##  Structure du projet
```
finops-dashboard/
├── venv/                    # Environnement Python
├── data/
│   ├── raw/                 # Données brutes
│   └── processed/           # Données transformées et KPIs
├── scripts/                 # Scripts ETL
├── airflow/                 # DAGs, logs, Docker
├── logs/                    # Logs pipeline
├── .env                     # Credentials (gitignored)
├── .gitignore
├── dashboard.py             # Streamlit dashboard
└── README.md                # Documentation complète
```

## 🔧 Stack Technique

**Backend & ETL** : Python 3.11, pandas, boto3, azure-mgmt-costmanagement, Airflow 2.7.3, Docker  
**Stockage** : CSV, JSON, Amazon S3  
**Visualisation** : Streamlit, Plotly  
**Cloud Providers** : AWS (Cost Explorer, S3, IAM), Azure (Cost Management API, Service Principal)  

 

##  Workflow Pipeline ETL

1. **Extraction Multi-Cloud** (`extract_multicloud_costs.py`)  
   - AWS Cost Explorer + Azure Cost Management API  
   - Gestion erreurs : fallback avec données simulées ou placeholder  
   - Output : `data/raw/multicloud_costs_YYYYMMDD.csv`

2. **Transformation** (`transform_costs.py`)  
   - Nettoyage, enrichissement, agrégations  
   - Calcul KPIs et détection anomalies  
   - Output : `data/processed/*.csv` et `kpis_*.json`

3. **Upload S3** (`s3_uploader.py`)  
   - Organisation S3 : `processed/`, `reports/`, `kpis/`  
   - Rétention : suppression > 30 jours

4. **Notification / Logs**  
   - Logs détaillés : `logs/pipeline.log`  
   - Rapports texte : `logs/report_*.txt`  
   - Historique exécutions : `logs/execution_history.json`

 

## Dashboard Streamlit

- KPI Cards : Coût total, moyen/jour, tendance, anomalies  
- Graphiques interactifs : évolution journalière, top services, par catégorie, comptes, comparaison multi-cloud  
- Filtres dynamiques : période, cloud, compte, catégorie  
- Export CSV des données filtrées et Top 10 services  

 

##  Configuration Cloud

**AWS** : Access Key + Secret, S3 Bucket `finops-dashboard-data`, IAM Role `finops_user`  
**Azure** : Service Principal `finops-cost-reader`, Cost Management Reader, Tenant/Client IDs + Secret  

 

##  Orchestration Airflow

- DAG principal : `finops_cost_analysis_pipeline` (ETL quotidien 8h00)  
- DAG secondaire : `finops_s3_cleanup` (suppression fichiers S3 >30j)  
- Docker Compose pour Airflow + PostgreSQL  
- Logs & monitoring via Airflow UI  

 

##  Données & KPIs

**Données brutes** : Date, Cloud, Service, Region, AccountName, AccountId, Cost, Currency  
**Données enrichies** : + dimensions temporelles, catégories services, agrégations, KPIs  

 

##  Instructions pour lancer le projet

1. Cloner le repo  
2. Créer `.env` avec credentials AWS/Azure  
3. Installer dependencies : `pip install -r airflow/requirements.txt`  
4. Lancer Airflow avec Docker Compose : `docker-compose up -d`  
5. Exécuter pipeline : `python run_pipeline_now.py`  
6. Lancer dashboard : `streamlit run dashboard.py`  

 

