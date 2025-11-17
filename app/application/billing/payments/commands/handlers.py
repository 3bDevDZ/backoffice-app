"""Command handlers for payment management."""
from decimal import Decimal
from datetime import date
from app.application.common.cqrs import CommandHandler
from app.domain.models.payment import Payment, PaymentAllocation, PaymentMethod, PaymentStatus
from app.domain.models.invoice import Invoice
from app.infrastructure.db import get_session
from .commands import (
    CreatePaymentCommand, AllocatePaymentCommand, ReconcilePaymentCommand, ImportBankStatementCommand,
    ConfirmPaymentCommand, PaymentAllocationInput
)


class CreatePaymentHandler(CommandHandler):
    """Handler for creating a new payment."""
    
    def handle(self, command: CreatePaymentCommand) -> int:
        """
        Create a new payment.
        
        Args:
            command: CreatePaymentCommand with payment details
            
        Returns:
            Payment ID (int) to avoid detached instance issues
        """
        with get_session() as session:
            # Convert payment method string to enum
            try:
                payment_method = PaymentMethod(command.payment_method)
            except ValueError:
                raise ValueError(f"Invalid payment method: {command.payment_method}")
            
            # Create payment
            payment = Payment.create(
                customer_id=command.customer_id,
                payment_method=payment_method,
                amount=command.amount,
                payment_date=command.payment_date,
                value_date=command.value_date,
                reference=command.reference,
                notes=command.notes,
                internal_notes=command.internal_notes,
                created_by=command.created_by
            )
            
            session.add(payment)
            session.flush()  # Get payment.id for allocations
            
            # Update domain events with payment ID
            events = payment.get_domain_events()
            for event in events:
                if hasattr(event, 'payment_id'):
                    event.payment_id = payment.id
            
            # Process automatic allocation if strategy is provided
            if command.auto_allocation_strategy:
                from app.services.payment_auto_allocation_service import PaymentAutoAllocationService
                
                # Auto-allocate payment to invoices
                auto_allocation_service = PaymentAutoAllocationService(session)
                auto_allocations = auto_allocation_service.allocate_payment(
                    customer_id=command.customer_id,
                    payment_amount=command.amount,
                    strategy=command.auto_allocation_strategy
                )
                
                # Convert to PaymentAllocationInput and add to allocations
                for alloc in auto_allocations:
                    command.allocations.append(
                        PaymentAllocationInput(
                            invoice_id=alloc['invoice_id'],
                            amount=alloc['amount']
                        )
                    )
            
            # Process initial allocations if provided
            if command.allocations:
                for alloc_input in command.allocations:
                    # Get invoice
                    invoice = session.get(Invoice, alloc_input.invoice_id)
                    if not invoice:
                        raise ValueError(f"Invoice with ID {alloc_input.invoice_id} not found.")
                    
                    # Allocate payment to invoice
                    payment.allocate_to_invoice(
                        invoice_id=alloc_input.invoice_id,
                        amount=alloc_input.amount,
                        created_by=command.created_by
                    )
                    
                    # Update invoice payment tracking
                    invoice.mark_paid(alloc_input.amount)
            
            # Confirm payment automatically after creation (standard business practice)
            # A payment is considered confirmed once it's recorded
            if payment.status == PaymentStatus.PENDING:
                payment.confirm()
            
            payment_id = payment.id
            session.commit()
            
            return payment_id


class AllocatePaymentHandler(CommandHandler):
    """Handler for allocating a payment to invoices."""
    
    def handle(self, command: AllocatePaymentCommand) -> int:
        """
        Allocate a payment to one or more invoices.
        
        Args:
            command: AllocatePaymentCommand with payment_id and allocations
            
        Returns:
            Payment ID (int)
        """
        with get_session() as session:
            payment = session.get(Payment, command.payment_id)
            if not payment:
                raise ValueError(f"Payment with ID {command.payment_id} not found.")
            
            # Validate payment status
            if payment.status == PaymentStatus.CANCELLED:
                raise ValueError(f"Cannot allocate cancelled payment '{payment.id}'.")
            
            # Process allocations
            for alloc_input in command.allocations:
                # Get invoice
                invoice = session.get(Invoice, alloc_input.invoice_id)
                if not invoice:
                    raise ValueError(f"Invoice with ID {alloc_input.invoice_id} not found.")
                
                # Validate invoice status
                if invoice.status in ["draft", "canceled"]:
                    raise ValueError(
                        f"Cannot allocate payment to invoice '{invoice.number}' in status '{invoice.status}'."
                    )
                
                # Allocate payment to invoice
                payment.allocate_to_invoice(
                    invoice_id=alloc_input.invoice_id,
                    amount=alloc_input.amount,
                    created_by=command.created_by
                )
                
                # Update invoice payment tracking
                invoice.mark_paid(alloc_input.amount)
            
            payment_id = payment.id
            session.commit()
            
            return payment_id


class ReconcilePaymentHandler(CommandHandler):
    """Handler for reconciling a payment with bank statement."""
    
    def handle(self, command: ReconcilePaymentCommand) -> int:
        """
        Reconcile a payment with bank statement.
        
        Args:
            command: ReconcilePaymentCommand with payment_id and bank details
            
        Returns:
            Payment ID (int)
        """
        with get_session() as session:
            payment = session.get(Payment, command.payment_id)
            if not payment:
                raise ValueError(f"Payment with ID {command.payment_id} not found.")
            
            # Reconcile payment
            payment.reconcile(
                bank_reference=command.bank_reference,
                bank_account=command.bank_account,
                reconciled_by=command.reconciled_by
            )
            
            payment_id = payment.id
            session.commit()
            
            return payment_id


class ImportBankStatementHandler(CommandHandler):
    """Handler for importing bank statement and auto-reconciling payments."""
    
    def handle(self, command: ImportBankStatementCommand) -> dict:
        """
        Import bank statement and auto-reconcile payments.
        
        Args:
            command: ImportBankStatementCommand with bank account and transactions
            
        Returns:
            dict with reconciliation results
        """
        from app.services.bank_reconciliation_service import BankReconciliationService
        
        with get_session() as session:
            reconciliation_service = BankReconciliationService(session=session)
            
            results = reconciliation_service.reconcile_statement(
                bank_account=command.bank_account,
                statement_date=command.statement_date,
                transactions=command.transactions,
                imported_by=command.imported_by
            )
            
            session.commit()
            
            return results


class ConfirmPaymentHandler(CommandHandler):
    """Handler for confirming a payment."""
    
    def handle(self, command: ConfirmPaymentCommand) -> int:
        """
        Confirm a pending payment.
        
        Args:
            command: ConfirmPaymentCommand with payment_id
            
        Returns:
            Payment ID (int)
        """
        with get_session() as session:
            payment = session.get(Payment, command.payment_id)
            if not payment:
                raise ValueError(f"Payment with ID {command.payment_id} not found.")
            
            # Confirm payment
            payment.confirm()
            
            payment_id = payment.id
            session.commit()
            
            return payment_id

