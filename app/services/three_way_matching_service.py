"""Service for 3-way matching of purchase orders, receipts, and supplier invoices."""
from decimal import Decimal
from typing import Optional, Dict, Tuple
from datetime import date

from sqlalchemy.orm import Session

from app.domain.models.purchase import (
    PurchaseOrder, PurchaseReceipt, SupplierInvoice,
    PurchaseOrderLine, PurchaseReceiptLine
)


class ThreeWayMatchingService:
    """Service for 3-way matching (PO/Receipt/Invoice)."""
    
    def __init__(self, session: Session):
        """
        Initialize the service.
        
        Args:
            session: SQLAlchemy session
        """
        self.session = session
    
    def match_invoice_with_po_and_receipt(
        self,
        supplier_invoice_id: int,
        purchase_order_id: int,
        purchase_receipt_id: Optional[int] = None,
        matched_by: int = None
    ) -> Dict[str, any]:
        """
        Perform 3-way matching between supplier invoice, purchase order, and receipt.
        
        Args:
            supplier_invoice_id: Supplier invoice ID
            purchase_order_id: Purchase order ID
            purchase_receipt_id: Purchase receipt ID (optional, will find if not provided)
            matched_by: User ID who performs the matching
            
        Returns:
            Dictionary with matching results:
            - matching_status: 'matched', 'partially_matched', 'unmatched'
            - discrepancies: List of discrepancy details
            - po_total: Purchase order total
            - receipt_total: Receipt total (if receipt provided)
            - invoice_total: Invoice total
        """
        # Get invoice
        invoice = self.session.get(SupplierInvoice, supplier_invoice_id)
        if not invoice:
            raise ValueError(f"Supplier invoice with ID {supplier_invoice_id} not found.")
        
        # Get purchase order
        po = self.session.get(PurchaseOrder, purchase_order_id)
        if not po:
            raise ValueError(f"Purchase order with ID {purchase_order_id} not found.")
        
        # Verify supplier matches
        if invoice.supplier_id != po.supplier_id:
            raise ValueError(
                f"Supplier mismatch: Invoice supplier ({invoice.supplier_id}) "
                f"does not match PO supplier ({po.supplier_id})."
            )
        
        # Get or find receipt
        receipt = None
        if purchase_receipt_id:
            receipt = self.session.get(PurchaseReceipt, purchase_receipt_id)
            if not receipt:
                raise ValueError(f"Purchase receipt with ID {purchase_receipt_id} not found.")
            
            if receipt.purchase_order_id != purchase_order_id:
                raise ValueError(
                    f"Receipt PO mismatch: Receipt PO ({receipt.purchase_order_id}) "
                    f"does not match provided PO ({purchase_order_id})."
                )
        else:
            # Find receipt for this PO
            receipt = self.session.query(PurchaseReceipt).filter(
                PurchaseReceipt.purchase_order_id == purchase_order_id,
                PurchaseReceipt.status == 'validated'
            ).first()
        
        # Perform matching
        discrepancies = []
        matching_status = 'matched'
        
        # Compare totals
        po_total = po.total_ttc
        invoice_total = invoice.total_ttc
        
        if abs(po_total - invoice_total) > Decimal('0.01'):  # Allow small rounding differences
            discrepancies.append({
                'type': 'total_mismatch',
                'description': f'PO total ({po_total}) does not match invoice total ({invoice_total})',
                'po_total': float(po_total),
                'invoice_total': float(invoice_total),
                'difference': float(invoice_total - po_total)
            })
            matching_status = 'partially_matched'
        
        # Compare with receipt if available
        if receipt:
            # Calculate receipt total from lines
            receipt_total = Decimal(0)
            for receipt_line in receipt.lines:
                po_line = self.session.get(PurchaseOrderLine, receipt_line.purchase_order_line_id)
                if po_line:
                    # Use PO line price for receipt total calculation
                    receipt_total += po_line.unit_price * receipt_line.quantity_received * (
                        Decimal(1) - po_line.discount_percent / Decimal(100)
                    ) * (Decimal(1) + po_line.tax_rate / Decimal(100))
            
            if abs(receipt_total - invoice_total) > Decimal('0.01'):
                discrepancies.append({
                    'type': 'receipt_mismatch',
                    'description': f'Receipt total ({receipt_total}) does not match invoice total ({invoice_total})',
                    'receipt_total': float(receipt_total),
                    'invoice_total': float(invoice_total),
                    'difference': float(invoice_total - receipt_total)
                })
                if matching_status == 'matched':
                    matching_status = 'partially_matched'
            
            # Check for quantity discrepancies in receipt lines
            for receipt_line in receipt.lines:
                if receipt_line.quantity_discrepancy != Decimal(0):
                    discrepancies.append({
                        'type': 'quantity_discrepancy',
                        'description': f'Product {receipt_line.product_id}: Ordered {receipt_line.quantity_ordered}, '
                                     f'Received {receipt_line.quantity_received}',
                        'product_id': receipt_line.product_id,
                        'quantity_ordered': float(receipt_line.quantity_ordered),
                        'quantity_received': float(receipt_line.quantity_received),
                        'discrepancy': float(receipt_line.quantity_discrepancy),
                        'reason': receipt_line.discrepancy_reason
                    })
                    if matching_status == 'matched':
                        matching_status = 'partially_matched'
        
        # If no receipt, check if PO is fully received
        if not receipt:
            # Check if PO has any received quantity
            has_receipts = self.session.query(PurchaseReceipt).filter(
                PurchaseReceipt.purchase_order_id == purchase_order_id,
                PurchaseReceipt.status == 'validated'
            ).first() is not None
            
            if not has_receipts:
                discrepancies.append({
                    'type': 'no_receipt',
                    'description': 'No validated receipt found for this purchase order',
                    'warning': True
                })
                matching_status = 'unmatched'
        
        # Match invoice
        matching_notes = None
        if discrepancies:
            matching_notes = "; ".join([d['description'] for d in discrepancies])
        
        invoice.match_with_po_and_receipt(
            purchase_order_id=purchase_order_id,
            purchase_receipt_id=receipt.id if receipt else None,
            matched_by=matched_by or invoice.created_by,
            matching_status=matching_status,
            matching_notes=matching_notes
        )
        
        return {
            'matching_status': matching_status,
            'discrepancies': discrepancies,
            'po_total': float(po_total),
            'receipt_total': float(receipt_total) if receipt else None,
            'invoice_total': float(invoice_total),
            'has_receipt': receipt is not None
        }
    
    def find_matching_po_for_invoice(
        self,
        supplier_invoice_id: int
    ) -> Optional[Tuple[PurchaseOrder, Optional[PurchaseReceipt]]]:
        """
        Automatically find matching purchase order and receipt for a supplier invoice.
        
        Args:
            supplier_invoice_id: Supplier invoice ID
            
        Returns:
            Tuple of (PurchaseOrder, PurchaseReceipt or None) if found, None otherwise
        """
        invoice = self.session.get(SupplierInvoice, supplier_invoice_id)
        if not invoice:
            raise ValueError(f"Supplier invoice with ID {supplier_invoice_id} not found.")
        
        # Find PO by supplier and invoice date range
        # Look for POs from the same supplier with order date around invoice date
        date_range_start = invoice.invoice_date
        date_range_end = invoice.invoice_date
        
        # Search for POs within 30 days of invoice date
        from datetime import timedelta
        date_range_start = date_range_start - timedelta(days=30)
        date_range_end = date_range_end + timedelta(days=30)
        
        matching_pos = self.session.query(PurchaseOrder).filter(
            PurchaseOrder.supplier_id == invoice.supplier_id,
            PurchaseOrder.order_date >= date_range_start,
            PurchaseOrder.order_date <= date_range_end,
            PurchaseOrder.status.in_(['confirmed', 'partially_received', 'received'])
        ).all()
        
        # Try to match by total amount (within 5% tolerance)
        tolerance = Decimal('0.05')
        for po in matching_pos:
            if abs(po.total_ttc - invoice.total_ttc) <= (po.total_ttc * tolerance):
                # Found potential match, get receipt if available
                receipt = self.session.query(PurchaseReceipt).filter(
                    PurchaseReceipt.purchase_order_id == po.id,
                    PurchaseReceipt.status == 'validated'
                ).first()
                
                return (po, receipt)
        
        return None




