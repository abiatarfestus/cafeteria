from django.contrib import admin

from .models import *
    

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("customer", "id")
    ordering = ("customer",)
    search_fields = (
        "customer__last_name",
        "customer__first_name",
    )

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("table_number", "max_seats")
    ordering = ("table_number",)

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("seat_number", "table", "status")
    list_filter = ("status",)
    ordering = ("seat_number",)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    date_hierarchy = "time_reserved"
    list_display = ("id", "customer", "seat", "status", "time_reserved")
    list_filter = ("status",)
    ordering = ("id",)
    search_fields = (
        "customer__username",
    )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    date_hierarchy = "date_ordered"
    list_display = ("id", "customer", "delivery", "complete", "date_ordered")
    list_filter = ("delivery", "complete", "date_ordered",)
    ordering = ("customer",)
    search_fields = (
        "customer",
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    date_hierarchy = "date_added"
    list_display = ("id", "order", "product", "quantity")
    list_filter = ("order",)
    ordering = ("order",)
    search_fields = (
        "product",
    )
