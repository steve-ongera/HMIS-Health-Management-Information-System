from django.contrib import admin
from .models import Patient, Department, Doctor, Appointment, MedicalRecord, Prescription, Invoice, InvoiceItem


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'get_full_name', 'gender', 'phone_number', 'blood_type', 'status', 'registered_at']
    list_filter = ['status', 'gender', 'blood_type']
    search_fields = ['first_name', 'last_name', 'patient_id', 'phone_number', 'national_id']
    readonly_fields = ['patient_id', 'registered_at', 'updated_at']
    ordering = ['-registered_at']

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['staff_id', 'get_full_name', 'specialisation', 'department', 'status']
    list_filter = ['specialisation', 'status', 'department']
    search_fields = ['user__first_name', 'user__last_name', 'staff_id', 'license_number']
    readonly_fields = ['staff_id', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Name'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['appointment_id', 'patient', 'doctor', 'appointment_date', 'appointment_time', 'status', 'priority']
    list_filter = ['status', 'appointment_type', 'priority', 'appointment_date']
    search_fields = ['appointment_id', 'patient__first_name', 'patient__last_name']
    readonly_fields = ['appointment_id', 'created_at', 'updated_at']
    date_hierarchy = 'appointment_date'


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'doctor', 'record_date', 'diagnosis', 'icd10_code']
    list_filter = ['record_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'diagnosis', 'icd10_code']
    readonly_fields = ['record_date', 'created_at', 'updated_at']
    date_hierarchy = 'record_date'


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['prescription_id', 'patient', 'medication_name', 'dosage', 'frequency', 'status', 'start_date']
    list_filter = ['status', 'route', 'frequency']
    search_fields = ['prescription_id', 'patient__first_name', 'patient__last_name', 'medication_name']
    readonly_fields = ['prescription_id', 'created_at', 'updated_at']


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    readonly_fields = ['total_price']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'patient', 'invoice_date', 'total_amount', 'amount_paid', 'payment_status']
    list_filter = ['payment_status', 'payment_method', 'invoice_date']
    search_fields = ['invoice_number', 'patient__first_name', 'patient__last_name', 'mpesa_transaction_id']
    readonly_fields = ['invoice_number', 'total_amount', 'invoice_date', 'created_at', 'updated_at']
    inlines = [InvoiceItemInline]
    date_hierarchy = 'invoice_date'