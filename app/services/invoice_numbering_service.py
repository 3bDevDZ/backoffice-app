"""Service for managing sequential invoice numbering without gaps (French legal requirement)."""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.domain.models.invoice import Invoice
from app.domain.models.order import Order


class InvoiceNumberingService:
    """Service for generating sequential invoice numbers without gaps."""
    
    def __init__(self, session: Session):
        """Initialize the service with a database session."""
        self.session = session
    
    def generate_invoice_number(self, year: Optional[int] = None) -> str:
        """
        Generate the next sequential invoice number in format FA-YYYY-XXXXX.
        
        This ensures no gaps in numbering, which is required by French tax law
        (Article 242 nonies A de l'annexe II au CGI).
        
        Args:
            year: Year for the invoice number (defaults to current year)
            
        Returns:
            Invoice number in format FA-YYYY-XXXXX
        """
        if year is None:
            year = datetime.now().year
        
        # Find the last invoice number for this year
        last_invoice = self.session.query(Invoice).filter(
            Invoice.number.like(f"FA-{year}-%")
        ).order_by(Invoice.id.desc()).first()
        
        if last_invoice:
            # Extract sequence number from last invoice
            try:
                parts = last_invoice.number.split('-')
                if len(parts) == 3 and parts[0] == 'FA' and parts[1] == str(year):
                    sequence = int(parts[2])
                    sequence += 1
                else:
                    # Invalid format, start from 1
                    sequence = 1
            except (ValueError, IndexError):
                # Invalid format, start from 1
                sequence = 1
        else:
            # No invoices for this year, start from 1
            sequence = 1
        
        return f"FA-{year}-{sequence:05d}"
    
    def generate_credit_note_number(self, year: Optional[int] = None) -> str:
        """
        Generate the next sequential credit note number in format AV-YYYY-XXXXX.
        
        Args:
            year: Year for the credit note number (defaults to current year)
            
        Returns:
            Credit note number in format AV-YYYY-XXXXX
        """
        if year is None:
            year = datetime.now().year
        
        from app.domain.models.invoice import CreditNote
        
        # Find the last credit note number for this year
        last_credit_note = self.session.query(CreditNote).filter(
            CreditNote.number.like(f"AV-{year}-%")
        ).order_by(CreditNote.id.desc()).first()
        
        if last_credit_note:
            # Extract sequence number from last credit note
            try:
                parts = last_credit_note.number.split('-')
                if len(parts) == 3 and parts[0] == 'AV' and parts[1] == str(year):
                    sequence = int(parts[2])
                    sequence += 1
                else:
                    # Invalid format, start from 1
                    sequence = 1
            except (ValueError, IndexError):
                # Invalid format, start from 1
                sequence = 1
        else:
            # No credit notes for this year, start from 1
            sequence = 1
        
        return f"AV-{year}-{sequence:05d}"
    
    def validate_invoice_number(self, number: str) -> bool:
        """
        Validate that an invoice number follows the correct format FA-YYYY-XXXXX.
        
        Args:
            number: Invoice number to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            parts = number.split('-')
            if len(parts) != 3:
                return False
            
            prefix, year_str, sequence_str = parts
            
            if prefix != 'FA':
                return False
            
            year = int(year_str)
            if year < 2000 or year > 2100:
                return False
            
            sequence = int(sequence_str)
            if sequence < 1 or len(sequence_str) != 5:
                return False
            
            return True
        except (ValueError, IndexError):
            return False
    
    def find_gaps(self, year: Optional[int] = None) -> list:
        """
        Find gaps in invoice numbering for a given year.
        This is useful for detecting numbering issues.
        
        Args:
            year: Year to check (defaults to current year)
            
        Returns:
            List of missing sequence numbers
        """
        if year is None:
            year = datetime.now().year
        
        # Get all invoice numbers for this year
        invoices = self.session.query(Invoice).filter(
            Invoice.number.like(f"FA-{year}-%")
        ).order_by(Invoice.number).all()
        
        if not invoices:
            return []
        
        # Extract sequence numbers
        sequences = []
        for invoice in invoices:
            try:
                parts = invoice.number.split('-')
                if len(parts) == 3 and parts[0] == 'FA' and parts[1] == str(year):
                    sequences.append(int(parts[2]))
            except (ValueError, IndexError):
                continue
        
        if not sequences:
            return []
        
        # Find gaps
        min_seq = min(sequences)
        max_seq = max(sequences)
        all_sequences = set(range(min_seq, max_seq + 1))
        existing_sequences = set(sequences)
        gaps = sorted(all_sequences - existing_sequences)
        
        return gaps

