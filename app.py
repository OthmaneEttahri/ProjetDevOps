import os
import cv2
import random
import unicodedata
from flask import Flask, render_template, request, session, redirect, url_for

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

@app.route("/", methods=["GET", "POST"])
def index():
    if 'target' not in session:
        session['target'] = get_random_image()
        session['attempts'] = 1
        session['won'] = False

    target_image = session['target']
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