from django.db import models
from .medical_record import MedicalRecord
from .patient import Patient
from .doctor import Doctor


class Prescription(models.Model):
    FREQUENCY_CHOICES = [
        ('once_daily', 'Once Daily (OD)'),
        ('twice_daily', 'Twice Daily (BD)'),
        ('three_times', 'Three Times Daily (TDS)'),
        ('four_times', 'Four Times Daily (QID)'),
        ('every_8hrs', 'Every 8 Hours'),
        ('every_6hrs', 'Every 6 Hours'),
        ('as_needed', 'As Needed (PRN)'),
        ('weekly', 'Weekly'),
        ('stat', 'Immediately (STAT)'),
        ('other', 'Other'),
    ]
    ROUTE_CHOICES = [
        ('oral', 'Oral (PO)'),
        ('iv', 'Intravenous (IV)'),
        ('im', 'Intramuscular (IM)'),
        ('sc', 'Subcutaneous (SC)'),
        ('topical', 'Topical'),
        ('inhalation', 'Inhalation'),
        ('sublingual', 'Sublingual'),
        ('rectal', 'Rectal'),
        ('ophthalmic', 'Ophthalmic'),
        ('otic', 'Otic'),
        ('nasal', 'Nasal'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('discontinued', 'Discontinued'),
        ('on_hold', 'On Hold'),
    ]

    prescription_id = models.CharField(max_length=20, unique=True, editable=False)
    medical_record = models.ForeignKey(
        MedicalRecord, on_delete=models.CASCADE,
        related_name='prescriptions', null=True, blank=True
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='prescriptions')

    medication_name = models.CharField(max_length=300)
    generic_name = models.CharField(max_length=300, blank=True)
    dosage = models.CharField(max_length=100, help_text='e.g. 500mg, 10ml')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    route = models.CharField(max_length=20, choices=ROUTE_CHOICES, default='oral')
    duration_days = models.PositiveIntegerField(null=True, blank=True, help_text='Treatment duration in days')
    quantity = models.PositiveIntegerField(null=True, blank=True, help_text='Total units dispensed')
    refills = models.PositiveIntegerField(default=0, help_text='Number of refills allowed')

    instructions = models.TextField(blank=True, help_text='Special instructions e.g. take with food')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    discontinuation_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'status']),
        ]

    def __str__(self):
        return f"{self.prescription_id} — {self.medication_name} for {self.patient.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.prescription_id:
            import uuid
            self.prescription_id = f"RX-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)