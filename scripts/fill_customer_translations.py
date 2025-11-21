#!/usr/bin/env python
"""
Script to fill French translations for customer management and other common UI strings.
"""
import re
from pathlib import Path

# French translations mapping
FRENCH_TRANSLATIONS = {
    # Customer Management
    "Customer Management": "Gestion des clients",
    "Manage your B2B and B2C customers": "Gérez vos clients B2B et B2C",
    "Total Customers": "Total clients",
    "B2B Customers": "Clients B2B",
    "B2C Customers": "Clients B2C",
    "Active Customers": "Clients actifs",
    "New Customer": "Nouveau client",
    "Export": "Exporter",
    "Import": "Importer",
    "Search by name, code, email...": "Rechercher par nom, code, email...",
    "All Types": "Tous les types",
    "All Statuses": "Tous les statuts",
    "CUSTOMER": "CLIENT",
    "CODE": "CODE",
    "TYPE": "TYPE",
    "EMAIL": "EMAIL",
    "PHONE": "TÉLÉPHONE",
    "STATUS": "STATUT",
    "ACTIONS": "ACTIONS",
    "B2B": "B2B",
    "B2C": "B2C",
    "Active": "Actif",
    "Inactive": "Inactif",
    "Archived": "Archivé",
    "Blocked": "Bloqué",
    "Filter": "Filtrer",
    "Reset": "Réinitialiser",
    "View": "Voir",
    "Edit": "Modifier",
    "Delete": "Supprimer",
    "Customers": "Clients",
    "New": "Nouveau",
    "Save": "Enregistrer",
    "Cancel": "Annuler",
    "Back": "Retour",
    "Search": "Rechercher",
    "Close": "Fermer",
    "Confirm": "Confirmer",
    "Yes": "Oui",
    "No": "Non",
    "OK": "OK",
    "Loading...": "Chargement...",
    "Error": "Erreur",
    "Success": "Succès",
    "Warning": "Avertissement",
    "Info": "Information",
    "Are you sure?": "Êtes-vous sûr ?",
    "This action cannot be undone.": "Cette action ne peut pas être annulée.",
    "Please wait...": "Veuillez patienter...",
    "Operation successful": "Opération réussie",
    "Operation failed": "Opération échouée",
    "An error occurred": "Une erreur s'est produite",
    "Invalid input": "Saisie invalide",
    "Required field": "Champ requis",
    "Draft": "Brouillon",
    "Confirmed": "Confirmé",
    "Cancelled": "Annulé",
    "Completed": "Terminé",
    "Pending": "En attente",
    "Add": "Ajouter",
    "Remove": "Retirer",
    "Select": "Sélectionner",
    "Choose": "Choisir",
    "Upload": "Télécharger",
    "Download": "Télécharger",
    "Print": "Imprimer",
    "Date": "Date",
    "From": "De",
    "To": "À",
    "Today": "Aujourd'hui",
    "Yesterday": "Hier",
    "This week": "Cette semaine",
    "This month": "Ce mois",
    "This year": "Cette année",
    "Page": "Page",
    "of": "de",
    "Showing": "Affichage",
    "to": "à",
    "results": "résultats",
    "No results found": "Aucun résultat trouvé",
    "Please fill in all required fields": "Veuillez remplir tous les champs requis",
    "Invalid email address": "Adresse e-mail invalide",
    "Invalid phone number": "Numéro de téléphone invalide",
    "Value must be greater than 0": "La valeur doit être supérieure à 0",
    "Value must be a number": "La valeur doit être un nombre",
}

def fill_translations(po_file_path, translations_dict):
    """Fill translations in a .po file."""
    po_file = Path(po_file_path)
    if not po_file.exists():
        print(f"File not found: {po_file_path}")
        return
    
    content = po_file.read_text(encoding='utf-8')
    lines = content.split('\n')
    new_lines = []
    i = 0
    filled_count = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a msgid line
        if line.startswith('msgid '):
            # Extract the msgid value (handle multi-line msgid)
            msgid_lines = [line]
            j = i + 1
            while j < len(lines) and lines[j].startswith('"'):
                msgid_lines.append(lines[j])
                j += 1
            
            # Find the corresponding msgstr
            msgstr_index = j
            if msgstr_index < len(lines) and lines[msgstr_index].startswith('msgstr '):
                # Extract full msgid (handle multi-line)
                msgid_full = '\n'.join(msgid_lines)
                msgid_match = re.search(r'msgid\s+"(.+?)"', msgid_full, re.DOTALL)
                if msgid_match:
                    msgid = msgid_match.group(1).replace('\\n', '\n').replace('\\"', '"')
                    
                    # Check if we have a translation
                    if msgid in translations_dict:
                        translation = translations_dict[msgid]
                        # Check if msgstr is empty
                        msgstr_line = lines[msgstr_index]
                        if msgstr_line == 'msgstr ""' or msgstr_line.startswith('msgstr ""'):
                            # Replace the msgstr line
                            new_lines.extend(msgid_lines)
                            new_lines.append(f'msgstr "{translation}"')
                            i = msgstr_index + 1
                            filled_count += 1
                            continue
        
        new_lines.append(line)
        i += 1
    
    po_file.write_text('\n'.join(new_lines), encoding='utf-8')
    print(f"✓ Updated {po_file_path} ({filled_count} translations filled)")

def main():
    print("============================================================")
    print("CommerceFlow - Fill Customer & Common Translations (French)")
    print("============================================================")
    
    fr_po = Path('app/translations/fr/LC_MESSAGES/messages.po')
    if fr_po.exists():
        print("\nFilling French translations...")
        fill_translations(fr_po, FRENCH_TRANSLATIONS)
    else:
        print(f"✗ File not found: {fr_po}")
    
    print("\n============================================================")
    print("✓ Translation filling completed!")
    print("\nNext step: Run 'pybabel compile -d app/translations' to compile")
    print("============================================================")

if __name__ == '__main__':
    main()


