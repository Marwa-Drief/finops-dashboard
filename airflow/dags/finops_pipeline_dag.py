"""
DAG Airflow - FinOps Cost Analysis Pipeline
ETL complet : Extraction → Transformation → Export S3
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
import sys
import os

# Ajouter les scripts au path
sys.path.insert(0, '/opt/airflow/scripts')

from s3_uploader import S3Uploader

# Configuration du DAG
default_args = {
    'owner': 'finops-team',
    'depends_on_past': False,
    'email': ['votre-email@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'finops_cost_analysis_pipeline',
    default_args=default_args,
    description='Pipeline ETL complet pour analyse des coûts cloud',
    schedule_interval='0 8 * * *',  # Tous les jours à 8h
    start_date=days_ago(1),
    catchup=False,
    tags=['finops', 'aws', 'costs', 'etl'],
)


def extract_costs(**context):
    """Tâche d'extraction multi-cloud"""
    import subprocess
    
    print("🌐 Extraction multi-cloud...")
    
    result = subprocess.run(
        ['python', '/opt/airflow/scripts/extract_multicloud_costs.py'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise Exception(f"Erreur extraction : {result.stderr}")
    
    print("✅ Extraction multi-cloud terminée")
    return "extraction_success"


def transform_costs(**context):
    """Tâche de transformation des données"""
    import subprocess
    
    print("🔄 Transformation des données...")
    
    result = subprocess.run(
        ['python', '/opt/airflow/scripts/transform_costs.py'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise Exception(f"Erreur transformation : {result.stderr}")
    
    print("✅ Transformation terminée")
    return "transformation_success"


def upload_to_s3(**context):
    """Tâche d'upload vers S3"""
    print("📤 Upload vers S3...")
    
    uploader = S3Uploader()
    count = uploader.upload_latest_data()
    
    if count == 0:
        raise Exception("Aucun fichier uploadé vers S3")
    
    print(f"✅ {count} fichiers uploadés vers S3")
    return f"uploaded_{count}_files"


def send_notification(**context):
    """Envoie une notification de succès"""
    import json
    
    ti = context['task_instance']
    
    # Récupérer les résultats des tâches précédentes
    extraction_result = ti.xcom_pull(task_ids='extract_costs_task')
    transformation_result = ti.xcom_pull(task_ids='transform_costs_task')
    upload_result = ti.xcom_pull(task_ids='upload_to_s3_task')
    
    print("="*60)
    print("📊 PIPELINE FINOPS - RÉSUMÉ D'EXÉCUTION")
    print("="*60)
    print(f"📅 Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"✅ Extraction : {extraction_result}")
    print(f"✅ Transformation : {transformation_result}")
    print(f"✅ Upload S3 : {upload_result}")
    print("="*60)
    
    return "pipeline_complete"


# Définition des tâches
task_extract = PythonOperator(
    task_id='extract_costs_task',
    python_callable=extract_costs,
    dag=dag,
)

task_transform = PythonOperator(
    task_id='transform_costs_task',
    python_callable=transform_costs,
    dag=dag,
)

task_upload_s3 = PythonOperator(
    task_id='upload_to_s3_task',
    python_callable=upload_to_s3,
    dag=dag,
)

task_notify = PythonOperator(
    task_id='send_notification_task',
    python_callable=send_notification,
    dag=dag,
)

# Définir les dépendances (ordre d'exécution)
task_extract >> task_transform >> task_upload_s3 >> task_notify