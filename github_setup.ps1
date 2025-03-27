# Script pour pousser le projet YakTaa sur GitHub et créer une release
# Utilise les outils Git et GitHub CLI (gh)

# Configuration
$ErrorActionPreference = "Stop" # Arrêter en cas d'erreur
$ProjectRoot = $PSScriptRoot
$OutputDir = Join-Path $ProjectRoot "Output"
$RepoName = "YakTaa"

# Fonction pour configurer Git avec l'identité de l'utilisateur
function Configure-GitIdentity {
    Write-Host "Configuration de l'identité Git..." -ForegroundColor Cyan
    
    # Vérifier si l'identité est déjà configurée
    $userEmail = git config --global user.email
    $userName = git config --global user.name
    
    if ([string]::IsNullOrEmpty($userEmail) -or [string]::IsNullOrEmpty($userName)) {
        Write-Host "L'identité Git n'est pas configurée." -ForegroundColor Yellow
        
        if ([string]::IsNullOrEmpty($userEmail)) {
            $email = Read-Host "Entrez votre email pour Git"
            git config --global user.email $email
        }
        
        if ([string]::IsNullOrEmpty($userName)) {
            $name = Read-Host "Entrez votre nom pour Git"
            git config --global user.name $name
        }
        
        Write-Host "Identité Git configurée avec succès!" -ForegroundColor Green
    } else {
        Write-Host "Identité Git déjà configurée: $userName <$userEmail>" -ForegroundColor Green
    }
}

# Fonction pour vérifier si Git est installé et accessible
function Check-Git {
    try {
        # Essayer d'exécuter git
        git --version
        Write-Host "Git est accessible dans le PATH" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "Git n'est pas accessible dans le PATH, recherche de l'installation..." -ForegroundColor Yellow
        
        # Chemins possibles d'installation de Git
        $gitPaths = @(
            "${env:ProgramFiles}\Git\bin\git.exe",
            "${env:ProgramFiles(x86)}\Git\bin\git.exe",
            "${env:LOCALAPPDATA}\Programs\Git\bin\git.exe"
        )
        
        foreach ($path in $gitPaths) {
            if (Test-Path $path) {
                Write-Host "Git trouvé à: $path" -ForegroundColor Green
                
                # Ajouter le répertoire de Git au PATH pour cette session
                $gitDir = Split-Path -Parent $path
                $env:PATH = "$gitDir;$env:PATH"
                
                Write-Host "Git ajouté au PATH pour cette session" -ForegroundColor Green
                return $true
            }
        }
        
        Write-Host "Git est installé mais n'est pas accessible. Redémarrez PowerShell ou ajoutez manuellement Git au PATH." -ForegroundColor Red
        Write-Host "Vous pouvez également essayer de fermer et rouvrir PowerShell et réexécuter ce script." -ForegroundColor Yellow
        return $false
    }
}

# Fonction pour vérifier si GitHub CLI est installé
function Check-GithubCLI {
    try {
        $ghVersion = gh --version
        Write-Host "GitHub CLI trouvé: $ghVersion" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "GitHub CLI n'est pas installé. Installation en cours..." -ForegroundColor Yellow
        
        try {
            winget install --id GitHub.cli -e --source winget
            Write-Host "GitHub CLI installé avec succès!" -ForegroundColor Green
            
            # Ajouter GitHub CLI au PATH pour cette session
            $ghPaths = @(
                "${env:ProgramFiles}\GitHub CLI\",
                "${env:LOCALAPPDATA}\Programs\GitHub CLI\"
            )
            
            foreach ($path in $ghPaths) {
                if (Test-Path $path) {
                    $env:PATH = "$path;$env:PATH"
                    break
                }
            }
            
            return $true
        }
        catch {
            Write-Host "Échec de l'installation de GitHub CLI. Veuillez l'installer manuellement: https://cli.github.com/" -ForegroundColor Red
            return $false
        }
    }
}

# Fonction pour initialiser le dépôt git et faire le premier commit
function Initialize-Git {
    Write-Host "Initialisation du dépôt Git..." -ForegroundColor Cyan
    
    # Vérifier si Git est déjà initialisé
    if (Test-Path (Join-Path $ProjectRoot ".git")) {
        Write-Host "Le dépôt Git est déjà initialisé." -ForegroundColor Yellow
        
        # Vérifier s'il y a déjà des commits
        $hasCommits = git log --oneline 2>&1
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrEmpty($hasCommits)) {
            Write-Host "Aucun commit trouvé. Création du premier commit..." -ForegroundColor Yellow
            
            # Nettoyer tout
            git reset
            
            # Ajouter les fichiers
            git add .
            
            # Premier commit
            git commit -m "Initial commit: YakTaa - Jeu de rôle cyberpunk"
            
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Échec du commit initial. Vérifiez les erreurs Git." -ForegroundColor Red
                exit 1
            }
            
            Write-Host "Premier commit créé avec succès!" -ForegroundColor Green
        }
        else {
            Write-Host "Le dépôt Git contient déjà des commits." -ForegroundColor Green
        }
        
        return
    }
    
    # Initialiser Git
    Push-Location $ProjectRoot
    git init
    git config --local core.autocrlf true
    
    # Ajouter les fichiers
    git add .
    
    # Premier commit
    git commit -m "Initial commit: YakTaa - Jeu de rôle cyberpunk"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Échec du commit initial. Vérifiez les erreurs Git." -ForegroundColor Red
        exit 1
    }
    
    Pop-Location
    
    Write-Host "Dépôt Git initialisé avec succès!" -ForegroundColor Green
}

# Fonction pour créer un dépôt GitHub
function Create-GithubRepo {
    Write-Host "Création du dépôt GitHub..." -ForegroundColor Cyan
    
    # Authentification GitHub CLI si nécessaire
    Push-Location $ProjectRoot
    
    $authStatus = gh auth status 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Authentification GitHub requise. Suivez les instructions..." -ForegroundColor Yellow
        gh auth login
    }
    
    # Demander le nom du dépôt
    $defaultRepoName = $RepoName
    $repoName = Read-Host "Entrez le nom du dépôt GitHub (Laissez vide pour utiliser '$defaultRepoName')"
    if ([string]::IsNullOrEmpty($repoName)) {
        $repoName = $defaultRepoName
    }
    
    # Créer le dépôt sur GitHub
    Write-Host "Création du dépôt GitHub '$repoName'..." -ForegroundColor Cyan
    
    # Vérifier si un remote origin existe déjà
    $remoteExists = git remote -v 2>&1
    if ($remoteExists -match "origin") {
        Write-Host "Un remote 'origin' existe déjà. Suppression..." -ForegroundColor Yellow
        git remote remove origin
    }
    
    # Vérifier si le dépôt existe déjà sur GitHub
    $repoExists = gh repo view "syrus2008/$repoName" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Le dépôt GitHub 'syrus2008/$repoName' existe déjà." -ForegroundColor Yellow
        
        # Obtenir le nom d'utilisateur GitHub
        $username = gh api user | ConvertFrom-Json | Select-Object -ExpandProperty login
        
        # Ajouter le remote origin
        git remote add origin "https://github.com/$username/$repoName.git"
        
        # Déterminer le nom de la branche par défaut
        $defaultBranchName = "main"
        $branchExists = git branch --list $defaultBranchName
        if ([string]::IsNullOrEmpty($branchExists)) {
            # La branche main n'existe pas, utiliser la branche actuelle
            $currentBranch = git branch --show-current
            
            if ([string]::IsNullOrEmpty($currentBranch)) {
                # Pas de branche actuelle, on est probablement dans un état de HEAD détaché
                # Créer une branche main
                git checkout -b main
                $defaultBranchName = "main"
            } else {
                $defaultBranchName = $currentBranch
            }
        }
        
        # Pousser les modifications
        git push -u origin $defaultBranchName
        
        Write-Host "Code poussé vers GitHub avec succès!" -ForegroundColor Green
        return
    }
    
    # Créer le dépôt et pousser le code
    Write-Host "Création d'un nouveau dépôt GitHub '$repoName'..." -ForegroundColor Yellow
    
    # Créer le dépôt sans option --source pour éviter les erreurs
    gh repo create $repoName --private
    
    if ($LASTEXITCODE -eq 0) {
        # Obtenir le nom d'utilisateur GitHub
        $username = gh api user | ConvertFrom-Json | Select-Object -ExpandProperty login
        
        Write-Host "Dépôt GitHub créé. Ajout du remote..." -ForegroundColor Yellow
        git remote add origin "https://github.com/$username/$repoName.git"
        
        # Déterminer le nom de la branche par défaut
        $defaultBranchName = "main"
        $branchExists = git branch --list $defaultBranchName
        if ([string]::IsNullOrEmpty($branchExists)) {
            # La branche main n'existe pas, utiliser la branche actuelle
            $currentBranch = git branch --show-current
            
            if ([string]::IsNullOrEmpty($currentBranch)) {
                # Pas de branche actuelle, on est probablement dans un état de HEAD détaché
                # Créer une branche main
                git checkout -b main
                $defaultBranchName = "main"
            } else {
                $defaultBranchName = $currentBranch
            }
        }
        
        # Pousser les modifications
        git push -u origin $defaultBranchName
        
        Write-Host "Code poussé vers GitHub avec succès!" -ForegroundColor Green
    }
    else {
        Write-Host "Échec de création du dépôt GitHub." -ForegroundColor Red
        exit 1
    }
    
    Pop-Location
}

# Fonction pour créer une release GitHub avec l'installateur
function Create-GithubRelease {
    Write-Host "Création d'une release GitHub avec l'installateur..." -ForegroundColor Cyan
    
    # Vérifier si l'installateur existe
    $installerFiles = Get-ChildItem -Path $OutputDir -Filter "*.exe"
    if ($installerFiles.Count -eq 0) {
        Write-Host "Aucun installateur trouvé dans le dossier $OutputDir. Exécutez d'abord build_final.ps1" -ForegroundColor Red
        
        # Demander à l'utilisateur s'il veut exécuter le script de build
        $runBuild = Read-Host "Voulez-vous exécuter le script de build maintenant? (o/n)"
        if ($runBuild -eq "o") {
            Write-Host "Exécution du script de build..." -ForegroundColor Yellow
            & "$ProjectRoot\build_final.ps1"
            
            # Vérifier à nouveau si l'installateur existe
            $installerFiles = Get-ChildItem -Path $OutputDir -Filter "*.exe"
            if ($installerFiles.Count -eq 0) {
                Write-Host "L'installateur n'a pas été créé. Vérifiez le script de build." -ForegroundColor Red
                exit 1
            }
        }
        else {
            Write-Host "Création de la release annulée." -ForegroundColor Yellow
            return
        }
    }
    
    $installerPath = $installerFiles[0].FullName
    $installerName = $installerFiles[0].Name
    
    # Obtenir la version actuelle
    $version = "1.0.0"  # Version par défaut
    $versionInput = Read-Host "Entrez la version pour cette release (par défaut: $version)"
    if ($versionInput) {
        $version = $versionInput
    }
    
    # Créer la release
    Push-Location $ProjectRoot
    
    # Vérifier si le repo est vide et créer un fichier README si nécessaire
    $filesCount = gh api repos/syrus2008/YakTaa/contents | ConvertFrom-Json | Measure-Object | Select-Object -ExpandProperty Count
    
    if ($filesCount -eq 0) {
        Write-Host "Le dépôt est vide sur GitHub. Création d'un fichier README.md..." -ForegroundColor Yellow
        
        # S'assurer que le README.md existe localement
        if (-not (Test-Path (Join-Path $ProjectRoot "README.md"))) {
            @"
# YakTaa

Un jeu de rôle et de simulation immersif dans un univers cyberpunk où vous accomplissez des missions, explorez différentes villes et pays, et interagissez avec divers systèmes informatiques via un terminal.

## Fonctionnalités

- Interface utilisateur moderne avec PyQt6
- Système de terminal et hacking avec émulation réaliste
- Exploration géographique avec carte interactive
- Système de missions et progression de personnage
- Économie dynamique et inventaire interactif

## Installation

Téléchargez l'installateur à partir des releases et suivez les instructions.

"@ | Out-File -FilePath (Join-Path $ProjectRoot "README.md") -Encoding utf8
        }
        
        # Pousser le README vers GitHub
        git add README.md
        git commit -m "Ajout du README.md"
        
        # Obtenir la branche actuelle
        $currentBranch = git branch --show-current
        if ([string]::IsNullOrEmpty($currentBranch)) {
            $currentBranch = "main"
            git checkout -b main
        }
        
        git push -u origin $currentBranch
    }
    
    Write-Host "Création de la release v$version avec l'installateur: $installerName" -ForegroundColor Cyan
    gh release create "v$version" "$installerPath" --title "YakTaa v$version" --notes "Release initiale de YakTaa v$version. Contient le jeu YakTaa et l'éditeur de monde."
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Release GitHub créée avec succès!" -ForegroundColor Green
        Write-Host "L'installateur est maintenant disponible dans les releases GitHub." -ForegroundColor Green
        
        # Afficher le lien vers la release
        $username = gh api user | ConvertFrom-Json | Select-Object -ExpandProperty login
        Write-Host "Vous pouvez accéder à votre release ici: https://github.com/$username/$RepoName/releases/tag/v$version" -ForegroundColor Cyan
    }
    else {
        Write-Host "Échec de création de la release GitHub." -ForegroundColor Red
        exit 1
    }
    
    Pop-Location
}

# Programme principal
Write-Host "=== Configuration GitHub pour YakTaa ===" -ForegroundColor Magenta

try {
    # Vérifier Git
    $gitAccessible = Check-Git
    if (-not $gitAccessible) {
        # Si Git n'est pas accessible, proposer de redémarrer PowerShell
        Write-Host "Le script a besoin d'être exécuté dans une nouvelle session PowerShell." -ForegroundColor Yellow
        Write-Host "Fermez cette fenêtre PowerShell, ouvrez-en une nouvelle et réexécutez le script." -ForegroundColor Yellow
        exit 1
    }
    
    # Configurer l'identité Git
    Configure-GitIdentity
    
    # Vérifier GitHub CLI
    $ghInstalled = Check-GithubCLI
    if (-not $ghInstalled) {
        exit 1
    }
    
    # Initialiser Git
    Initialize-Git
    
    # Créer le dépôt GitHub
    Create-GithubRepo
    
    # Créer une release
    Create-GithubRelease
    
    Write-Host "=== Configuration GitHub terminée avec succès! ===" -ForegroundColor Magenta
    Write-Host "Votre projet YakTaa est maintenant disponible sur GitHub avec une release contenant l'installateur." -ForegroundColor Green
} catch {
    Write-Host "Une erreur s'est produite: $_" -ForegroundColor Red
    exit 1
}
