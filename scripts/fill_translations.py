#!/usr/bin/env python
"""
Script to fill basic French and Arabic translations.
This script adds common translations to the .po files.
"""
import re
from pathlib import Path

# Common translations mapping (English -> French)
FRENCH_TRANSLATIONS = {
    "Invalid username or password": "Nom d'utilisateur ou mot de passe invalide",
    "Login successful": "Connexion réussie",
    "Login failed: {}": "Échec de la connexion : {}",
    "Customer not found": "Client non trouvé",
    "Customer created successfully": "Client créé avec succès",
    "Failed to create customer: {}": "Échec de la création du client : {}",
    "Customer updated successfully": "Client mis à jour avec succès",
    "Delete not yet implemented": "Suppression pas encore implémentée",
    "Customer archived successfully": "Client archivé avec succès",
    "Customer activated successfully": "Client activé avec succès",
    "Settings": "Paramètres",
    "Default Language": "Langue par défaut",
    "Document Prefixes": "Préfixes de documents",
    "Stock Management": "Gestion des stocks",
    "Application Settings": "Paramètres de l'application",
    "Company Information": "Informations de l'entreprise",
    "Manage application and company settings": "Gérer les paramètres de l'application et de l'entreprise",
    "Loading...": "Chargement...",
    "Error": "Erreur",
    "Success": "Succès",
    "Warning": "Attention",
    "Info": "Information",
    "Cancel": "Annuler",
    "Save": "Enregistrer",
    "Delete": "Supprimer",
    "Edit": "Modifier",
    "View": "Voir",
    "Create": "Créer",
    "Update": "Mettre à jour",
    "Submit": "Soumettre",
    "Back": "Retour",
    "Next": "Suivant",
    "Previous": "Précédent",
    "Search": "Rechercher",
    "Filter": "Filtrer",
    "Reset": "Réinitialiser",
    "Close": "Fermer",
    "Confirm": "Confirmer",
    "Yes": "Oui",
    "No": "Non",
    "OK": "OK",
}

def fill_translations(po_file_path, translations_dict, lang_code):
    """Fill empty msgstr entries with translations."""
    po_file = Path(po_file_path)
    if not po_file.exists():
        print(f"File not found: {po_file_path}")
        return
    
    content = po_file.read_text(encoding='utf-8')
    lines = content.split('\n')
    new_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Check if this is a msgid line
        if line.startswith('msgid '):
            # Extract the msgid value
            msgid_match = re.match(r'msgid "(.+)"', line)
            if msgid_match:
                msgid = msgid_match.group(1)
                # Look for the next msgstr line
                if i + 1 < len(lines) and lines[i + 1].startswith('msgstr ""'):
                    # Check if we have a translation for this msgid
                    if msgid in translations_dict:
                        translation = translations_dict[msgid]
                        new_lines.append(f'msgstr "{translation}"')
                        i += 1  # Skip the empty msgstr line
                        continue
                # If next line is already a filled msgstr, skip it
                elif i + 1 < len(lines) and lines[i + 1].startswith('msgstr "'):
                    i += 1  # Skip the existing msgstr line
                    continue
        
        i += 1
    
    # Write back
    po_file.write_text('\n'.join(new_lines), encoding='utf-8')
    print(f"✓ Updated {po_file_path}")

def main():
    project_root = Path(__file__).parent.parent
    translations_dir = project_root / "app" / "translations"
    
    # Fill French translations
    fr_po = translations_dir / "fr" / "LC_MESSAGES" / "messages.po"
    if fr_po.exists():
        print("Filling French translations...")
        fill_translations(fr_po, FRENCH_TRANSLATIONS, 'fr')
    
    # For Arabic, we'll leave empty for now (can be filled later)
    print("\nNote: Arabic translations are left empty. You can fill them manually or use a translation service.")
    
    print("\n✓ Done! Now compile translations:")
    print("  pybabel compile -d app/translations")

if __name__ == '__main__':
    main()

