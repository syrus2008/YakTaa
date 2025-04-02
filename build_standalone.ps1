# Script PowerShell pour la création d'un package YakTaa complètement autonome
# Ne nécessite aucune installation préalable de Python ou autres dépendances

# Configuration
$ErrorActionPreference = "Stop" # Arrêter en cas d'erreur
$ProjectRoot = $PSScriptRoot
$YakTaaRoot = Join-Path $ProjectRoot "yaktaa"
$YakTaaEditorRoot = Join-Path $ProjectRoot "yaktaa_world_editor"
$OutputDir = Join-Path $ProjectRoot "Output"
$DistDir = Join-Path $ProjectRoot "dist"
$SpecFile = Join-Path $ProjectRoot "yaktaa_standalone.spec"
$IssFile = Join-Path $ProjectRoot "yaktaa_standalone.iss"

# Vérification des prérequis
Write-Host "Vérification des prérequis pour le build autonome..." -ForegroundColor Cyan

# Vérifier PyInstaller
try {
    $pyinstallerVersion = python -c "import PyInstaller; print(PyInstaller.__version__)"
    Write-Host "PyInstaller version $pyinstallerVersion détecté." -ForegroundColor Green
} catch {
    Write-Host "PyInstaller n'est pas installé. Installation en cours..." -ForegroundColor Yellow
    python -m pip install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Échec de l'installation de PyInstaller." -ForegroundColor Red
        exit 1
    }
}

# Vérifier Inno Setup
$innoSetupPath = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $innoSetupPath)) {
    Write-Host "Inno Setup 6 n'est pas installé. Veuillez l'installer depuis: https://jrsoftware.org/isdl.php" -ForegroundColor Red
    exit 1
}

# Création des dossiers nécessaires
function Ensure-Directory {
    param(
        [string]$Path
    )
    
    if (-not (Test-Path $Path)) {
        Write-Host "Création du dossier $Path" -ForegroundColor Yellow
        New-Item -Path $Path -ItemType Directory -Force | Out-Null
    }
}

# Nettoyage des anciens fichiers
function Clean-BuildFiles {
    Write-Host "Nettoyage des anciens fichiers de build..." -ForegroundColor Yellow
    
    # Supprimer les anciens dossiers de build
    if (Test-Path (Join-Path $ProjectRoot "build")) {
        Remove-Item -Path (Join-Path $ProjectRoot "build") -Recurse -Force
    }
    
    if (Test-Path $DistDir) {
        Remove-Item -Path $DistDir -Recurse -Force
    }
    
    # Supprimer les anciens fichiers spec et iss autonomes s'ils existent
    if (Test-Path $SpecFile) {
        Remove-Item -Path $SpecFile -Force
    }
    
    if (Test-Path $IssFile) {
        Remove-Item -Path $IssFile -Force
    }
}

# Création du fichier spec amélioré pour YakTaa
function Create-StandaloneSpec {
    Write-Host "Création du fichier spec optimisé pour le build autonome..." -ForegroundColor Cyan
    
    # Obtenir le chemin des DLLs Qt6
    $qtBinPath = python -c "from PyQt6.QtCore import QLibraryInfo; print(QLibraryInfo.path(QLibraryInfo.LibraryPath.BinariesPath))"
    
    if ([string]::IsNullOrEmpty($qtBinPath)) {
        Write-Host "Impossible de trouver le chemin des DLLs Qt6." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Chemin des DLLs Qt6 détecté: $qtBinPath" -ForegroundColor Green
    
    # Contenu du fichier spec pour YakTaa
    $specContent = @"
# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

# Chemins importants
qt_bin_path = r'$qtBinPath'
project_root = r'$ProjectRoot'
yaktaa_root = r'$YakTaaRoot'
yaktaa_editor_root = r'$YakTaaEditorRoot'

# Collecte des dépendances
datas = []
binaries = []
hiddenimports = []

# Collecter toutes les données et imports pour PyQt6
qt_datas, qt_binaries, qt_hiddenimports = collect_all('PyQt6')
datas.extend(qt_datas)
binaries.extend(qt_binaries)
hiddenimports.extend(qt_hiddenimports)

# Collecter les autres dépendances importantes
for pkg in ['pygame', 'sqlalchemy', 'networkx', 'matplotlib', 'pygments']:
    try:
        pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
        datas.extend(pkg_datas)
        binaries.extend(pkg_binaries)
        hiddenimports.extend(pkg_hiddenimports)
    except:
        pass  # Ignorer si le package n'est pas installé

# Ajouter les DLLs Qt manuellement pour s'assurer qu'elles sont incluses
qt_dlls = [
    'Qt6Core.dll', 'Qt6Gui.dll', 'Qt6Widgets.dll', 'Qt6Svg.dll', 
    'Qt6Network.dll', 'Qt6DBus.dll', 'Qt6PrintSupport.dll'
]

for dll in qt_dlls:
    dll_path = os.path.join(qt_bin_path, dll)
    if os.path.exists(dll_path):
        binaries.append((dll_path, '.'))

# Ajouter les plugins Qt
qt_plugin_dirs = ['platforms', 'imageformats', 'styles', 'iconengines']
for plugin_dir in qt_plugin_dirs:
    plugin_path = os.path.join(qt_bin_path, '..', 'plugins', plugin_dir)
    if os.path.exists(plugin_path):
        for file in os.listdir(plugin_path):
            if file.endswith('.dll'):
                binaries.append((os.path.join(plugin_path, file), os.path.join(plugin_dir)))

# Ajouter la base de données
dbworld_path = os.path.join(yaktaa_root, 'dbworld', 'worlds.db')
if os.path.exists(dbworld_path):
    datas.append((dbworld_path, os.path.join('yaktaa', 'dbworld')))

# Configuration de YakTaa
a = Analysis(
    [os.path.join(yaktaa_root, 'main.py')],
    pathex=[project_root, yaktaa_root],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='YakTaa',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(yaktaa_root, 'resources', 'icons', 'app_icon.ico') if os.path.exists(os.path.join(yaktaa_root, 'resources', 'icons', 'app_icon.ico')) else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='YakTaa',
)

# Configuration de YakTaa World Editor
b = Analysis(
    [os.path.join(yaktaa_editor_root, 'main.py')],
    pathex=[project_root, yaktaa_editor_root],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz_editor = PYZ(b.pure, b.zipped_data, cipher=None)

exe_editor = EXE(
    pyz_editor,
    b.scripts,
    [],
    exclude_binaries=True,
    name='YakTaaWorldEditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(yaktaa_editor_root, 'resources', 'icons', 'editor_icon.ico') if os.path.exists(os.path.join(yaktaa_editor_root, 'resources', 'icons', 'editor_icon.ico')) else None,
)

coll_editor = COLLECT(
    exe_editor,
    b.binaries,
    b.zipfiles,
    b.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='YakTaaWorldEditor',
)
"@
    
    # Écrire le contenu dans le fichier spec
    $specContent | Out-File -FilePath $SpecFile -Encoding utf8
    
    Write-Host "Fichier spec autonome créé avec succès: $SpecFile" -ForegroundColor Green
}

# Fonction pour créer le fichier Inno Setup amélioré
function Create-StandaloneISS {
    Write-Host "Création du fichier Inno Setup optimisé pour le build autonome..." -ForegroundColor Cyan
    
    # Vérifier si l'icône existe
    $appIconPath = Join-Path $ProjectRoot "yaktaa\resources\icons\app_icon.ico"
    $editorIconPath = Join-Path $ProjectRoot "yaktaa_world_editor\resources\icons\editor_icon.ico"
    
    # Utiliser des icônes par défaut si elles n'existent pas
    $appIconSetting = ""
    $editorIconSetting = ""
    
    if (Test-Path $appIconPath) {
        Write-Host "Icône de l'application trouvée: $appIconPath" -ForegroundColor Green
        $appIconSetting = "SetupIconFile=$appIconPath"
    } else {
        Write-Host "Icône de l'application non trouvée. L'installateur utilisera l'icône par défaut." -ForegroundColor Yellow
    }
    
    # Contenu du fichier ISS pour l'installateur
    $issContent = @"
; Script d'installation Inno Setup pour YakTaa
; Configuration optimisée pour un installateur autonome

#define MyAppName "YakTaa"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "YakTaa Dev Team"
#define MyAppURL "https://github.com/syrus2008/YakTaa"
#define MyAppExeName "YakTaa.exe"
#define MyAppEditorExeName "YakTaaWorldEditor.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
AppId={{F1CA8245-BA39-4A73-9BF1-0D8E62A27B1C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=Output
OutputBaseFilename=YakTaa_Installer
$appIconSetting
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

; Installation des redistributables VC++
[Files]
Source: "dist\YakTaa\*"; DestDir: "{app}\YakTaa"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\YakTaaWorldEditor\*"; DestDir: "{app}\YakTaaWorldEditor"; Flags: ignoreversion recursesubdirs createallsubdirs
; Inclure les redistributables Visual C++
Source: "vcredist\*"; DestDir: "{tmp}"; Flags: deleteafterinstall; Check: VCRedistNeeded

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\YakTaa\{#MyAppExeName}"
Name: "{group}\{#MyAppName} World Editor"; Filename: "{app}\YakTaaWorldEditor\{#MyAppEditorExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\YakTaa\{#MyAppExeName}"; Tasks: desktopicon
Name: "{autodesktop}\{#MyAppName} World Editor"; Filename: "{app}\YakTaaWorldEditor\{#MyAppEditorExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Run]
; Installation des redistributables VC++ si nécessaire
Filename: "{tmp}\VC_redist.x64.exe"; Parameters: "/install /quiet /norestart"; StatusMsg: "Installation de Visual C++ Redistributable..."; Check: VCRedistNeeded
; Lancement de l'application après l'installation
Filename: "{app}\YakTaa\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Associer l'extension .yktw aux fichiers du monde YakTaa
Root: HKCR; Subkey: ".yktw"; ValueType: string; ValueName: ""; ValueData: "YakTaaWorldFile"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "YakTaaWorldFile"; ValueType: string; ValueName: ""; ValueData: "Fichier Monde YakTaa"; Flags: uninsdeletekey
Root: HKCR; Subkey: "YakTaaWorldFile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\YakTaaWorldEditor\{#MyAppEditorExeName},0"
Root: HKCR; Subkey: "YakTaaWorldFile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\YakTaaWorldEditor\{#MyAppEditorExeName}"" ""%1"""

[Code]
// Fonction pour vérifier si Visual C++ Redistributable est déjà installé
function VCRedistNeeded(): Boolean;
var
  Version: String;
  RegKey: String;
begin
  // Vérifier si Visual C++ Redistributable 2019 est installé
  RegKey := 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64';
  Result := not RegKeyExists(HKLM, RegKey);
  
  // Vérifier également la version 2022
  if Result then
  begin
    RegKey := 'SOFTWARE\Microsoft\VisualStudio\15.0\VC\Runtimes\x64';
    Result := not RegKeyExists(HKLM, RegKey);
  end;
end;

// Fonction qui s'exécute avant l'installation pour vérifier les conditions requises
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
"@
    
    # Écrire le contenu dans le fichier ISS
    $issContent | Out-File -FilePath $IssFile -Encoding utf8
    
    Write-Host "Fichier Inno Setup autonome créé avec succès: $IssFile" -ForegroundColor Green
}

# Téléchargement des redistributables VC++
function Download-VCRedist {
    Write-Host "Téléchargement des redistributables Visual C++..." -ForegroundColor Cyan
    
    $vcRedistDir = Join-Path $ProjectRoot "vcredist"
    Ensure-Directory -Path $vcRedistDir
    
    $vcRedistUrl = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
    $vcRedistFile = Join-Path $vcRedistDir "VC_redist.x64.exe"
    
    if (-not (Test-Path $vcRedistFile)) {
        Write-Host "Téléchargement de VC_redist.x64.exe depuis $vcRedistUrl..." -ForegroundColor Yellow
        
        try {
            Invoke-WebRequest -Uri $vcRedistUrl -OutFile $vcRedistFile
            Write-Host "Redistributable Visual C++ téléchargé avec succès." -ForegroundColor Green
        } catch {
            Write-Host "Échec du téléchargement du redistributable Visual C++. Erreur: $_" -ForegroundColor Red
            Write-Host "Veuillez télécharger manuellement VC_redist.x64.exe depuis https://aka.ms/vs/17/release/vc_redist.x64.exe" -ForegroundColor Yellow
            Write-Host "et placez-le dans le dossier $vcRedistDir" -ForegroundColor Yellow
            
            # Attendre que l'utilisateur télécharge manuellement le fichier
            $response = Read-Host "Appuyez sur Entrée une fois que vous avez téléchargé le fichier, ou tapez 'skip' pour continuer sans le redistributable"
            
            if ($response -eq "skip") {
                Write-Host "Construction sans redistributable Visual C++. L'installateur pourrait ne pas fonctionner sur certains systèmes." -ForegroundColor Yellow
            } else {
                if (-not (Test-Path $vcRedistFile)) {
                    Write-Host "Le fichier VC_redist.x64.exe n'a pas été trouvé dans $vcRedistDir. Construction sans redistributable." -ForegroundColor Red
                } else {
                    Write-Host "Redistributable Visual C++ trouvé." -ForegroundColor Green
                }
            }
        }
    } else {
        Write-Host "Redistributable Visual C++ déjà téléchargé." -ForegroundColor Green
    }
}

# Construction des exécutables avec PyInstaller
function Build-StandaloneExecutables {
    Write-Host "Construction des exécutables autonomes avec PyInstaller..." -ForegroundColor Cyan
    
    # Utiliser le fichier spec optimisé
    python -m PyInstaller --clean $SpecFile
    
    # Vérifier si les exécutables ont été créés
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

# Création de l'installateur avec Inno Setup
function Build-StandaloneInstaller {
    Write-Host "Création de l'installateur autonome avec Inno Setup..." -ForegroundColor Cyan
    
    Ensure-Directory -Path $OutputDir
    
    # Utiliser le fichier ISS optimisé
    & $innoSetupPath $IssFile "/O$OutputDir"
    
    # Vérifier si l'installateur a été créé
    $setupFiles = Get-ChildItem -Path $OutputDir -Filter "YakTaa_Installer.exe"
    if ($setupFiles.Count -gt 0) {
        Write-Host "Installateur autonome créé avec succès: $($setupFiles[0].FullName)" -ForegroundColor Green
    } else {
        Write-Host "Échec de création de l'installateur autonome" -ForegroundColor Red
        exit 1
    }
}

# Programme principal
Write-Host "=== Création du package YakTaa Standalone ===" -ForegroundColor Magenta

try {
    # Nettoyer les anciens fichiers
    Clean-BuildFiles
    
    # Créer les fichiers de configuration
    Create-StandaloneSpec
    Create-StandaloneISS
    
    # Télécharger les redistributables VC++
    Download-VCRedist
    
    # Construire les exécutables
    Build-StandaloneExecutables
    
    # Créer l'installateur
    Build-StandaloneInstaller
    
    Write-Host "=== Création du package YakTaa Standalone terminée avec succès! ===" -ForegroundColor Magenta
    Write-Host "L'installateur autonome se trouve dans: $OutputDir\YakTaa_Installer.exe" -ForegroundColor Green
    Write-Host "Cet installateur fonctionne sur toute machine Windows sans nécessiter Python préinstallé." -ForegroundColor Green
} catch {
    Write-Host "Une erreur s'est produite: $_" -ForegroundColor Red
    exit 1
}
