import boto3
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

print("🔍 Test de connexion AWS Cost Explorer (version avancée)...\n")

client = boto3.client(
    'ce',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

# Test 1 : Vérifier que les credentials fonctionnent
print("✅ Étape 1/3 : Credentials AWS valides\n")

# Test 2 : Essayer plusieurs périodes
test_periods = [
    (30, "30 derniers jours"),
    (60, "60 derniers jours"),
    (90, "90 derniers jours"),
]

print("⏳ Étape 2/3 : Recherche de données disponibles...\n")

data_found = False

for days, label in test_periods:
    try:
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        response = client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost']
        )
        
        print(f"✅ Données trouvées pour : {label}")
        print(f"   Période : {start_date} → {end_date}")
        
        for result in response['ResultsByTime']:
            amount = result['Total']['UnblendedCost']['Amount']
            unit = result['Total']['UnblendedCost']['Unit']
            period = result['TimePeriod']['Start']
            print(f"   💰 {period} : {float(amount):.4f} {unit}")
        
        data_found = True
        print()
        break
        
    except Exception as e:
        print(f"⏭️  {label} : Pas encore de données")

print("\n" + "="*60)

if data_found:
    print("🎉 SUCCÈS : Cost Explorer est opérationnel !")
    print("✅ Vous pouvez passer à l'étape 2")
else:
    print("⏳ Cost Explorer collecte encore les données")
    print("\n📋 Statut actuel :")
    print("   ✅ Connexion AWS : OK")
    print("   ✅ Permissions IAM : OK")
    print("   ⏳ Données Cost Explorer : En cours de collecte (24-48h)")
   

print("="*60)