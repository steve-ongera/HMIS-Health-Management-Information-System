from django.db import models
from .patient import Patient
from .doctor import Doctor
from .appointment import Appointment


class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='medical_records')
    appointment = models.OneToOneField(
        Appointment, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='medical_record'
    )

    record_date = models.DateField(auto_now_add=True)

    # Vitals
    temperature = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True,
        help_text='Body temperature in °C'
    )
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True, help_text='mmHg')
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True, help_text='mmHg')
    pulse_rate = models.PositiveIntegerField(null=True, blank=True, help_text='Beats per minute')
    respiratory_rate = models.PositiveIntegerField(null=True, blank=True, help_text='Breaths per minute')
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='Weight in kg')
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='Height in cm')
    oxygen_saturation = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text='SpO2 %')

    # Clinical
    chief_complaint = models.TextField()
    history_of_present_illness = models.TextField(blank=True)
    physical_examination = models.TextField(blank=True)
    diagnosis = models.TextField()
    icd10_code = models.CharField(max_length=20, blank=True, verbose_name='ICD-10 Code')
    treatment_plan = models.TextField(blank=True)
    follow_up_instructions = models.TextField(blank=True)
    referral = models.TextField(blank=True, help_text='Referral to specialist if any')

    # Lab / Radiology
    lab_results = models.TextField(blank=True)
    radiology_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-record_date', '-created_at']

    def __str__(self):
        return f"Record [{self.pk}] — {self.patient.get_full_name()} on {self.record_date}"

    @property
    def bmi(self):
        if self.weight and self.height and self.height > 0:
            height_m = float(self.height) / 100
            return round(float(self.weight) / (height_m ** 2), 1)
        return None

    @property
    def blood_pressure(self):
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic} mmHg"
        return None