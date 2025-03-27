from PIL import Image, ImageDraw, ImageFont
import os
import math

# Créer les dossiers nécessaires s'ils n'existent pas
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Dossiers d'icônes
icons_dir = os.path.join("yaktaa", "assets", "icons")
items_dir = os.path.join(icons_dir, "items")
ensure_dir(items_dir)

# Créer une icône simple avec du texte
def create_text_icon(path, text, bg_color=(50, 50, 50, 255), text_color=(255, 255, 255, 255), size=(64, 64)):
    img = Image.new('RGBA', size, bg_color)
    draw = ImageDraw.Draw(img)
    
    # Calculer la taille du texte pour le centrer
    text_width = len(text) * 7  # Approximation simple
    text_x = (size[0] - text_width) // 2
    text_y = (size[1] - 10) // 2
    
    # Dessiner le texte
    draw.text((text_x, text_y), text, fill=text_color)
    
    # Sauvegarder l'image
    img.save(path)
    print(f"Icône créée: {path}")

# Créer une icône générique
def create_generic_icon(path, icon_type, color=(100, 100, 200, 255), size=(64, 64)):
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Dessiner un fond arrondi
    draw.rectangle((5, 5, size[0]-5, size[1]-5), fill=color, outline=(255, 255, 255, 128), width=1)
    
    # Dessiner un symbole en fonction du type
    if "credit" in path:
        # Symbole de crédit (¤)
        draw.text((25, 20), "¤", fill=(255, 255, 0, 255), font=None, size=30)
    elif "enter" in path:
        # Flèche vers la droite
        draw.polygon([(20, 32), (40, 20), (40, 44)], fill=(255, 255, 255, 255))
    elif "exit" in path:
        # Flèche vers la gauche
        draw.polygon([(44, 32), (24, 20), (24, 44)], fill=(255, 255, 255, 255))
    elif "help" in path:
        # Point d'interrogation
        draw.text((25, 15), "?", fill=(255, 255, 255, 255), font=None, size=30)
    elif "generic" in path:
        # Boîte simple
        draw.rectangle((15, 15, 49, 49), fill=(200, 200, 200, 255))
    
    # Sauvegarder l'image
    img.save(path)
    print(f"Icône créée: {path}")

# Créer une icône d'arme
def create_weapon_icon(path, weapon_type, color=(200, 50, 50, 255), size=(64, 64)):
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if weapon_type == "ranged":
        # Dessiner une arme à distance simple (comme un pistolet)
        # Corps du pistolet
        draw.rectangle((10, 25, 40, 35), fill=color)
        # Canon
        draw.rectangle((40, 28, 55, 32), fill=color)
        # Poignée
        draw.rectangle((15, 35, 25, 50), fill=color)
        # Gâchette
        draw.rectangle((30, 35, 35, 40), fill=color)
    elif weapon_type == "melee":
        # Dessiner une arme de mêlée simple (comme une épée)
        # Lame
        draw.polygon([(20, 10), (45, 35), (40, 40), (15, 15)], fill=color)
        # Garde
        draw.rectangle((15, 40, 40, 45), fill=color)
        # Poignée
        draw.rectangle((25, 45, 30, 55), fill=color)
    
    # Sauvegarder l'image
    img.save(path)
    print(f"Icône créée: {path}")

# Créer une icône de hardware
def create_hardware_icon(path, hardware_type, color=(50, 150, 250, 255), size=(64, 64)):
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if hardware_type == "computer":
        # Écran
        draw.rectangle((10, 10, 54, 40), fill=color)
        # Base
        draw.rectangle((25, 40, 39, 45), fill=color)
        # Clavier
        draw.rectangle((15, 45, 49, 54), fill=color)
    elif hardware_type == "router":
        # Boîtier
        draw.rectangle((15, 25, 49, 45), fill=color)
        # Antennes
        draw.rectangle((20, 10, 22, 25), fill=color)
        draw.rectangle((32, 5, 34, 25), fill=color)
        draw.rectangle((44, 10, 46, 25), fill=color)
    elif hardware_type == "server":
        # Serveur rack
        draw.rectangle((15, 10, 49, 54), fill=color)
        # Détails
        for i in range(5):
            y = 15 + i * 8
            draw.rectangle((20, y, 44, y+5), fill=(30, 100, 200, 255))
    elif hardware_type == "terminal":
        # Écran
        draw.rectangle((10, 10, 54, 45), fill=color)
        # Clavier intégré
        draw.rectangle((15, 45, 49, 54), fill=(30, 100, 200, 255))
    elif hardware_type == "mobile":
        # Smartphone
        draw.rectangle((22, 10, 42, 54), fill=color)
        # Écran
        draw.rectangle((24, 15, 40, 45), fill=(30, 100, 200, 255))
        # Bouton
        draw.ellipse((29, 47, 35, 53), fill=(200, 200, 200, 255))
    
    # Sauvegarder l'image
    img.save(path)
    print(f"Icône créée: {path}")

# Créer une icône de consommable
def create_consumable_icon(path, consumable_type, color=(50, 200, 50, 255), size=(64, 64)):
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if consumable_type == "health":
        # Croix médicale
        draw.rectangle((25, 10, 39, 54), fill=color)
        draw.rectangle((10, 25, 54, 39), fill=color)
    elif consumable_type == "boost":
        # Flèche vers le haut
        draw.polygon([(32, 10), (10, 40), (25, 40), (25, 54), (39, 54), (39, 40), (54, 40)], fill=color)
    elif consumable_type == "food":
        # Hamburger stylisé
        draw.ellipse((15, 20, 49, 54), fill=(200, 150, 100, 255))  # Pain
        draw.rectangle((15, 30, 49, 40), fill=(150, 100, 50, 255))  # Viande
        draw.rectangle((15, 25, 49, 30), fill=(50, 200, 50, 255))   # Salade
    
    # Sauvegarder l'image
    img.save(path)
    print(f"Icône créée: {path}")

# Créer une icône de software
def create_software_icon(path, software_type, color=(150, 50, 200, 255), size=(64, 64)):
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Base commune (disquette/CD)
    draw.rectangle((10, 10, 54, 54), fill=color)
    
    if software_type == "security":
        # Bouclier
        draw.polygon([(32, 15), (15, 25), (15, 40), (32, 50), (49, 40), (49, 25)], fill=(100, 30, 150, 255))
        # Serrure
        draw.ellipse((27, 30, 37, 40), fill=(200, 200, 200, 255))
    elif software_type == "hack":
        # Symbole de hacking (matrice de points)
        for x in range(5):
            for y in range(5):
                if (x + y) % 2 == 0:
                    draw.ellipse((15 + x*8, 15 + y*8, 19 + x*8, 19 + y*8), fill=(200, 200, 200, 255))
    elif software_type == "utility":
        # Clé à molette
        draw.polygon([(20, 20), (25, 15), (44, 34), (49, 39), (44, 44), (39, 49), (34, 44), (15, 25)], fill=(200, 200, 200, 255))
    elif software_type == "virus":
        # Symbole biohazard simplifié
        draw.ellipse((22, 22, 42, 42), fill=(200, 50, 50, 255))
        for i in range(3):
            angle = i * 2.09  # 120 degrés en radians
            x1 = 32 + 20 * math.cos(angle)
            y1 = 32 + 20 * math.sin(angle)
            draw.ellipse((x1-5, y1-5, x1+5, y1+5), fill=(200, 50, 50, 255))
    
    # Sauvegarder l'image
    img.save(path)
    print(f"Icône créée: {path}")

# Créer une icône d'implant
def create_implant_icon(path, implant_type, color=(200, 150, 50, 255), size=(64, 64)):
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if implant_type == "neural":
        # Cerveau stylisé
        draw.ellipse((15, 10, 49, 44), fill=color)
        # Connexions
        draw.line((20, 44, 15, 54), fill=color, width=3)
        draw.line((32, 44, 32, 54), fill=color, width=3)
        draw.line((44, 44, 49, 54), fill=color, width=3)
    elif implant_type == "physical":
        # Bras robotique
        draw.rectangle((25, 10, 39, 30), fill=color)  # Épaule
        draw.rectangle((20, 30, 44, 40), fill=color)  # Coude
        draw.rectangle((15, 40, 30, 54), fill=color)  # Avant-bras
    elif implant_type == "sensory":
        # Œil cybernétique
        draw.ellipse((15, 15, 49, 49), fill=color)
        draw.ellipse((25, 25, 39, 39), fill=(200, 50, 50, 255))
        draw.ellipse((29, 29, 35, 35), fill=(0, 0, 0, 255))
    
    # Sauvegarder l'image
    img.save(path)
    print(f"Icône créée: {path}")

# Créer les icônes génériques
create_generic_icon(os.path.join(icons_dir, "credit.png"), "credit", color=(255, 215, 0, 255))
create_generic_icon(os.path.join(icons_dir, "enter.png"), "enter", color=(50, 200, 50, 255))
create_generic_icon(os.path.join(icons_dir, "exit.png"), "exit", color=(200, 50, 50, 255))
create_generic_icon(os.path.join(icons_dir, "help.png"), "help", color=(50, 50, 200, 255))
create_generic_icon(os.path.join(items_dir, "generic.png"), "generic", color=(150, 150, 150, 255))

# Créer les icônes d'objets
# Hardware
for hardware_type in ["computer", "router", "server", "terminal", "mobile"]:
    create_hardware_icon(os.path.join(items_dir, f"hardware_{hardware_type}.png"), hardware_type)

# Consommables
for consumable_type in ["health", "boost", "food"]:
    create_consumable_icon(os.path.join(items_dir, f"consumable_{consumable_type}.png"), consumable_type)

# Software
for software_type in ["security", "hack", "utility", "virus"]:
    create_software_icon(os.path.join(items_dir, f"software_{software_type}.png"), software_type)

# Implants
for implant_type in ["neural", "physical", "sensory"]:
    create_implant_icon(os.path.join(items_dir, f"implant_{implant_type}.png"), implant_type)

print("Toutes les icônes ont été créées avec succès!")
