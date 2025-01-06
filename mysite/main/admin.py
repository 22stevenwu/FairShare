from django.contrib import admin
from .models import Bill

# Register the Bill model with the admin site
class BillAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_amount', 'tip_percentage', 'created_by', 'created_at')  # Columns to display in the list view
    search_fields = ('name', 'created_by__username')  # Allow searching by bill name and username of the creator
    list_filter = ('created_at',)  # Filter bills by creation date

admin.site.register(Bill, BillAdmin)  # Register the model with the custom admin class