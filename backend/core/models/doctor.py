from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Doctor(models.Model):
    SPECIALISATION_CHOICES = [
        ('general', 'General Practice'),
        ('pediatrics', 'Pediatrics'),
        ('gynecology', 'Gynecology & Obstetrics'),
        ('surgery', 'Surgery'),
        ('internal_medicine', 'Internal Medicine'),
        ('cardiology', 'Cardiology'),
        ('orthopedics', 'Orthopedics'),
        ('dermatology', 'Dermatology'),
        ('psychiatry', 'Psychiatry'),
        ('ophthalmology', 'Ophthalmology'),
        ('ent', 'ENT'),
        ('radiology', 'Radiology'),
        ('pathology', 'Pathology'),
        ('anesthesiology', 'Anesthesiology'),
        ('emergency', 'Emergency Medicine'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('inactive', 'Inactive'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    staff_id = models.CharField(max_length=20, unique=True, editable=False)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='doctors')
    specialisation = models.CharField(max_length=50, choices=SPECIALISATION_CHOICES, default='general')
    license_number = models.CharField(max_length=50, unique=True)
    qualification = models.CharField(max_length=500, help_text='e.g. MBChB, MMed Surgery')
    phone_number = models.CharField(max_length=15)
    profile_photo = models.ImageField(upload_to='doctors/photos/', blank=True, null=True)
    bio = models.TextField(blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__last_name']

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} ({self.get_specialisation_display()})"

    def get_full_name(self):
        return f"Dr. {self.user.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.staff_id:
            import uuid
            self.staff_id = f"DOC-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)