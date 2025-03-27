#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour corriger l'erreur de syntaxe dans world_generator.py
"""

def fix_syntax_error():
    """Corrige l'erreur de syntaxe dans world_generator.py"""
    file_path = "world_generator.py"
    
    # Lire le contenu du fichier
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Trouver et corriger la ligne problématique
    for i, line in enumerate(lines):
        if "Un lieu où la loi n\\" in line:
            # Remplacer la ligne problématique par une version corrigée
            lines[i] = '                description += f" {self.random.choice([\'Un lieu où la loi est absente.\', \'Dangereux pour les non-initiés.\', \'La survie y est une lutte quotidienne.\'])}"' + '\n'
            print(f"Ligne {i+1} corrigée")
            break
    
    # Écrire le contenu corrigé
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    
    print(f"Correction appliquée à {file_path}")

if __name__ == "__main__":
    fix_syntax_error()
