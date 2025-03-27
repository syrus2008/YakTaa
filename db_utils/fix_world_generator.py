#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour corriger l'erreur de syntaxe dans world_generator.py
"""

import re

def fix_f_string_backslash():
    """Corrige l'erreur de syntaxe dans world_generator.py"""
    file_path = "world_generator.py"
    
    # Lire le contenu du fichier
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Corriger la ligne problématique
    # Remplacer l'échappement de l'apostrophe par des guillemets doubles
    pattern = r"description \+= f\" \{self\.random\.choice\(\['Un lieu où la loi n\\'existe plus\."
    replacement = r'description += f" {self.random.choice(["Un lieu où la loi n\'existe plus."'
    
    # Appliquer la correction
    new_content = re.sub(pattern, replacement, content)
    
    # Écrire le contenu corrigé
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"Correction appliquée à {file_path}")

if __name__ == "__main__":
    fix_f_string_backslash()
