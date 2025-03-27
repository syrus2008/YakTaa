# Script PowerShell final pour la création du package YakTaa
# Utilise les fichiers corrigés yaktaa_fixed.spec et yaktaa_fixed.iss

# Configuration
$ErrorActionPreference = "Stop" # Arrêter en cas d'erreur
$ProjectRoot = $PSScriptRoot
$SpecFile = Join-Path $ProjectRoot "yaktaa_fixed.spec"
$IssFile = Join-Path $ProjectRoot "yaktaa_fixed.iss"
$OutputDir = Join-Path $ProjectRoot "Output"
$DistDir = Join-Path $ProjectRoot "dist"

# Fonction pour créer le dossier de sortie
function Ensure-Directory {
    param(
        [string]$Path
    )
    
    if (-not (Test-Path $Path)) {
        Write-Host "Création du dossier $Path" -ForegroundColor Yellow
        New-Item -Path $Path -ItemType Directory -Force | Out-Null
    }
}

# Fonction pour nettoyer les anciens fichiers de build
function Clean-BuildFiles {
    Write-Host "Nettoyage des anciens fichiers de build..." -ForegroundColor Yellow
    
    if (Test-Path (Join-Path $ProjectRoot "build")) {
        Remove-Item -Path (Join-Path $ProjectRoot "build") -Recurse -Force
    }
    
    if (Test-Path $DistDir) {
        Remove-Item -Path $DistDir -Recurse -Force
    }
}

# Fonction pour construire les exécutables avec PyInstaller
function Build-Executables {
    Write-Host "Construction des exécutables avec PyInstaller..." -ForegroundColor Cyan
    
    python -m PyInstaller --clean $SpecFile
    
    if (Test-Path (Join-Path $DistDir "YakTaa\YakTaa.exe")) {
        Write-Host "Exécutable YakTaa créé avec succès!" -ForegroundColor Green
    } else {
        Write-Host "Échec de création de l'exécutable YakTaa" -ForegroundColor Red
        exit 1
    }
    
    if (Test-Path (Join-Path $DistDir "YakTaaWorldEditor\YakTaaWorldEditor.exe")) {
        Write-Host "Exécutable YakTaa World Editor créé avec succès!" -ForegroundColor Green
    } else {
        Write-Host "Échec de création de l'exécutable YakTaa World Editor" -ForegroundColor Red
        exit 1
    }
}

# Fonction pour créer l'installateur avec Inno Setup
function Build-Installer {
    Write-Host "Création de l'installateur avec Inno Setup..." -ForegroundColor Cyan
    
    $innoSetupPath = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
    if (-not (Test-Path $innoSetupPath)) {
        Write-Host "Inno Setup introuvable. Vérifiez qu'il est installé." -ForegroundColor Red
        exit 1
    }
    
    Ensure-Directory -Path $OutputDir
    
    & $innoSetupPath $IssFile "/O$OutputDir"
    
    $setupFiles = Get-ChildItem -Path $OutputDir -Filter "*.exe"
    if ($setupFiles.Count -gt 0) {
        Write-Host "Installateur créé avec succès: $($setupFiles[0].FullName)" -ForegroundColor Green
    } else {
        Write-Host "Échec de création de l'installateur" -ForegroundColor Red
        exit 1
    }
}

# Programme principal
Write-Host "=== Création du package YakTaa (Version finale) ===" -ForegroundColor Magenta

try {
    # Vérifier que les fichiers nécessaires existent
    if (-not (Test-Path $SpecFile)) {
        Write-Host "Erreur: Le fichier spec $SpecFile n'existe pas!" -ForegroundColor Red
        exit 1
    }
    
    if (-not (Test-Path $IssFile)) {
        Write-Host "Erreur: Le fichier ISS $IssFile n'existe pas!" -ForegroundColor Red
        exit 1
    }
    
    # Nettoyer les anciens fichiers
    Clean-BuildFiles
    
    # Construire les exécutables
    Build-Executables
    
    # Créer l'installateur
    Build-Installer
    
    Write-Host "=== Création du package YakTaa terminée avec succès! ===" -ForegroundColor Magenta
    Write-Host "L'installateur se trouve dans: $OutputDir" -ForegroundColor Green
} catch {
    Write-Host "Une erreur s'est produite: $_" -ForegroundColor Red
    exit 1
}
