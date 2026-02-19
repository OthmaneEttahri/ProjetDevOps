import os
import time
import json
import signal
import sys
from datetime import datetime


IMAGE_FOLDER = 'images'
TEMP_FOLDER = 'static/temp'
CATALOG_FILE = 'static/catalog.json'

# arret propre ??
def graceful_exit(signum, frame):
    print(f"\n[WORKER] Signal {signum} reçu. Arrêt propre en cours...")
    sys.exit(0)

signal.signal(signal.SIGTERM, graceful_exit)
signal.signal(signal.SIGINT, graceful_exit)

def clean_temp_files(max_age_seconds=600):
    # Supprime les fichiers vieux de plus de X secondes.
    print("[WORKER] Étape 1 : Nettoyage des fichiers temporaires...")
    now = time.time()
    count = 0
    if os.path.exists(TEMP_FOLDER):
        for f in os.listdir(TEMP_FOLDER):
            f_path = os.path.join(TEMP_FOLDER, f)
            if os.stat(f_path).st_mtime < now - max_age_seconds:
                os.remove(f_path)
                count += 1
    print(f"[WORKER] {count} fichiers supprimés.")

def audit_data_quality():
    #Vérifie noms des fichiers images et génére un rapport  json
    print("[WORKER] Étape 2 : Audit de la qualité des données...")
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_images": 0,
        "valid_naming": 0,
        "invalid_files": []
    }
    
    if os.path.exists(IMAGE_FOLDER):
        files = os.listdir(IMAGE_FOLDER)
        report["total_images"] = len(files)
        for f in files:
            name_part = os.path.splitext(f)[0]
            if "_" in name_part:
                report["valid_naming"] += 1
            else:
                report["invalid_files"].append(f)
                
    # Sauvegarde du rapport pour l'API ou monitoring
    with open(CATALOG_FILE, 'w') as jf:
        json.dump(report, jf, indent=4)
    print(f"[WORKER] Audit terminé. {report['valid_naming']}/{report['total_images']} images valides.")

def run_worker():
    print("--- DÉMARRAGE DU WORKER BATCH ---")
    try:
        clean_temp_files()
        audit_data_quality()
        print("--- MISSION TERMINÉE AVEC SUCCÈS ---")
    except Exception as e:
        print(f"[ERROR] Le worker a rencontré un problème : {e}")
        sys.exit(1) # Code 1 indique une erreur en DevOps

if __name__ == "__main__":
    run_worker()