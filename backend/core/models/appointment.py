from django.db import models
from .patient import Patient
from .doctor import Doctor


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    TYPE_CHOICES = [
        ('consultation', 'Consultation'),
        ('follow_up', 'Follow-Up'),
        ('procedure', 'Procedure'),
        ('lab_review', 'Lab Review'),
        ('emergency', 'Emergency'),
        ('checkup', 'Routine Checkup'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    appointment_id = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')

    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=30)

    appointment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='consultation')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='scheduled')

    reason = models.TextField(help_text='Chief complaint / reason for visit')
    notes = models.TextField(blank=True, help_text='Doctor notes after consultation')
    cancellation_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        indexes = [
            models.Index(fields=['appointment_date', 'doctor']),
            models.Index(fields=['patient', 'status']),
        ]
        # Prevent double-booking
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'appointment_date', 'appointment_time'],
                condition=models.Q(status__in=['scheduled', 'confirmed', 'in_progress']),
                name='unique_doctor_slot'
            )
        ]

    def __str__(self):
        return f"{self.appointment_id} — {self.patient.get_full_name()} with {self.doctor.get_full_name()} on {self.appointment_date}"

    def save(self, *args, **kwargs):
        if not self.appointment_id:
            import uuid
            self.appointment_id = f"APT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)