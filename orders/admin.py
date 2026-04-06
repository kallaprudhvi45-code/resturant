from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone_number', 'total_amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('full_name', 'phone_number', 'address')
    inlines = [OrderItemInline]
