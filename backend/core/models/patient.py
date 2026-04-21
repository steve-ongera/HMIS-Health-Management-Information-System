from django.db import models


class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('deceased', 'Deceased'),
    ]

    # Identity
    patient_id = models.CharField(max_length=20, unique=True, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    national_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='patients/photos/', blank=True, null=True)

    # Contact
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)

    # Medical
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, blank=True)
    allergies = models.TextField(blank=True, help_text='Comma-separated list of allergies')
    chronic_conditions = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True)

    # Insurance
    insurance_provider = models.CharField(max_length=200, blank=True)
    insurance_policy_number = models.CharField(max_length=100, blank=True)
    nhif_number = models.CharField(max_length=50, blank=True, verbose_name='NHIF Number')

    # System
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-registered_at']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['patient_id']),
            models.Index(fields=['phone_number']),
        ]

    def __str__(self):
        return f"{self.patient_id} — {self.get_full_name()}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        from datetime import date
        today = date.today()
        dob = self.date_of_birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def save(self, *args, **kwargs):
        if not self.patient_id:
            import uuid
            self.patient_id = f"PAT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)