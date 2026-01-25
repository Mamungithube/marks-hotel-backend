# # finance_accounting/views.py
# # ==========================================

# from rest_framework import viewsets, status, filters
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from django_filters.rest_framework import DjangoFilterBackend
# from django.utils import timezone
# from django.db.models import Sum, Count, Avg
# from decimal import Decimal
# from datetime import datetime, timedelta
# from finance_accounting.models import Invoice, Expense, Revenue, FinancialReport
# from finance_accounting.serializers import (
#     InvoiceSerializer, InvoiceCreateSerializer,
#     ExpenseSerializer, ExpenseCreateSerializer,
#     RevenueSerializer, FinancialReportSerializer,
#     FinancialReportCreateSerializer
# )
# from core.permissions import IsFinanceUser


# class InvoiceViewSet(viewsets.ModelViewSet):
#     """Invoice CRUD (Finance/Admin Only)"""
#     permission_classes = [IsFinanceUser]
#     filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
#     filterset_fields = ['status', 'issue_date', 'due_date']
#     ordering_fields = ['issue_date', 'due_date', 'total_amount']
    
#     def get_queryset(self):
#         return Invoice.objects.filter(is_active=True).select_related(
#             'booking', 'booking__user', 'created_by'
#         ).prefetch_related('items')
    
#     def get_serializer_class(self):
#         if self.action == 'create':
#             return InvoiceCreateSerializer
#         return InvoiceSerializer
    
#     @action(detail=True, methods=['post'])
#     def send_invoice(self, request, pk=None):
#         """Send invoice to customer"""
#         invoice = self.get_object()
        
#         if invoice.status == 'draft':
#             invoice.status = 'sent'
#             invoice.save()
        
#         # TODO: Send email with invoice PDF
        
#         return Response({'message': 'Invoice sent to customer'})
    
#     @action(detail=True, methods=['post'])
#     def mark_paid(self, request, pk=None):
#         """Mark invoice as paid"""
#         invoice = self.get_object()
#         invoice.status = 'paid'
#         invoice.paid_amount = invoice.total_amount
#         invoice.save()
        
#         return Response({'message': 'Invoice marked as paid'})


# class ExpenseViewSet(viewsets.ModelViewSet):
#     """Expense CRUD (Finance/Admin Only)"""
#     permission_classes = [IsFinanceUser]
#     filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
#     filterset_fields = ['category', 'payment_status', 'is_approved', 'expense_date']
#     ordering_fields = ['expense_date', 'amount', 'created_at']
    
#     def get_queryset(self):
#         return Expense.objects.filter(is_active=True).select_related(
#             'related_employee', 'related_maintenance', 'recorded_by', 'approved_by'
#         )
    
#     def get_serializer_class(self):
#         if self.action == 'create':
#             return ExpenseCreateSerializer
#         return ExpenseSerializer
    
#     @action(detail=True, methods=['post'])
#     def approve(self, request, pk=None):
#         """Approve expense"""
#         expense = self.get_object()
#         expense.is_approved = True
#         expense.approved_by = request.user
#         expense.save()
        
#         return Response({'message': 'Expense approved'})
    
#     @action(detail=False, methods=['get'])
#     def summary(self, request):
#         """Expense summary by category"""
#         from django.db.models import Sum
        
#         start_date = request.query_params.get('start_date')
#         end_date = request.query_params.get('end_date')
        
#         queryset = self.get_queryset()
        
#         if start_date and end_date:
#             queryset = queryset.filter(
#                 expense_date__gte=start_date,
#                 expense_date__lte=end_date
#             )
        
#         summary = queryset.filter(is_approved=True).values('category').annotate(
#             total=Sum('amount'),
#             count=Count('id')
#         ).order_by('-total')
        
#         total_expenses = sum(item['total'] for item in summary)
        
#         return Response({
#             'summary': summary,
#             'total_expenses': total_expenses,
#             'period': {
#                 'start_date': start_date,
#                 'end_date': end_date
#             }
#         })


# class RevenueViewSet(viewsets.ReadOnlyModelViewSet):
#     """Revenue View (Finance/Admin Only)"""
#     serializer_class = RevenueSerializer
#     permission_classes = [IsFinanceUser]
#     filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
#     filterset_fields = ['source', 'revenue_date']
#     ordering_fields = ['revenue_date', 'amount']
    
#     def get_queryset(self):
#         return Revenue.objects.filter(is_active=True).select_related(
#             'related_booking', 'related_payment'
#         )
    
#     @action(detail=False, methods=['get'])
#     def summary(self, request):
#         """Revenue summary by source"""
#         from django.db.models import Sum
        
#         start_date = request.query_params.get('start_date')
#         end_date = request.query_params.get('end_date')
        
#         queryset = self.get_queryset()
        
#         if start_date and end_date:
#             queryset = queryset.filter(
#                 revenue_date__gte=start_date,
#                 revenue_date__lte=end_date
#             )
        
#         summary = queryset.values('source').annotate(
#             total=Sum('amount'),
#             count=Count('id')
#         ).order_by('-total')
        
#         total_revenue = sum(item['total'] for item in summary)
        
#         return Response({
#             'summary': summary,
#             'total_revenue': total_revenue,
#             'period': {
#                 'start_date': start_date,
#                 'end_date': end_date
#             }
#         })


# class FinancialReportViewSet(viewsets.ModelViewSet):
#     """Financial Report CRUD (Finance/Admin Only)"""
#     permission_classes = [IsFinanceUser]
#     filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
#     filterset_fields = ['report_type', 'report_date']
#     ordering_fields = ['report_date', 'created_at']
    
#     def get_queryset(self):
#         return FinancialReport.objects.filter(is_active=True).select_related('generated_by')
    
#     def get_serializer_class(self):
#         if self.action == 'create':
#             return FinancialReportCreateSerializer
#         return FinancialReportSerializer
    
#     @action(detail=False, methods=['get'])
#     def dashboard(self, request):
#         """Finance Dashboard - Key Metrics"""
#         from booking_api.models import Booking, Payment
#         from room_management.models import Room
        
#         today = timezone.now().date()
#         this_month_start = today.replace(day=1)
        
#         # Today's revenue
#         today_revenue = Revenue.objects.filter(
#             revenue_date=today,
#             is_active=True
#         ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
#         # This month revenue
#         month_revenue = Revenue.objects.filter(
#             revenue_date__gte=this_month_start,
#             revenue_date__lte=today,
#             is_active=True
#         ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
#         # Pending payments
#         pending_payments = Booking.objects.filter(
#             payment_status__in=['pending', 'partial'],
#             is_active=True
#         ).aggregate(total=Sum('total_amount') - Sum('paid_amount'))['total'] or Decimal('0.00')
        
#         # Today's expenses
#         today_expenses = Expense.objects.filter(
#             expense_date=today,
#             is_approved=True,
#             is_active=True
#         ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
#         # This month expenses
#         month_expenses = Expense.objects.filter(
#             expense_date__gte=this_month_start,
#             expense_date__lte=today,
#             is_approved=True,
#             is_active=True
#         ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
#         # Net profit
#         net_profit_today = today_revenue - today_expenses
#         net_profit_month = month_revenue - month_expenses
        
#         # Occupancy rate
#         total_rooms = Room.objects.filter(is_active=True).count()
#         occupied_rooms = Room.objects.filter(
#             current_status='occupied',
#             is_active=True
#         ).count()
#         occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
        
#         # Bookings
#         today_bookings = Booking.objects.filter(
#             created_at__date=today,
#             is_active=True
#         ).count()
        
#         pending_checkouts = Booking.objects.filter(
#             check_out_date=today,
#             booking_status='checked_in',
#             is_active=True
#         ).count()
        
#         return Response({
#             'today': {
#                 'revenue': today_revenue,
#                 'expenses': today_expenses,
#                 'net_profit': net_profit_today,
#                 'bookings': today_bookings,
#                 'pending_checkouts': pending_checkouts
#             },
#             'this_month': {
#                 'revenue': month_revenue,
#                 'expenses': month_expenses,
#                 'net_profit': net_profit_month
#             },
#             'occupancy': {
#                 'rate': round(occupancy_rate, 2),
#                 'occupied_rooms': occupied_rooms,
#                 'total_rooms': total_rooms
#             },
#             'pending_payments': pending_payments
#         })