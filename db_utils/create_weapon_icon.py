from PIL import Image, ImageDraw
import os

# Créer les dossiers nécessaires s'ils n'existent pas
icons_dir = os.path.join("yaktaa", "assets", "icons", "items")
os.makedirs(icons_dir, exist_ok=True)

# Créer une icône pour les armes à distance
def create_weapon_icon(name, color):
    # Créer une image 64x64 avec fond transparent
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if name == "weapon_ranged":
        # Dessiner une arme à distance simple (comme un pistolet)
        # Corps du pistolet
        draw.rectangle((10, 25, 40, 35), fill=color)
        # Canon
        draw.rectangle((40, 28, 55, 32), fill=color)
        # Poignée
        draw.rectangle((15, 35, 25, 50), fill=color)
        # Gâchette
        draw.rectangle((30, 35, 35, 40), fill=color)
    elif name == "weapon_melee":
        # Dessiner une arme de mêlée simple (comme une épée)
        # Lame
        draw.polygon([(20, 10), (45, 35), (40, 40), (15, 15)], fill=color)
        # Garde
        draw.rectangle((15, 40, 40, 45), fill=color)
        # Poignée
        draw.rectangle((25, 45, 30, 55), fill=color)
    
    # Sauvegarder l'image
    img.save(os.path.join(icons_dir, f"{name}.png"))
    print(f"Icône {name}.png créée avec succès")

# Créer les icônes
create_weapon_icon("weapon_ranged", (200, 50, 50, 255))  # Rouge
create_weapon_icon("weapon_melee", (50, 50, 200, 255))   # Bleu
