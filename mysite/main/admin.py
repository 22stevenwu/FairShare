from django.contrib import admin
from .models import Bill, BillSplit

class BillAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_amount', 'tip_percentage', 'tax_amount', 'created_by', 'created_at')

class BillSplitAdmin(admin.ModelAdmin):
    list_display = ('bill', 'participant_name', 'amount_spent', 'amount_owed')

admin.site.register(Bill, BillAdmin)
admin.site.register(BillSplit, BillSplitAdmin)