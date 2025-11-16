"""Seed script for suppliers for a plumbing fixtures wholesaler."""
from decimal import Decimal
from app import create_app
from app.infrastructure.db import get_session
from app.domain.models.supplier import Supplier, SupplierConditions


def seed_suppliers() -> None:
    """Seed suppliers for a plumbing fixtures wholesaler."""
    app = create_app()
    with app.app_context():
        with get_session() as session:
            # Check if suppliers already exist
            existing = session.query(Supplier).first()
            if existing:
                print("[SKIP] Suppliers already exist. Skipping seed.")
                return
            
            suppliers_data = [
                {
                    "name": "Grohe France",
                    "email": "contact@grohe.fr",
                    "phone": "+33 1 45 67 89 00",
                    "company_name": "Grohe France SAS",
                    "siret": "12345678901234",
                    "vat_number": "FR12345678901",
                    "rcs": "Paris B 123 456 789",
                    "legal_form": "SAS",
                    "category": "Primary",
                    "notes": "Fournisseur principal pour robinetterie haut de gamme",
                    "payment_terms_days": 30,
                    "default_discount_percent": Decimal("10.00"),
                    "minimum_order_amount": Decimal("1000.00"),
                    "delivery_lead_time_days": 7
                },
                {
                    "name": "Hansgrohe Distribution",
                    "email": "commercial@hansgrohe.fr",
                    "phone": "+33 1 23 45 67 89",
                    "company_name": "Hansgrohe Distribution SARL",
                    "siret": "23456789012345",
                    "vat_number": "FR23456789012",
                    "rcs": "Paris B 234 567 890",
                    "legal_form": "SARL",
                    "category": "Primary",
                    "notes": "Fournisseur premium pour douches et robinetterie",
                    "payment_terms_days": 45,
                    "default_discount_percent": Decimal("8.00"),
                    "minimum_order_amount": Decimal("1500.00"),
                    "delivery_lead_time_days": 10
                },
                {
                    "name": "Ideal Standard France",
                    "email": "ventes@idealstandard.fr",
                    "phone": "+33 1 34 56 78 90",
                    "company_name": "Ideal Standard France SA",
                    "siret": "34567890123456",
                    "vat_number": "FR34567890123",
                    "rcs": "Lyon B 345 678 901",
                    "legal_form": "SA",
                    "category": "Primary",
                    "notes": "Fournisseur pour sanitaires et robinetterie standard",
                    "payment_terms_days": 30,
                    "default_discount_percent": Decimal("5.00"),
                    "minimum_order_amount": Decimal("500.00"),
                    "delivery_lead_time_days": 5
                },
                {
                    "name": "Tubes et Raccords Pro",
                    "email": "info@tubes-raccords-pro.fr",
                    "phone": "+33 1 45 78 90 12",
                    "company_name": "Tubes et Raccords Pro SARL",
                    "siret": "45678901234567",
                    "vat_number": "FR45678901234",
                    "rcs": "Marseille B 456 789 012",
                    "legal_form": "SARL",
                    "category": "Secondary",
                    "notes": "Spécialiste en tubes, raccords et accessoires plomberie",
                    "payment_terms_days": 30,
                    "default_discount_percent": Decimal("3.00"),
                    "minimum_order_amount": Decimal("300.00"),
                    "delivery_lead_time_days": 3
                },
                {
                    "name": "Accessoires Plomberie Express",
                    "email": "contact@accessoires-plomberie.fr",
                    "phone": "+33 1 56 78 90 23",
                    "company_name": "Accessoires Plomberie Express SAS",
                    "siret": "56789012345678",
                    "vat_number": "FR56789012345",
                    "rcs": "Toulouse B 567 890 123",
                    "legal_form": "SAS",
                    "category": "Secondary",
                    "notes": "Fournisseur rapide pour petits accessoires et pièces détachées",
                    "payment_terms_days": 15,
                    "default_discount_percent": Decimal("2.00"),
                    "minimum_order_amount": Decimal("100.00"),
                    "delivery_lead_time_days": 2
                },
                {
                    "name": "Villeroy & Boch France",
                    "email": "b2b@villeroy-boch.fr",
                    "phone": "+33 1 67 89 01 34",
                    "company_name": "Villeroy & Boch France SA",
                    "siret": "67890123456789",
                    "vat_number": "FR67890123456",
                    "rcs": "Paris B 678 901 234",
                    "legal_form": "SA",
                    "category": "Primary",
                    "notes": "Fournisseur luxe pour sanitaires et carrelage",
                    "payment_terms_days": 60,
                    "default_discount_percent": Decimal("12.00"),
                    "minimum_order_amount": Decimal("2000.00"),
                    "delivery_lead_time_days": 14
                }
            ]
            
            for supplier_data in suppliers_data:
                # Extract conditions
                conditions_data = {
                    "payment_terms_days": supplier_data.pop("payment_terms_days"),
                    "default_discount_percent": supplier_data.pop("default_discount_percent"),
                    "minimum_order_amount": supplier_data.pop("minimum_order_amount"),
                    "delivery_lead_time_days": supplier_data.pop("delivery_lead_time_days")
                }
                
                # Create supplier
                supplier = Supplier.create(
                    name=supplier_data["name"],
                    email=supplier_data["email"],
                    phone=supplier_data.get("phone"),
                    company_name=supplier_data.get("company_name"),
                    siret=supplier_data.get("siret"),
                    vat_number=supplier_data.get("vat_number"),
                    rcs=supplier_data.get("rcs"),
                    legal_form=supplier_data.get("legal_form"),
                    category=supplier_data.get("category"),
                    notes=supplier_data.get("notes")
                )
                
                session.add(supplier)
                session.flush()  # Get supplier.id
                
                # Create supplier conditions
                conditions = SupplierConditions(
                    supplier_id=supplier.id,
                    payment_terms_days=conditions_data["payment_terms_days"],
                    default_discount_percent=conditions_data["default_discount_percent"],
                    minimum_order_amount=conditions_data["minimum_order_amount"],
                    delivery_lead_time_days=conditions_data["delivery_lead_time_days"]
                )
                session.add(conditions)
            
            session.commit()
            print(f"[OK] Created {len(suppliers_data)} suppliers successfully.")


if __name__ == "__main__":
    seed_suppliers()

