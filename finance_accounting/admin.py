from django.contrib import admin
from .models import Invoice,InvoiceItem,Expense,Revenue,FinancialReport

admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(Expense)
admin.site.register(Revenue)
admin.site.register(FinancialReport)