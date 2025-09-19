import os
import hashlib
import shutil
from PIL import Image, ExifTags
from datetime import datetime

# Extensions courantes de photos
EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".tiff", ".bmp", ".heic", ".webp", ".mp4", ".mov"}

def get_file_hash(path):
    """Retourne le hash SHA256 d’un fichier"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def get_exif_date(path):
    """Récupère la date EXIF si possible, sinon date de modification"""
    try:
        img = Image.open(path)
        exif = img._getexif()
        if exif:
            for tag, value in exif.items():
                tag_name = ExifTags.TAGS.get(tag, tag)
                if tag_name == "DateTimeOriginal":
                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    # fallback -> date de modif du fichier
    ts = os.path.getmtime(path)
    return datetime.fromtimestamp(ts)

def organize_photos(src_folder, dest_folder):
    hashes = set()
    for root, _, files in os.walk(src_folder):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in EXTENSIONS:
                continue

            src_path = os.path.join(root, file)
            file_hash = get_file_hash(src_path)

            # Skip si doublon
            if file_hash in hashes:
                print(f"[DUPLICATE] {src_path} supprimé")
                os.remove(src_path)
                continue

            hashes.add(file_hash)

            # Récupérer date
            date = get_exif_date(src_path)
            folder = os.path.join(dest_folder, date.strftime("%Y"), date.strftime("%m"))
            os.makedirs(folder, exist_ok=True)

            dest_path = os.path.join(folder, file)

            # Évite d’écraser un fichier
            counter = 1
            while os.path.exists(dest_path):
                name, ext = os.path.splitext(file)
                dest_path = os.path.join(folder, f"{name}_{counter}{ext}")
                counter += 1

            shutil.move(src_path, dest_path)
            print(f"[OK] {src_path} -> {dest_path}")

if __name__ == "__main__":
    SRC = r"REDACTED"   # dossier source
    DEST = r"REDACTED"    # dossier destination
    organize_photos(SRC, DEST)
