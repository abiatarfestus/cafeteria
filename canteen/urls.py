from django.urls import path

from . import views

app_name = "canteen"
urlpatterns = [
    path("cart/", views.cart, name="cart"),
    path("canteen/", views.canteen, name="canteen"),
    path("checkout/", views.checkout, name="checkout"),
    path("update_item/", views.updateItem, name="update_item"),
    path("process_order/", views.processOrder, name="process_order"),
    path("reservations/", views.ReservationListView.as_view(), name="reservations"),
    path("reserve_seat/", views.ReservationCreateView.as_view(), name="reserve_seat"),
]