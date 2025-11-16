# Installation de WeasyPrint sur Windows

## Prérequis
- Python 3.11 (64-bit) ✅ (déjà installé)
- GTK+ Runtime installé dans `C:\GTK` ✅ (déjà fait)

## Étapes d'installation

### 1. Ajouter GTK au PATH système (OBLIGATOIRE)

**Option A : Via l'interface graphique**
1. Ouvrir le **Panneau de configuration** → **Système**
2. Cliquer sur **Paramètres système avancés**
3. Cliquer sur **Variables d'environnement**
4. Dans **Variables système**, sélectionner `Path` et cliquer sur **Modifier**
5. Cliquer sur **Nouveau** et ajouter : `C:\GTK\bin`
6. Cliquer sur **OK** pour fermer toutes les fenêtres
7. **Redémarrer** le terminal/IDE pour que les changements prennent effet

**Option B : Via PowerShell (Administrateur)**
```powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\GTK\bin", [EnvironmentVariableTarget]::Machine)
```

**Vérification :**
```powershell
$env:Path -split ';' | Select-String -Pattern 'gtk'
```

### 2. Installer les bibliothèques Python pour GTK

Pour **Python 3.11 64-bit**, vous avez deux options :

#### Option A : Via pip (recommandé si disponible)
```bash
pip install pycairo
pip install PyGObject
```

#### Option B : Via les binaires précompilés (si pip échoue)

1. **PyCairo** :
   - Télécharger depuis : https://www.lfd.uci.edu/~gohlke/pythonlibs/#pycairo
   - Chercher `pycairo‑1.XX.X‑cp311‑cp311‑win_amd64.whl`
   - Installer : `pip install pycairo‑1.XX.X‑cp311‑cp311‑win_amd64.whl`

2. **PyGObject** :
   - Télécharger depuis : https://www.lfd.uci.edu/~gohlke/pythonlibs/#pygobject
   - Chercher `PyGObject‑3.XX.X‑cp311‑cp311‑win_amd64.whl`
   - Installer : `pip install PyGObject‑3.XX.X‑cp311‑cp311‑win_amd64.whl`

3. **lxml** (déjà installé ✅) :
   ```bash
   pip install lxml
   ```

### 3. Vérifier l'installation

**Test 1 : Vérifier que GTK est dans le PATH**
```powershell
# Dans un NOUVEAU terminal (après redémarrage)
$env:Path -split ';' | Select-String -Pattern 'gtk'
# Doit afficher : C:\GTK\bin
```

**Test 2 : Vérifier les DLL GTK**
```powershell
Test-Path "C:\GTK\bin\libgobject-2.0-0.dll"
# Doit retourner : True
```

**Test 3 : Tester WeasyPrint**
```python
python -c "from weasyprint import HTML; print('✅ WeasyPrint fonctionne!')"
```

### 4. Résolution de problèmes

#### Problème : "cannot load library libgobject-2.0-0.dll"

**Solution 1 : Vérifier que C:\GTK\bin est dans le PATH**
- Redémarrer le terminal après avoir modifié le PATH
- Vérifier avec : `echo %PATH%` (cmd) ou `$env:Path` (PowerShell)

**Solution 2 : Vérifier l'architecture**
- GTK doit être 64-bit si Python est 64-bit
- Vérifier : `python -c "import sys; print('64-bit' if sys.maxsize > 2**32 else '32-bit')"`

**Solution 3 : Conflit avec Tesseract-OCR**
- Si Tesseract est installé dans `C:\Program Files\Tesseract-OCR\`
- Vérifier que `C:\GTK\bin` est **AVANT** Tesseract dans le PATH
- Ou désinstaller Tesseract si non utilisé

**Solution 4 : Réinstaller GTK+**
- Télécharger le bundle complet depuis : https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
- Installer dans `C:\GTK` (pas dans Program Files)

### 5. Installation complète (commande par commande)

```bash
# 1. Vérifier Python
python --version
# Doit être 3.11

# 2. Ajouter GTK au PATH (voir étape 1 ci-dessus)
# Puis redémarrer le terminal

# 3. Installer les dépendances Python
pip install pycairo PyGObject lxml

# 4. Installer WeasyPrint (déjà fait, mais peut être réinstallé)
pip install --upgrade weasyprint

# 5. Tester
python -c "from weasyprint import HTML; print('✅ Succès!')"
```

## Notes importantes

- **Redémarrer le terminal/IDE** après avoir modifié le PATH est **OBLIGATOIRE**
- Les instructions ci-dessus sont pour **Python 3.11 64-bit**
- Pour Python 2.7, utiliser PyGTK au lieu de PyGObject
- Si vous utilisez un IDE (VS Code, PyCharm), redémarrer l'IDE après modification du PATH

## Vérification finale

Une fois tout installé, tester avec :

```python
from weasyprint import HTML
from io import BytesIO

html_content = "<html><body><h1>Test</h1></body></html>"
pdf = HTML(string=html_content).write_pdf()
print(f"✅ PDF généré avec succès! Taille: {len(pdf)} bytes")
```

