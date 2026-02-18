import os
import cv2
import random
import unicodedata
import shutil
from flask import Flask, render_template, request, session, redirect, url_for


# à faire :
# - supprimer les images temporaires en début de session (utiliser/créer un worker)



app = Flask(__name__)
app.secret_key = "devops_secret_key"

IMAGE_FOLDER = 'images'
TEMP_FOLDER = 'static/temp'
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

os.makedirs(TEMP_FOLDER, exist_ok=True)

def normalize_text(text):
    """Supprime les accents, les majuscules et les espaces superflus."""
    if not text: return ""
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
    return text.lower().strip()

def get_random_image():
    if not os.path.exists(IMAGE_FOLDER) or not os.listdir(IMAGE_FOLDER):
        return None # Évite de planter si le dossier est vide
    files = [f for f in os.listdir(IMAGE_FOLDER) if os.path.splitext(f)[1].lower() in ALLOWED_EXTENSIONS]
    return random.choice(files) if files else None

def apply_blur(image_name, attempt, won):
    img_path = os.path.join(IMAGE_FOLDER, image_name)
    img = cv2.imread(img_path)
    
    if won:
        blur_level = 1 # Image nette
    else:
        # Dégressivité du flou : 1: 91, 2: 61, 3: 31, 4: 11, 5: 1
        blur_level = max(1, 121 - (attempt * 30))
        if blur_level % 2 == 0: blur_level += 1
    
    if blur_level > 1:
        img = cv2.GaussianBlur(img, (blur_level, blur_level), 0)
    
    temp_name = f"display_image.png" # Nom fixe pour éviter d'accumuler les fichiers
    cv2.imwrite(os.path.join(TEMP_FOLDER, temp_name), img)
    return temp_name


# Fonctions vérifications pour /health
# pas trop d'inspirations sur les tests à faire donc on fait vérification dossier images, écriture dans temp et check espace disque

def check_image_folder():
    # Correction : On vérifie que le dossier EXISTE et n'est pas vide
    if os.path.exists(IMAGE_FOLDER) and len(os.listdir(IMAGE_FOLDER)) > 0:
        return True
    return False

def check_temp_folder():
    return os.access(TEMP_FOLDER, os.W_OK)

def check_disk_space():
    total, used, free = shutil.disk_usage("/")
    return free > 100 * 1024 * 1024 # 100Mo libre

@app.route("/health")
def health():
    checks = {
        "image_folder": check_image_folder(),
        "temp_folder": check_temp_folder(),
        "disk_space": check_disk_space()
    }
    status_overall = "healthy" if all(checks.values()) else "unhealthy"
    status_code = 200 if status_overall == "healthy" else 503

    return {
        "status": status_overall,
        "checks": checks
    }, status_code


@app.route("/", methods=["GET", "POST"])
def index():
    if 'target' not in session:
        session['target'] = get_random_image()
        session['attempts'] = 1
        session['won'] = False

    target_image = session['target']
    if not target_image:
        return "Aucune image valide disponible dans le dossier /images.", 503
    message = ""
    
    if request.method == "POST" and not session['won']:
        guess = normalize_text(request.form.get("guess", ""))
        
        # Extraire les parties du nom de fichier (ex: "Theodore_Roosevelt.jpg" -> ["theodore", "roosevelt"])
        filename_raw = os.path.splitext(target_image)[0]
        valid_parts = [normalize_text(p) for p in filename_raw.split('_')]

        if guess in valid_parts:
            session['won'] = True
            message = "Félicitations !! 🎉"
        else:
            session['attempts'] += 1
            message = "Raté ! Réessaie."

    current_image = apply_blur(target_image, session['attempts'], session['won'])
    
    return render_template("index.html", 
                           image=current_image, 
                           message=message, 
                           won=session['won'])

@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for('index'))



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)