from django.urls import path

from . import views
from django.views.generic import TemplateView

app_name = "canteen"
urlpatterns = [
    path("cart/", views.cart, name="cart"),
    path("menu/", views.menu, name="menu"),
    path("contact/", views.contact, name="contact"),
    path("sub_menu/<str:menu_type>/", views.sub_menu, name="sub_menu"),
    path("checkout/", views.checkout, name="checkout"),
    path("update_item/", views.updateItem, name="update_item"),
    path("process_order/", views.processOrder, name="process_order"),
    path("reservations/", views.ReservationListView.as_view(), name="reservations"),
    path("reserve_seat/", views.ReservationCreateView.as_view(), name="reserve_seat"),
    path(
        "update_reservation/<int:pk>/<str:type>",
        views.update_reservation,
        name="update_reservation",
    ),
    path("help/", TemplateView.as_view(template_name="canteen/help.html"), name="help"),
]
