"""Service for exporting FEC (Fichier des Écritures Comptables) for French tax authorities."""
from io import BytesIO, StringIO
from decimal import Decimal
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy.orm import Session
from app.domain.models.invoice import Invoice, InvoiceLine
from app.domain.models.order import Order
from app.domain.models.customer import Customer


class FECExportService:
    """Service for exporting accounting entries to FEC format."""
    
    # FEC column headers (as per French tax authority requirements)
    FEC_COLUMNS = [
        "JournalCode",      # Code journal
        "JournalLib",       # Libellé journal
        "EcritureNum",      # Numéro d'écriture
        "EcritureDate",     # Date d'écriture (format YYYYMMDD)
        "CompteNum",        # Numéro de compte
        "CompteLib",        # Libellé de compte
        "CompAuxNum",       # Numéro de compte auxiliaire (client)
        "CompAuxLib",       # Libellé de compte auxiliaire
        "PieceRef",         # Référence de pièce (numéro facture)
        "PieceDate",        # Date de pièce (format YYYYMMDD)
        "EcritureLib",      # Libellé d'écriture
        "Debit",            # Montant débit
        "Credit",           # Montant crédit
        "EcritureLet",      # Lettrage
        "DateLet",          # Date de lettrage
        "ValidDate",        # Date de validation
        "Montantdevise",    # Montant en devise
        "Idevise"           # Identifiant devise
    ]
    
    def __init__(self, session: Session):
        """Initialize the service with a database session."""
        self.session = session
    
    def export_invoices_to_fec(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        invoice_ids: Optional[List[int]] = None
    ) -> BytesIO:
        """
        Export invoices to FEC format.
        
        Args:
            date_from: Start date for invoice filtering (optional)
            date_to: End date for invoice filtering (optional)
            invoice_ids: Specific invoice IDs to export (optional)
            
        Returns:
            BytesIO object containing the FEC file (UTF-8 encoded, tab-separated)
        """
        # Build query
        query = self.session.query(Invoice).filter(
            Invoice.status != "canceled"  # Exclude canceled invoices
        )
        
        if date_from:
            query = query.filter(Invoice.invoice_date >= date_from)
        
        if date_to:
            query = query.filter(Invoice.invoice_date <= date_to)
        
        if invoice_ids:
            query = query.filter(Invoice.id.in_(invoice_ids))
        
        # Order by invoice date and number
        invoices = query.order_by(Invoice.invoice_date, Invoice.number).all()
        
        # Generate FEC content
        fec_content = StringIO()
        
        # Write header (column names)
        fec_content.write("\t".join(self.FEC_COLUMNS))
        fec_content.write("\n")
        
        # Write invoice entries
        for invoice in invoices:
            # Load relationships
            self.session.refresh(invoice, ['customer', 'lines', 'order'])
            
            # Generate accounting entries for this invoice
            entries = self._generate_invoice_entries(invoice)
            
            for entry in entries:
                fec_content.write("\t".join(entry))
                fec_content.write("\n")
        
        # Convert to BytesIO with UTF-8 encoding
        fec_buffer = BytesIO()
        fec_buffer.write(fec_content.getvalue().encode('utf-8'))
        fec_buffer.seek(0)
        
        return fec_buffer
    
    def _generate_invoice_entries(self, invoice: Invoice) -> List[List[str]]:
        """
        Generate accounting entries for an invoice.
        
        Each invoice generates multiple accounting entries:
        1. Customer account (debit) - Total TTC
        2. Sales account (credit) - Total HT
        3. VAT account (credit) - VAT amount
        
        Args:
            invoice: Invoice object
            
        Returns:
            List of accounting entry rows (each row is a list of column values)
        """
        entries = []
        
        # Format dates
        invoice_date_str = invoice.invoice_date.strftime('%Y%m%d')
        validation_date_str = invoice.validated_at.strftime('%Y%m%d') if invoice.validated_at else invoice_date_str
        
        # Get customer info
        customer_code = ""
        customer_name = ""
        if invoice.customer:
            customer_code = getattr(invoice.customer, 'code', '') or ""
            if hasattr(invoice.customer, 'company_name') and invoice.customer.company_name:
                customer_name = invoice.customer.company_name
            elif hasattr(invoice.customer, 'name'):
                customer_name = invoice.customer.name
        
        # Entry 1: Customer account (Debit) - Total TTC
        entries.append([
            "VT",                          # JournalCode: Ventes (Sales)
            "Ventes",                      # JournalLib
            invoice.number,                # EcritureNum: Invoice number
            invoice_date_str,              # EcritureDate
            "411",                         # CompteNum: Customer account (411000 for general, 411XXX for specific)
            f"Clients - {customer_name}",  # CompteLib
            customer_code,                 # CompAuxNum: Customer code
            customer_name,                 # CompAuxLib
            invoice.number,                # PieceRef: Invoice number
            invoice_date_str,              # PieceDate
            f"Facture {invoice.number}",   # EcritureLib
            self._format_amount(invoice.total),  # Debit: Total TTC
            "0,00",                        # Credit
            "",                            # EcritureLet
            "",                            # DateLet
            validation_date_str,           # ValidDate
            "",                            # Montantdevise
            ""                             # Idevise
        ])
        
        # Entry 2: Sales account (Credit) - Total HT after discount
        total_ht_after_discount = invoice.subtotal - invoice.discount_amount
        entries.append([
            "VT",                          # JournalCode
            "Ventes",                      # JournalLib
            invoice.number,                # EcritureNum
            invoice_date_str,              # EcritureDate
            "701",                         # CompteNum: Sales account
            "Ventes de produits finis",    # CompteLib
            "",                            # CompAuxNum
            "",                            # CompAuxLib
            invoice.number,                # PieceRef
            invoice_date_str,              # PieceDate
            f"Facture {invoice.number}",   # EcritureLib
            "0,00",                        # Debit
            self._format_amount(total_ht_after_discount),  # Credit: Total HT
            "",                            # EcritureLet
            "",                            # DateLet
            validation_date_str,           # ValidDate
            "",                            # Montantdevise
            ""                             # Idevise
        ])
        
        # Entry 3: VAT account (Credit) - VAT amount
        if invoice.tax_amount > 0:
            entries.append([
                "VT",                          # JournalCode
                "Ventes",                      # JournalLib
                invoice.number,                # EcritureNum
                invoice_date_str,              # EcritureDate
                "44571",                       # CompteNum: VAT to collect (TVA à décaisser)
                "TVA collectée",               # CompteLib
                "",                            # CompAuxNum
                "",                            # CompAuxLib
                invoice.number,                # PieceRef
                invoice_date_str,              # PieceDate
                f"Facture {invoice.number}",   # EcritureLib
                "0,00",                        # Debit
                self._format_amount(invoice.tax_amount),  # Credit: VAT amount
                "",                            # EcritureLet
                "",                            # DateLet
                validation_date_str,           # ValidDate
                "",                            # Montantdevise
                ""                             # Idevise
            ])
        
        # If discount applied, add discount entry
        if invoice.discount_amount > 0:
            entries.append([
                "VT",                          # JournalCode
                "Ventes",                      # JournalLib
                invoice.number,                # EcritureNum
                invoice_date_str,              # EcritureDate
                "709",                         # CompteNum: Discounts granted
                "Rabais, remises et ristournes obtenus",  # CompteLib
                "",                            # CompAuxNum
                "",                            # CompAuxLib
                invoice.number,                # PieceRef
                invoice_date_str,              # PieceDate
                f"Remise facture {invoice.number}",  # EcritureLib
                self._format_amount(invoice.discount_amount),  # Debit: Discount amount
                "0,00",                        # Credit
                "",                            # EcritureLet
                "",                            # DateLet
                validation_date_str,           # ValidDate
                "",                            # Montantdevise
                ""                             # Idevise
            ])
        
        return entries
    
    def _format_amount(self, amount: Decimal) -> str:
        """
        Format amount for FEC (French format: comma as decimal separator).
        
        Args:
            amount: Decimal amount
            
        Returns:
            Formatted string (e.g., "1234,56")
        """
        if amount is None:
            return "0,00"
        
        # Convert to float, format with 2 decimals, replace dot with comma
        return f"{float(amount):.2f}".replace('.', ',')
    
    def export_credit_notes_to_fec(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        credit_note_ids: Optional[List[int]] = None
    ) -> BytesIO:
        """
        Export credit notes to FEC format.
        
        Args:
            date_from: Start date for credit note filtering (optional)
            date_to: End date for credit note filtering (optional)
            credit_note_ids: Specific credit note IDs to export (optional)
            
        Returns:
            BytesIO object containing the FEC file
        """
        from app.domain.models.invoice import CreditNote
        
        # Build query
        query = self.session.query(CreditNote).filter(
            CreditNote.status != "canceled"
        )
        
        if date_from:
            query = query.filter(CreditNote.created_at >= date_from)
        
        if date_to:
            query = query.filter(CreditNote.created_at <= date_to)
        
        if credit_note_ids:
            query = query.filter(CreditNote.id.in_(credit_note_ids))
        
        credit_notes = query.order_by(CreditNote.created_at, CreditNote.number).all()
        
        # Generate FEC content
        fec_content = StringIO()
        
        # Write header
        fec_content.write("\t".join(self.FEC_COLUMNS))
        fec_content.write("\n")
        
        # Write credit note entries
        for credit_note in credit_notes:
            self.session.refresh(credit_note, ['customer', 'invoice'])
            
            entries = self._generate_credit_note_entries(credit_note)
            
            for entry in entries:
                fec_content.write("\t".join(entry))
                fec_content.write("\n")
        
        # Convert to BytesIO
        fec_buffer = BytesIO()
        fec_buffer.write(fec_content.getvalue().encode('utf-8'))
        fec_buffer.seek(0)
        
        return fec_buffer
    
    def _generate_credit_note_entries(self, credit_note) -> List[List[str]]:
        """Generate accounting entries for a credit note (reverse of invoice)."""
        entries = []
        
        # Format dates
        cn_date_str = credit_note.created_at.strftime('%Y%m%d')
        validation_date_str = credit_note.validated_at.strftime('%Y%m%d') if credit_note.validated_at else cn_date_str
        
        # Get customer info
        customer_code = ""
        customer_name = ""
        if credit_note.customer:
            customer_code = getattr(credit_note.customer, 'code', '') or ""
            if hasattr(credit_note.customer, 'company_name') and credit_note.customer.company_name:
                customer_name = credit_note.customer.company_name
            elif hasattr(credit_note.customer, 'name'):
                customer_name = credit_note.customer.name
        
        # Entry 1: Customer account (Credit) - Total TTC (reverse)
        entries.append([
            "VT",
            "Ventes",
            credit_note.number,
            cn_date_str,
            "411",
            f"Clients - {customer_name}",
            customer_code,
            customer_name,
            credit_note.number,
            cn_date_str,
            f"Avoir {credit_note.number}",
            "0,00",
            self._format_amount(credit_note.total_ttc),  # Credit (reverse)
            "",
            "",
            validation_date_str,
            "",
            ""
        ])
        
        # Entry 2: Sales account (Debit) - Total HT (reverse)
        entries.append([
            "VT",
            "Ventes",
            credit_note.number,
            cn_date_str,
            "701",
            "Ventes de produits finis",
            "",
            "",
            credit_note.number,
            cn_date_str,
            f"Avoir {credit_note.number}",
            self._format_amount(credit_note.total_amount),  # Debit (reverse)
            "0,00",
            "",
            "",
            validation_date_str,
            "",
            ""
        ])
        
        # Entry 3: VAT account (Debit) - VAT amount (reverse)
        if credit_note.tax_amount > 0:
            entries.append([
                "VT",
                "Ventes",
                credit_note.number,
                cn_date_str,
                "44571",
                "TVA collectée",
                "",
                "",
                credit_note.number,
                cn_date_str,
                f"Avoir {credit_note.number}",
                self._format_amount(credit_note.tax_amount),  # Debit (reverse)
                "0,00",
                "",
                "",
                validation_date_str,
                "",
                ""
            ])
        
        return entries

