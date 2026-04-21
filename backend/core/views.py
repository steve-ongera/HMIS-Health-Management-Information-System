from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from datetime import date, timedelta

from .models import (
    Patient, Department, Doctor,
    Appointment, MedicalRecord,
    Prescription, Invoice, InvoiceItem
)
from .serializers import (
    PatientListSerializer, PatientDetailSerializer,
    DepartmentSerializer, DoctorListSerializer, DoctorDetailSerializer,
    AppointmentListSerializer, AppointmentDetailSerializer,
    MedicalRecordListSerializer, MedicalRecordDetailSerializer,
    PrescriptionListSerializer, PrescriptionDetailSerializer,
    InvoiceListSerializer, InvoiceDetailSerializer, InvoiceItemSerializer,
)


# ─── PATIENT ─────────────────────────────────────────────────────────────────

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'gender', 'blood_type']
    search_fields = ['first_name', 'last_name', 'patient_id', 'phone_number', 'national_id', 'nhif_number']
    ordering_fields = ['last_name', 'registered_at', 'date_of_birth']
    ordering = ['-registered_at']

    def get_serializer_class(self):
        if self.action in ['list']:
            return PatientListSerializer
        return PatientDetailSerializer

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Return a patient's full medical history."""
        patient = self.get_object()
        records = patient.medical_records.order_by('-record_date')
        serializer = MedicalRecordListSerializer(records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def appointments(self, request, pk=None):
        patient = self.get_object()
        appointments = patient.appointments.order_by('-appointment_date')
        serializer = AppointmentListSerializer(appointments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def prescriptions(self, request, pk=None):
        patient = self.get_object()
        prescriptions = patient.prescriptions.filter(status='active')
        serializer = PrescriptionListSerializer(prescriptions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def invoices(self, request, pk=None):
        patient = self.get_object()
        invoices = patient.invoices.order_by('-invoice_date')
        serializer = InvoiceListSerializer(invoices, many=True)
        return Response(serializer.data)


# ─── DEPARTMENT & DOCTOR ─────────────────────────────────────────────────────

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.select_related('user', 'department').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialisation', 'status', 'department']
    search_fields = ['user__first_name', 'user__last_name', 'staff_id', 'license_number']
    ordering_fields = ['user__last_name', 'specialisation']

    def get_serializer_class(self):
        if self.action == 'list':
            return DoctorListSerializer
        return DoctorDetailSerializer

    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        """Return today's and upcoming appointments for a doctor."""
        doctor = self.get_object()
        today = date.today()
        appointments = doctor.appointments.filter(
            appointment_date__gte=today,
            status__in=['scheduled', 'confirmed']
        ).order_by('appointment_date', 'appointment_time')
        serializer = AppointmentListSerializer(appointments, many=True)
        return Response(serializer.data)


# ─── APPOINTMENT ─────────────────────────────────────────────────────────────

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.select_related('patient', 'doctor__user').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'appointment_type', 'priority', 'doctor', 'appointment_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'appointment_id', 'reason']
    ordering_fields = ['appointment_date', 'appointment_time', 'priority']
    ordering = ['-appointment_date', 'appointment_time']

    def get_serializer_class(self):
        if self.action == 'list':
            return AppointmentListSerializer
        return AppointmentDetailSerializer

    @action(detail=False, methods=['get'])
    def today(self, request):
        """All appointments for today."""
        today_appts = self.queryset.filter(appointment_date=date.today())
        serializer = AppointmentListSerializer(today_appts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        appointment = self.get_object()
        new_status = request.data.get('status')
        allowed = [s[0] for s in Appointment.STATUS_CHOICES]
        if new_status not in allowed:
            return Response({'error': f'Invalid status. Choose from: {allowed}'}, status=400)
        appointment.status = new_status
        appointment.save()
        return Response(AppointmentDetailSerializer(appointment).data)


# ─── MEDICAL RECORD ──────────────────────────────────────────────────────────

class MedicalRecordViewSet(viewsets.ModelViewSet):
    queryset = MedicalRecord.objects.select_related('patient', 'doctor__user').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['doctor', 'patient']
    search_fields = ['patient__first_name', 'patient__last_name', 'diagnosis', 'icd10_code', 'chief_complaint']
    ordering_fields = ['record_date', 'created_at']
    ordering = ['-record_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return MedicalRecordListSerializer
        return MedicalRecordDetailSerializer


# ─── PRESCRIPTION ─────────────────────────────────────────────────────────────

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.select_related('patient', 'doctor__user').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'patient', 'doctor', 'route']
    search_fields = ['medication_name', 'generic_name', 'prescription_id', 'patient__first_name', 'patient__last_name']
    ordering_fields = ['created_at', 'start_date']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return PrescriptionListSerializer
        return PrescriptionDetailSerializer

    @action(detail=False, methods=['get'])
    def active(self, request):
        """All currently active prescriptions."""
        active_rx = self.queryset.filter(status='active')
        serializer = PrescriptionListSerializer(active_rx, many=True)
        return Response(serializer.data)


# ─── BILLING ─────────────────────────────────────────────────────────────────

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related('patient').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['payment_status', 'patient', 'payment_method']
    search_fields = ['invoice_number', 'patient__first_name', 'patient__last_name', 'mpesa_transaction_id']
    ordering_fields = ['invoice_date', 'total_amount', 'due_date']
    ordering = ['-invoice_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return InvoiceListSerializer
        return InvoiceDetailSerializer

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """Add a line item to an invoice."""
        invoice = self.get_object()
        serializer = InvoiceItemSerializer(data={**request.data, 'invoice': invoice.pk})
        if serializer.is_valid():
            item = serializer.save()
            # Recalculate subtotal
            invoice.subtotal = sum(i.total_price for i in invoice.items.all())
            invoice.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def record_payment(self, request, pk=None):
        """Record a payment against an invoice."""
        invoice = self.get_object()
        amount = request.data.get('amount')
        method = request.data.get('payment_method', '')
        mpesa_id = request.data.get('mpesa_transaction_id', '')
        if not amount:
            return Response({'error': 'amount is required'}, status=400)
        invoice.amount_paid = float(invoice.amount_paid) + float(amount)
        if method:
            invoice.payment_method = method
        if mpesa_id:
            invoice.mpesa_transaction_id = mpesa_id
        invoice.save()
        return Response(InvoiceDetailSerializer(invoice).data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        today = date.today()
        overdue = self.queryset.filter(
            due_date__lt=today,
            payment_status__in=['pending', 'partial']
        )
        serializer = InvoiceListSerializer(overdue, many=True)
        return Response(serializer.data)


# ─── DASHBOARD ───────────────────────────────────────────────────────────────

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        today = date.today()
        this_month_start = today.replace(day=1)

        data = {
            'patients': {
                'total': Patient.objects.count(),
                'active': Patient.objects.filter(status='active').count(),
                'registered_this_month': Patient.objects.filter(registered_at__date__gte=this_month_start).count(),
            },
            'appointments': {
                'today': Appointment.objects.filter(appointment_date=today).count(),
                'this_week': Appointment.objects.filter(
                    appointment_date__range=[today, today + timedelta(days=7)]
                ).count(),
                'pending': Appointment.objects.filter(status__in=['scheduled', 'confirmed']).count(),
            },
            'billing': {
                'pending_invoices': Invoice.objects.filter(payment_status='pending').count(),
                'overdue_invoices': Invoice.objects.filter(
                    payment_status__in=['pending', 'partial'],
                    due_date__lt=today
                ).count(),
            },
            'doctors': {
                'total': Doctor.objects.count(),
                'active': Doctor.objects.filter(status='active').count(),
            },
        }
        return Response(data)