from django.contrib import admin

from .models import *
    

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("user", "id")
    ordering = ("user",)
    search_fields = (
        "user__last_name",
        "user__first_name",
    )

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    pass

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    pass

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    date_hierarchy = "time_reserved"
    list_display = ("id", "customer", "seat", "status", "time_reserved")
    list_filter = ("status",)
    ordering = ("id",)
    # raw_id_fields = ("english_word",)
    search_fields = (
        "customer__username",
    )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass
