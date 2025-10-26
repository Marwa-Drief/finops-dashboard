"""
Vérifier les fichiers dans S3
"""

import boto3
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

bucket = os.getenv('S3_BUCKET_NAME')

print(f"📦 Contenu du bucket : {bucket}\n")
print("="*60)

response = s3.list_objects_v2(Bucket=bucket)

if 'Contents' not in response:
    print("❌ Aucun fichier trouvé dans le bucket")
else:
    for obj in response['Contents']:
        size_mb = obj['Size'] / 1024 / 1024
        print(f"📄 {obj['Key']}")
        print(f"   Taille : {size_mb:.2f} MB")
        print(f"   Date : {obj['LastModified']}")
        print()

print("="*60)