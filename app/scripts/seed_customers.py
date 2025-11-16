"""Seed script for customers (B2B and B2C) for a plumbing fixtures wholesaler."""
from decimal import Decimal
from datetime import date
from app import create_app
from app.infrastructure.db import get_session
from app.domain.models.customer import Customer, CommercialConditions


def seed_customers() -> None:
    """Seed customers for a plumbing fixtures wholesaler."""
    app = create_app()
    with app.app_context():
        with get_session() as session:
            # Check if customers already exist
            existing = session.query(Customer).first()
            if existing:
                print("[SKIP] Customers already exist. Skipping seed.")
                return
            
            customers_data = [
                # B2B Customers
                {
                    "type": "B2B",
                    "name": "Plomberie Pro Marseille",
                    "email": "contact@plomberie-pro-marseille.fr",
                    "phone": "+33 4 91 23 45 67",
                    "mobile": "+33 6 12 34 56 78",
                    "category": "VIP",
                    "company_name": "Plomberie Pro Marseille SARL",
                    "siret": "12345678901234",
                    "vat_number": "FR12345678901",
                    "rcs": "Marseille B 123 456 789",
                    "legal_form": "SARL",
                    "notes": "Client principal région PACA, commandes régulières",
                    "payment_terms_days": 30,
                    "default_discount_percent": Decimal("5.00"),
                    "credit_limit": Decimal("50000.00"),
                    "block_on_credit_exceeded": True
                },
                {
                    "type": "B2B",
                    "name": "Sanitaires Express Lyon",
                    "email": "commercial@sanitaires-express-lyon.fr",
                    "phone": "+33 4 72 34 56 78",
                    "mobile": "+33 6 23 45 67 89",
                    "category": "Standard",
                    "company_name": "Sanitaires Express Lyon SAS",
                    "siret": "23456789012345",
                    "vat_number": "FR23456789012",
                    "rcs": "Lyon B 234 567 890",
                    "legal_form": "SAS",
                    "notes": "Client régulier, spécialisé en sanitaires",
                    "payment_terms_days": 45,
                    "default_discount_percent": Decimal("3.00"),
                    "credit_limit": Decimal("30000.00"),
                    "block_on_credit_exceeded": True
                },
                {
                    "type": "B2B",
                    "name": "Robinetterie Moderne Paris",
                    "email": "ventes@robinetterie-moderne-paris.fr",
                    "phone": "+33 1 45 67 89 01",
                    "mobile": "+33 6 34 56 78 90",
                    "category": "VIP",
                    "company_name": "Robinetterie Moderne Paris SA",
                    "siret": "34567890123456",
                    "vat_number": "FR34567890123",
                    "rcs": "Paris B 345 678 901",
                    "legal_form": "SA",
                    "notes": "Grand compte, commandes importantes mensuelles",
                    "payment_terms_days": 60,
                    "default_discount_percent": Decimal("8.00"),
                    "credit_limit": Decimal("100000.00"),
                    "block_on_credit_exceeded": False
                },
                {
                    "type": "B2B",
                    "name": "Tubes et Raccords Toulouse",
                    "email": "info@tubes-raccords-toulouse.fr",
                    "phone": "+33 5 61 23 45 67",
                    "mobile": "+33 6 45 67 89 01",
                    "category": "Standard",
                    "company_name": "Tubes et Raccords Toulouse SARL",
                    "siret": "45678901234567",
                    "vat_number": "FR45678901234",
                    "rcs": "Toulouse B 456 789 012",
                    "legal_form": "SARL",
                    "notes": "Spécialiste en tubes et raccords",
                    "payment_terms_days": 30,
                    "default_discount_percent": Decimal("2.00"),
                    "credit_limit": Decimal("20000.00"),
                    "block_on_credit_exceeded": True
                },
                # B2C Customers
                {
                    "type": "B2C",
                    "name": "Jean Dupont",
                    "email": "jean.dupont@email.fr",
                    "phone": "+33 1 23 45 67 89",
                    "mobile": "+33 6 12 34 56 78",
                    "category": "Standard",
                    "first_name": "Jean",
                    "last_name": "Dupont",
                    "birth_date": date(1980, 5, 15),
                    "notes": "Client particulier, rénovation maison",
                    "payment_terms_days": 0,
                    "default_discount_percent": Decimal("0.00"),
                    "credit_limit": Decimal("0.00"),
                    "block_on_credit_exceeded": True
                },
                {
                    "type": "B2C",
                    "name": "Marie Martin",
                    "email": "marie.martin@email.fr",
                    "phone": "+33 1 34 56 78 90",
                    "mobile": "+33 6 23 45 67 89",
                    "category": "VIP",
                    "first_name": "Marie",
                    "last_name": "Martin",
                    "birth_date": date(1975, 8, 22),
                    "notes": "Client fidèle, plusieurs commandes par an",
                    "payment_terms_days": 0,
                    "default_discount_percent": Decimal("2.00"),
                    "credit_limit": Decimal("0.00"),
                    "block_on_credit_exceeded": True
                },
                {
                    "type": "B2C",
                    "name": "Pierre Bernard",
                    "email": "pierre.bernard@email.fr",
                    "phone": "+33 1 45 67 89 01",
                    "mobile": "+33 6 34 56 78 90",
                    "category": "Standard",
                    "first_name": "Pierre",
                    "last_name": "Bernard",
                    "birth_date": date(1990, 3, 10),
                    "notes": "Nouveau client, première commande",
                    "payment_terms_days": 0,
                    "default_discount_percent": Decimal("0.00"),
                    "credit_limit": Decimal("0.00"),
                    "block_on_credit_exceeded": True
                },
                {
                    "type": "B2C",
                    "name": "Sophie Dubois",
                    "email": "sophie.dubois@email.fr",
                    "phone": "+33 1 56 78 90 12",
                    "mobile": "+33 6 45 67 89 01",
                    "category": "Standard",
                    "first_name": "Sophie",
                    "last_name": "Dubois",
                    "birth_date": date(1985, 11, 5),
                    "notes": "Client occasionnel",
                    "payment_terms_days": 0,
                    "default_discount_percent": Decimal("0.00"),
                    "credit_limit": Decimal("0.00"),
                    "block_on_credit_exceeded": True
                }
            ]
            
            for customer_data in customers_data:
                # Extract commercial conditions
                conditions_data = {
                    "payment_terms_days": customer_data.pop("payment_terms_days"),
                    "default_discount_percent": customer_data.pop("default_discount_percent"),
                    "credit_limit": customer_data.pop("credit_limit"),
                    "block_on_credit_exceeded": customer_data.pop("block_on_credit_exceeded")
                }
                
                # Create customer
                customer = Customer.create(**customer_data)
                session.add(customer)
                session.flush()  # Get customer.id
                
                # Create commercial conditions
                conditions = CommercialConditions(
                    customer_id=customer.id,
                    payment_terms_days=conditions_data["payment_terms_days"],
                    default_discount_percent=conditions_data["default_discount_percent"],
                    credit_limit=conditions_data["credit_limit"],
                    block_on_credit_exceeded=conditions_data["block_on_credit_exceeded"]
                )
                session.add(conditions)
            
            session.commit()
            # Count by type before processing
            b2b_count = sum(1 for c in customers_data if c["type"] == "B2B")
            b2c_count = sum(1 for c in customers_data if c["type"] == "B2C")
            print(f"[OK] Created {len(customers_data)} customers successfully:")
            print(f"  - {b2b_count} B2B customers")
            print(f"  - {b2c_count} B2C customers")


if __name__ == "__main__":
    seed_customers()

