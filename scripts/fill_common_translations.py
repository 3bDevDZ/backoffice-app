#!/usr/bin/env python
"""
Script to fill common French translations for CommerceFlow.
This script adds translations for the most commonly used strings in the UI.
"""
import re
from pathlib import Path

# Common translations mapping (English -> French)
COMMON_TRANSLATIONS = {
    # Modules
    "Dashboard": "Tableau de bord",
    "Sales": "Ventes",
    "Purchases": "Achats",
    "Inventory": "Inventaire",
    "Catalog": "Catalogue",
    "Settings": "Paramètres",
    "Modules": "Modules",
    
    # Module descriptions
    "Overview of your business KPIs, sales, and key metrics": "Aperçu des KPI, ventes et métriques clés de votre entreprise",
    "Manage customers, quotes, orders, invoices, and payments": "Gérer les clients, devis, commandes, factures et paiements",
    "Manage suppliers, purchase requests, orders, and receipts": "Gérer les fournisseurs, demandes d'achat, commandes et réceptions",
    "Manage stock levels, locations, movements, and alerts": "Gérer les niveaux de stock, emplacements, mouvements et alertes",
    "Manage products, variants, price lists, and pricing": "Gérer les produits, variantes, listes de prix et tarifs",
    "Configure company information and application settings": "Configurer les informations de l'entreprise et les paramètres de l'application",
    
    # Quick Actions
    "Quick Actions": "Actions rapides",
    "New Order": "Nouvelle commande",
    "New Purchase Order": "Nouvel ordre d'achat",
    "New Product": "Nouveau produit",
    "New Customer": "Nouveau client",
    
    # Common UI elements
    "Select a module to get started": "Sélectionnez un module pour commencer",
    "Back to Modules": "Retour aux modules",
    "Menu": "Menu",
    "Module Menu": "Menu du module",
    
    # Settings
    "Application Settings": "Paramètres de l'application",
    "Company Information": "Informations de l'entreprise",
    "Manage application and company settings": "Gérer les paramètres de l'application et de l'entreprise",
    "Default Language": "Langue par défaut",
    "Document Prefixes": "Préfixes de documents",
    "Stock Management": "Gestion des stocks",
    
    # Common actions
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

def fill_translations(po_file_path, translations_dict):
    """Fill empty msgstr entries with translations."""
    po_file = Path(po_file_path)
    if not po_file.exists():
        print(f"File not found: {po_file_path}")
        return False
    
    content = po_file.read_text(encoding='utf-8')
    lines = content.split('\n')
    new_lines = []
    i = 0
    updated_count = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a msgid line
        if line.startswith('msgid '):
            # Extract the msgid value (handle multi-line msgid)
            msgid_parts = [line]
            j = i + 1
            while j < len(lines) and (lines[j].startswith('"') or lines[j].strip() == ''):
                if lines[j].startswith('"'):
                    msgid_parts.append(lines[j])
                j += 1
            
            # Reconstruct full msgid
            full_msgid = '\n'.join(msgid_parts)
            msgid_match = re.search(r'msgid\s+"(.+?)"', full_msgid, re.DOTALL)
            if msgid_match:
                msgid = msgid_match.group(1).replace('\\n', '\n').replace('\\"', '"')
                # Remove escaped quotes and newlines for matching
                msgid_clean = msgid.replace('\\n', ' ').replace('\\"', '"').strip()
                
                # Add all msgid lines
                for part in msgid_parts:
                    new_lines.append(part)
                    i += 1
                
                # Look for the next msgstr line
                if i < len(lines) and lines[i].startswith('msgstr ""'):
                    # Check if we have a translation for this msgid
                    if msgid_clean in translations_dict:
                        translation = translations_dict[msgid_clean]
                        new_lines.append(f'msgstr "{translation}"')
                        updated_count += 1
                        i += 1  # Skip the empty msgstr line
                        continue
                # If msgstr is already filled, keep it
                elif i < len(lines) and lines[i].startswith('msgstr "'):
                    new_lines.append(lines[i])
                    i += 1
                    continue
            else:
                new_lines.append(line)
                i += 1
        else:
            new_lines.append(line)
            i += 1
    
    # Write back
    po_file.write_text('\n'.join(new_lines), encoding='utf-8')
    print(f"✓ Updated {po_file_path} ({updated_count} translations added)")
    return True

def main():
    project_root = Path(__file__).parent.parent
    translations_dir = project_root / "app" / "translations"
    
    # Fill French translations
    fr_po = translations_dir / "fr" / "LC_MESSAGES" / "messages.po"
    if fr_po.exists():
        print("Filling French translations...")
        fill_translations(fr_po, COMMON_TRANSLATIONS)
    
    print("\n✓ Done! Now compile translations:")
    print("  pybabel compile -d app/translations")

if __name__ == '__main__':
    main()

