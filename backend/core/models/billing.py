from django.db import models
from .patient import Patient
from .appointment import Appointment


class Invoice(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('waived', 'Waived'),
        ('refunded', 'Refunded'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('card', 'Credit / Debit Card'),
        ('insurance', 'Insurance'),
        ('nhif', 'NHIF'),
        ('bank_transfer', 'Bank Transfer'),
    ]

    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='invoices')
    appointment = models.OneToOneField(
        Appointment, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='invoice'
    )

    invoice_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    insurance_covered = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    mpesa_transaction_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-invoice_date']

    def __str__(self):
        return f"{self.invoice_number} — {self.patient.get_full_name()} ({self.payment_status})"

    @property
    def balance_due(self):
        return self.total_amount - self.amount_paid

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            import uuid
            self.invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
        # Recalculate total
        self.total_amount = self.subtotal - self.discount_amount + self.tax_amount - self.insurance_covered
        # Update payment status
        if self.amount_paid <= 0:
            self.payment_status = 'pending'
        elif self.amount_paid >= self.total_amount:
            self.payment_status = 'paid'
        else:
            self.payment_status = 'partial'
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('consultation', 'Consultation Fee'),
        ('procedure', 'Procedure'),
        ('medication', 'Medication'),
        ('lab', 'Laboratory Test'),
        ('radiology', 'Radiology'),
        ('bed', 'Bed / Ward Charges'),
        ('other', 'Other'),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=20, choices=ITEM_TYPE_CHOICES)
    description = models.CharField(max_length=500)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    class Meta:
        ordering = ['item_type']

    def __str__(self):
        return f"{self.description} x{self.quantity} = KES {self.total_price}"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)