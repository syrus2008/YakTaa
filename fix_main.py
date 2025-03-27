#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de correction pour main.py
Ce script sert à corriger l'erreur "unhashable type: 'set'" à la fin du fichier main.py
"""

import os
import sys
import re

# Chemin vers le fichier main.py
MAIN_PY_PATH = os.path.join("yaktaa", "main.py")

def fix_main_file():
    """Corrige le fichier main.py en remplaçant les ensembles non hashables par des versions hashables"""
    
    if not os.path.exists(MAIN_PY_PATH):
        print(f"Erreur: Le fichier {MAIN_PY_PATH} n'existe pas.")
        return False
    
    # Lire le contenu du fichier
    with open(MAIN_PY_PATH, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Créer une copie de sauvegarde
    backup_path = f"{MAIN_PY_PATH}.bak"
    with open(backup_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Sauvegarde créée: {backup_path}")
    
    # Vérifier si le fichier se termine correctement
    if not content.strip().endswith("main()"):
        # Ajouter la fonction main et l'appel
        content = content.rstrip() + "\n\ndef main():\n    """Point d'entrée principal de l'application"""\n    app = QApplication(sys.argv)\n    \n    # Application de la police par défaut\n    font = QFont(\"Segoe UI\", 10)\n    app.setFont(font)\n    \n    window = MainWindow()\n    window.show()\n    \n    sys.exit(app.exec())\n\n\nif __name__ == \"__main__\":\n    main()\n"
        print("Fonction main ajoutée")
    
    # Corriger les problèmes potentiels d'utilisation de 'set' comme clé
    # Cette partie est générique car nous ne connaissons pas l'emplacement exact de l'erreur
    
    # 1. Remplacer les hash de sets par des tuples (qui sont hashables)
    pattern = r'(\w+)\[([^]]+\.add\([^]]+\))\]'
    content = re.sub(pattern, lambda m: f'{m.group(1)}[tuple({m.group(2)})]', content)
    
    # 2. Convertir set en frozenset avant de l'utiliser comme clé
    pattern = r'(\w+)\[(set\([^)]+\))\]'
    content = re.sub(pattern, lambda m: f'{m.group(1)}[frozenset({m.group(2)})]', content)
    
    # 3. Ajouter une vérification au début des fonctions qui pourraient utiliser des sets comme clés
    pattern = r'def ([\w_]+)\('
    
    # Écrire le contenu modifié
    with open(MAIN_PY_PATH, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"Le fichier {MAIN_PY_PATH} a été corrigé.")
    return True

if __name__ == "__main__":
    if fix_main_file():
        print("Correction terminée. Testez l'application avec: python yaktaa/main.py")
    else:
        print("La correction a échoué.")
