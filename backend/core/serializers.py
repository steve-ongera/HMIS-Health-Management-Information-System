from django.contrib.auth.models import User
from rest_framework import serializers
from .models import (
    Patient, Department, Doctor,
    Appointment, MedicalRecord,
    Prescription, Invoice, InvoiceItem
)


# ─── AUTH ────────────────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


# ─── PATIENT ─────────────────────────────────────────────────────────────────

class PatientListSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            'id', 'patient_id', 'full_name', 'first_name', 'last_name',
            'date_of_birth', 'age', 'gender', 'phone_number',
            'blood_type', 'status', 'registered_at',
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()


class PatientDetailSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['patient_id', 'registered_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.get_full_name()


# ─── DEPARTMENT & DOCTOR ─────────────────────────────────────────────────────

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class DoctorListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    specialisation_display = serializers.CharField(source='get_specialisation_display', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Doctor
        fields = [
            'id', 'staff_id', 'full_name', 'specialisation',
            'specialisation_display', 'department_name',
            'phone_number', 'consultation_fee', 'status',
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()


class DoctorDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source='department', write_only=True
    )
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = '__all__'
        read_only_fields = ['staff_id', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.get_full_name()


# ─── APPOINTMENT ─────────────────────────────────────────────────────────────

class AppointmentListSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    patient_id_code = serializers.CharField(source='patient.patient_id', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_appointment_type_display', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'appointment_id', 'patient', 'patient_name', 'patient_id_code',
            'doctor', 'doctor_name', 'appointment_date', 'appointment_time',
            'duration_minutes', 'appointment_type', 'type_display',
            'priority', 'status', 'status_display', 'reason',
        ]


class AppointmentDetailSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['appointment_id', 'created_at', 'updated_at']

    def validate(self, data):
        # Ensure appointment date is not in the past on creation
        from datetime import date
        if self.instance is None and data.get('appointment_date') < date.today():
            raise serializers.ValidationError({'appointment_date': 'Appointment date cannot be in the past.'})
        return data


# ─── MEDICAL RECORD ──────────────────────────────────────────────────────────

class MedicalRecordListSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    bmi = serializers.ReadOnlyField()
    blood_pressure = serializers.ReadOnlyField()

    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'record_date', 'chief_complaint', 'diagnosis',
            'icd10_code', 'bmi', 'blood_pressure', 'created_at',
        ]


class MedicalRecordDetailSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    bmi = serializers.ReadOnlyField()
    blood_pressure = serializers.ReadOnlyField()

    class Meta:
        model = MedicalRecord
        fields = '__all__'
        read_only_fields = ['record_date', 'created_at', 'updated_at']


# ─── PRESCRIPTION ─────────────────────────────────────────────────────────────

class PrescriptionListSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    route_display = serializers.CharField(source='get_route_display', read_only=True)

    class Meta:
        model = Prescription
        fields = [
            'id', 'prescription_id', 'patient', 'patient_name',
            'doctor', 'doctor_name', 'medication_name', 'dosage',
            'frequency', 'frequency_display', 'route', 'route_display',
            'duration_days', 'status', 'start_date', 'end_date',
        ]


class PrescriptionDetailSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)

    class Meta:
        model = Prescription
        fields = '__all__'
        read_only_fields = ['prescription_id', 'created_at', 'updated_at']


# ─── BILLING ─────────────────────────────────────────────────────────────────

class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = '__all__'
        read_only_fields = ['total_price']


class InvoiceListSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    balance_due = serializers.ReadOnlyField()
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'patient', 'patient_name',
            'invoice_date', 'due_date', 'total_amount', 'amount_paid',
            'balance_due', 'payment_status', 'payment_status_display',
        ]


class InvoiceDetailSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    balance_due = serializers.ReadOnlyField()

    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['invoice_number', 'total_amount', 'invoice_date', 'created_at', 'updated_at']