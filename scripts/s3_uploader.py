"""
Module pour uploader les données vers S3
"""

import boto3
import os
from datetime import datetime
from dotenv import load_dotenv
import glob
import logging

load_dotenv()

logger = logging.getLogger(__name__)


class S3Uploader:
    """Classe pour gérer les uploads vers S3"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME non défini dans .env")
    
    def upload_file(self, local_path, s3_key):
        """
        Upload un fichier vers S3
        
        Args:
            local_path: Chemin local du fichier
            s3_key: Clé S3 (chemin dans le bucket)
        """
        try:
            self.s3_client.upload_file(local_path, self.bucket_name, s3_key)
            logger.info(f"✅ Uploadé : {local_path} → s3://{self.bucket_name}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur upload {local_path}: {e}")
            return False
    
    def upload_latest_data(self):
        """Upload les derniers fichiers transformés vers S3"""
        
        logger.info("📤 Début de l'upload vers S3...")
        
        today = datetime.now().strftime('%Y-%m-%d')
        uploaded_count = 0
        
        # Fichiers à uploader
        file_patterns = [
            ('data/processed/costs_enriched_*.csv', 'processed/daily/'),
            ('data/processed/daily_costs_*.csv', 'processed/daily/'),
            ('data/processed/top10_services_*.csv', 'reports/'),
            ('data/processed/monthly_evolution_*.csv', 'reports/'),
            ('data/processed/kpis_*.json', 'kpis/')
        ]
        
        for pattern, s3_folder in file_patterns:
            files = glob.glob(pattern)
            if files:
                # Prendre le fichier le plus récent
                latest_file = max(files, key=os.path.getctime)
                filename = os.path.basename(latest_file)
                s3_key = f"{s3_folder}{today}/{filename}"
                
                if self.upload_file(latest_file, s3_key):
                    uploaded_count += 1
        
        logger.info(f"✅ Upload terminé : {uploaded_count} fichiers uploadés")
        return uploaded_count


def main():
    """Test du module"""
    logging.basicConfig(level=logging.INFO)
    
    uploader = S3Uploader()
    uploader.upload_latest_data()


if __name__ == "__main__":
    main()