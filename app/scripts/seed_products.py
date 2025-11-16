"""Seed script for categories and products for a plumbing fixtures wholesaler."""
from decimal import Decimal

from app import create_app
from app.infrastructure.db import get_session
from app.domain.models.category import Category
from app.domain.models.product import Product


def seed_categories_and_products() -> None:
    """Seed categories and products for plumbing fixtures wholesaler."""
    app = create_app()
    
    with app.app_context():
        with get_session() as session:
            # Check if categories already exist
            existing_categories = session.query(Category).count()
            if existing_categories > 0:
                print(f"[INFO] {existing_categories} categories already exist. Skipping category seed.")
            else:
                print("[INFO] Creating categories...")
                
                # Main categories for plumbing fixtures wholesaler
                categories_data = [
                    {
                        "name": "Robinetterie",
                        "code": "ROB",
                        "description": "Robinetterie et accessoires de plomberie"
                    },
                    {
                        "name": "Robinetterie Évier",
                        "code": "ROB-EVIER",
                        "parent_name": "Robinetterie",
                        "description": "Robinetterie pour évier de cuisine"
                    },
                    {
                        "name": "Robinetterie Lavabo",
                        "code": "ROB-LAVABO",
                        "parent_name": "Robinetterie",
                        "description": "Robinetterie pour lavabo de salle de bain"
                    },
                    {
                        "name": "Robinetterie Douche",
                        "code": "ROB-DOUCHE",
                        "parent_name": "Robinetterie",
                        "description": "Robinetterie pour douche et baignoire"
                    },
                    {
                        "name": "Tubes et Raccords",
                        "code": "TUBE",
                        "description": "Tubes, tuyaux et raccords de plomberie"
                    },
                    {
                        "name": "Accessoires",
                        "code": "ACC",
                        "description": "Accessoires de plomberie divers"
                    },
                    {
                        "name": "Vanne et Vannes",
                        "code": "VANNE",
                        "description": "Vannes et robinets d'arrêt"
                    },
                ]
                
                categories_dict = {}
                
                # Create parent categories first
                for cat_data in categories_data:
                    if "parent_name" not in cat_data:
                        category = Category.create(
                            name=cat_data["name"],
                            code=cat_data["code"],
                            description=cat_data.get("description")
                        )
                        session.add(category)
                        session.flush()  # Get ID
                        categories_dict[cat_data["name"]] = category
                        print(f"  [OK] Created category: {cat_data['name']} ({cat_data['code']})")
                
                # Create child categories
                for cat_data in categories_data:
                    if "parent_name" in cat_data:
                        parent = categories_dict.get(cat_data["parent_name"])
                        if parent:
                            category = Category.create(
                                name=cat_data["name"],
                                code=cat_data["code"],
                                parent_id=parent.id,
                                description=cat_data.get("description")
                            )
                            session.add(category)
                            session.flush()
                            categories_dict[cat_data["name"]] = category
                            print(f"  [OK] Created category: {cat_data['name']} ({cat_data['code']}) - child of {cat_data['parent_name']}")
                
                session.commit()
                print(f"[OK] Created {len(categories_dict)} categories.")
            
            # Check if products already exist
            existing_products = session.query(Product).count()
            if existing_products > 0:
                print(f"[INFO] {existing_products} products already exist. Skipping product seed.")
            else:
                print("[INFO] Creating products...")
                
                # Get categories for product assignment
                rob_evier = session.query(Category).filter_by(code="ROB-EVIER").first()
                rob_lavabo = session.query(Category).filter_by(code="ROB-LAVABO").first()
                rob_douche = session.query(Category).filter_by(code="ROB-DOUCHE").first()
                tube = session.query(Category).filter_by(code="TUBE").first()
                acc = session.query(Category).filter_by(code="ACC").first()
                vanne = session.query(Category).filter_by(code="VANNE").first()
                
                # Products data for plumbing fixtures wholesaler
                products_data = [
                    # Robinetterie Évier
                    {
                        "code": "ROB-EV-001",
                        "name": "Robinet Évier Chromé Simple",
                        "description": "Robinet de cuisine chromé, simple levier, montage sur évier",
                        "price": Decimal("89.90"),
                        "cost": Decimal("45.00"),
                        "unit_of_measure": "pièce",
                        "barcode": "1234567890123",
                        "category_codes": ["ROB-EVIER"]
                    },
                    {
                        "code": "ROB-EV-002",
                        "name": "Robinet Évier Inox avec Douchette",
                        "description": "Robinet de cuisine inox avec douchette extractible",
                        "price": Decimal("149.90"),
                        "cost": Decimal("75.00"),
                        "unit_of_measure": "pièce",
                        "barcode": "1234567890124",
                        "category_codes": ["ROB-EVIER"]
                    },
                    {
                        "code": "ROB-EV-003",
                        "name": "Robinet Évier Professionnel",
                        "description": "Robinet professionnel haute résistance pour cuisine commerciale",
                        "price": Decimal("299.90"),
                        "cost": Decimal("150.00"),
                        "unit_of_measure": "pièce",
                        "barcode": "1234567890125",
                        "category_codes": ["ROB-EVIER"]
                    },
                    # Robinetterie Lavabo
                    {
                        "code": "ROB-LV-001",
                        "name": "Robinet Lavabo Chromé",
                        "description": "Robinet de lavabo chromé, design moderne",
                        "price": Decimal("79.90"),
                        "cost": Decimal("40.00"),
                        "unit_of_measure": "pièce",
                        "barcode": "1234567890126",
                        "category_codes": ["ROB-LAVABO"]
                    },
                    {
                        "code": "ROB-LV-002",
                        "name": "Robinet Lavabo avec Douchette",
                        "description": "Robinet de lavabo avec douchette intégrée",
                        "price": Decimal("129.90"),
                        "cost": Decimal("65.00"),
                        "unit_of_measure": "pièce",
                        "barcode": "1234567890127",
                        "category_codes": ["ROB-LAVABO"]
                    },
                    {
                        "code": "ROB-LV-003",
                        "name": "Robinet Lavabo Design",
                        "description": "Robinet de lavabo design, finition or rose",
                        "price": Decimal("199.90"),
                        "cost": Decimal("100.00"),
                        "unit_of_measure": "pièce",
                        "barcode": "1234567890128",
                        "category_codes": ["ROB-LAVABO"]
                    },
                    # Robinetterie Douche
                    {
                        "code": "ROB-DO-001",
                        "name": "Mitigeur Douche Standard",
                        "description": "Mitigeur de douche standard, chromé",
                        "price": Decimal("119.90"),
                        "cost": Decimal("60.00"),
                        "unit_of_measure": "pièce",
                        "barcode": "1234567890129",
                        "category_codes": ["ROB-DOUCHE"]
                    },
                    {
                        "code": "ROB-DO-002",
                        "name": "Mitigeur Douche Thermostatique",
                        "description": "Mitigeur thermostatique avec sécurité anti-brûlure",
                        "price": Decimal("249.90"),
                        "cost": Decimal("125.00"),
                        "unit_of_measure": "pièce",
                        "barcode": "1234567890130",
                        "category_codes": ["ROB-DOUCHE"]
                    },
                    {
                        "code": "ROB-DO-003",
                        "name": "Douchette Haute Pression",
                        "description": "Douchette haute pression avec plusieurs jets",
                        "price": Decimal("89.90"),
                        "cost": Decimal("45.00"),
                        "unit_of_measure": "pièce",
                        "barcode": "1234567890131",
                        "category_codes": ["ROB-DOUCHE"]
                    },
                    # Tubes et Raccords
                    {
                        "code": "TUBE-CU-001",
                        "name": "Tuyau Cuivre 15mm x 1m",
                        "description": "Tuyau de cuivre diamètre 15mm, longueur 1 mètre",
                        "price": Decimal("12.90"),
                        "cost": Decimal("6.50"),
                        "unit_of_measure": "mètre",
                        "barcode": "1234567890132",
                        "category_codes": ["TUBE"]
                    },
                    {
                        "code": "TUBE-CU-002",
                        "name": "Tuyau Cuivre 22mm x 1m",
                        "description": "Tuyau de cuivre diamètre 22mm, longueur 1 mètre",
                        "price": Decimal("18.90"),
                        "cost": Decimal("9.50"),
                        "unit_of_measure": "mètre",
                        "barcode": "1234567890133",
                        "category_codes": ["TUBE"]
                    },
                    {
                        "code": "RAC-001",
                        "name": "Raccord Cuivre 15mm",
                        "description": "Raccord à souder cuivre 15mm",
                        "price": Decimal("2.50"),
                        "cost": Decimal("1.25"),
                        "unit_of_measure": "pièce",
                        "barcode": "1234567890134",
                        "category_codes": ["TUBE"]
                    },
                    {
                        "code": "RAC-002",
                        "name": "Raccord Cuivre 22mm",
                        "description": "Raccord à souder cuivre 22mm",
                        "price": Decimal("3.90"),
                        "cost": Decimal("1.95"),
                        "unit_of_measure": "pièce",
                        "barcode": "1234567890135",
                        "category_codes": ["TUBE"]
                    },
                    # Accessoires
                    {
                        "code": "ACC-FLEX-001",
                        "name": "Flexible Robinet 30cm",
                        "description": "Flexible d'alimentation robinet, longueur 30cm",
                        "price": Decimal("8.90"),
                        "cost": Decimal("4.50"),
                        "unit_of_measure": "pièce",
                        "barcode": "1234567890136",
                        "category_codes": ["ACC"]
                    },
                    {
                        "code": "ACC-FLEX-002",
                        "name": "Flexible Robinet 50cm",
                        "description": "Flexible d'alimentation robinet, longueur 50cm",
                        "price": Decimal("12.90"),
                        "cost": Decimal("6.50"),
                        "unit_of_measure": "pièce",
                        "barcode": "1234567890137",
                        "category_codes": ["ACC"]
                    },
                    {
                        "code": "ACC-JOINT-001",
                        "name": "Joint Fibre 15mm",
                        "description": "Joint en fibre pour raccord 15mm, lot de 10",
                        "price": Decimal("4.90"),
                        "cost": Decimal("2.50"),
                        "unit_of_measure": "lot",
                        "barcode": "1234567890138",
                        "category_codes": ["ACC"]
                    },
                    # Vannes
                    {
                        "code": "VAN-001",
                        "name": "Vanne d'Arrêt 15mm",
                        "description": "Robinet d'arrêt 15mm, laiton chromé",
                        "price": Decimal("15.90"),
                        "cost": Decimal("8.00"),
                        "unit_of_measure": "pièce",
                        "barcode": "1234567890139",
                        "category_codes": ["VANNE"]
                    },
                    {
                        "code": "VAN-002",
                        "name": "Vanne d'Arrêt 22mm",
                        "description": "Robinet d'arrêt 22mm, laiton chromé",
                        "price": Decimal("22.90"),
                        "cost": Decimal("11.50"),
                        "unit_of_measure": "pièce",
                        "barcode": "1234567890140",
                        "category_codes": ["VANNE"]
                    },
                ]
                
                category_map = {
                    "ROB-EVIER": rob_evier,
                    "ROB-LAVABO": rob_lavabo,
                    "ROB-DOUCHE": rob_douche,
                    "TUBE": tube,
                    "ACC": acc,
                    "VANNE": vanne,
                }
                
                products_created = 0
                for prod_data in products_data:
                    # Get category IDs
                    category_ids = []
                    for cat_code in prod_data["category_codes"]:
                        cat = category_map.get(cat_code)
                        if cat:
                            category_ids.append(cat.id)
                    
                    if not category_ids:
                        print(f"  [WARN] No categories found for product {prod_data['code']}, skipping")
                        continue
                    
                    # Create product
                    product = Product.create(
                        code=prod_data["code"],
                        name=prod_data["name"],
                        description=prod_data.get("description"),
                        price=prod_data["price"],
                        cost=prod_data.get("cost"),
                        unit_of_measure=prod_data.get("unit_of_measure"),
                        barcode=prod_data.get("barcode"),
                        category_ids=category_ids
                    )
                    
                    # Add categories
                    categories = session.query(Category).filter(Category.id.in_(category_ids)).all()
                    product.categories = categories
                    
                    session.add(product)
                    session.flush()
                    products_created += 1
                    print(f"  [OK] Created product: {prod_data['code']} - {prod_data['name']}")
                
                session.commit()
                print(f"[OK] Created {products_created} products.")
            
            print("[OK] Seed completed successfully!")


if __name__ == "__main__":
    seed_categories_and_products()

