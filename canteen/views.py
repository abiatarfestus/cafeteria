import datetime
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView

from .forms import AddressUpdateForm, OrderUpdateForm, ReservationForm
from .models import *
from .utils import cartData


def home(request):
    return render(request, "canteen/home.html", {})


# @login_required
def menu(request):
    return render(request, "canteen/menu.html")


@login_required
def sub_menu(request, menu_type):
    data = cartData(request)

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    products = Product.objects.all()
    context = {"products": products, "cartItems": cartItems, "menu_type":menu_type}
    return render(request, "canteen/sub_menu.html", context)


@login_required
def cart(request):
    data = cartData(request)

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "canteen/cart.html", context)


@login_required
def checkout(request):
    data = cartData(request)

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]
    if request.method == "POST":
        order_form = OrderUpdateForm(request.POST, instance=order)
        address_form = AddressUpdateForm(request.POST, instance=request.user.address)
        if order_form.is_valid() and address_form.is_valid:
            order_form.save()
            address_form.save()
            # messages.success(request, "Delivery infomation updated!")
            return render(request, "canteen/process_order.html", context)
        else:
            messages.warning(
                request,
                "Delivery infomation not updated! Please correct the errors shown below.",
            )
            context = {
                "items": items,
                "order": order,
                "cartItems": cartItems,
                "user_form": order_form,
                "address_form": address_form,
            }
            return render(request, "canteen/checkout.html", context)
    order_form = OrderUpdateForm(instance=order)
    address_form = AddressUpdateForm(instance=request.user.address)
    context = {
        "items": items,
        "order": order,
        "cartItems": cartItems,
        "order_form": order_form,
        "address_form": address_form,
    }
    return render(request, "canteen/checkout.html", context)


@login_required
def updateItem(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]
    print("Action:", action)
    print("Product:", productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, submitted=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == "add":
        orderItem.quantity = orderItem.quantity + 1
    elif action == "remove":
        orderItem.quantity = orderItem.quantity - 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item was added", safe=False)


@login_required
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, submitted=False)
    # else:
    #     customer, order = guestOrder(request, data)

    total = float(data["form"]["total"])
    delivery = data["form"]["delivery"]
    address = data["address"]["address"]
    order.transaction_id = transaction_id

    delivery_address, created = DeliveryAddress.objects.get_or_create(user=request.user)
    delivery_address.address = address
    delivery_address.save()

    if delivery:
        order.delivery = True
    if total == order.get_cart_total:
        order.submitted = True
        order.status = "SUBMITTED"
    order.save()

    return JsonResponse("Payment submitted..", safe=False)


class ReservationCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    form_class = ReservationForm
    model = Reservation
    success_message = f"Reservation of Seat __ was successfully submitted!"
    success_url = reverse_lazy("canteen:reservations")
    success_message = "Your reservation was sent successfully! You will receive a notification once your reservation is processed."

    def get_active_reservists(self):
        active_reservations = Reservation.objects.filter(
            Q(status="PENDING") | Q(status="ACCEPTED")
        ).select_related("customer")
        active_reservists = [
            reservation.customer for reservation in active_reservations
        ]
        # active_reservation_ids = [reservation.id for reservation in active_reservations]
        return active_reservists

    def num_of_open_seats(self):
        return Seat.objects.filter(status="OPEN").count()

    def get_context_data(self, **kwargs):
        data = cartData(self.request)
        cartItems = data["cartItems"]
        context = super(ReservationCreateView, self).get_context_data(**kwargs)
        context["heading"] = "Reserve your seat in the Cafeteria"
        context["active_reservists"] = self.get_active_reservists()
        context["open_seats"] = self.num_of_open_seats()
        context["cartItems"] = cartItems
        return context

    def get_initial(self):
        return {"customer": self.request.user.customer}


# List View
# Templates for displaying List and Detail views
list_view = "canteen/list_view.html"
detail_view = "canteen/detail_view.html"


class ReservationListView(LoginRequiredMixin, generic.ListView):
    paginate_by = 10
    model = Reservation
    template_name = list_view

    def get_queryset(self):
        return Reservation.objects.filter(
            Q(status="PENDING") | Q(status="ACCEPTED")
        ).order_by("customer")

    def num_of_open_seats(self):
        return Seat.objects.filter(status="OPEN").count()

    def get_context_data(self, **kwargs):
        data = cartData(self.request)
        cartItems = data["cartItems"]
        context = super(ReservationListView, self).get_context_data(**kwargs)
        context["heading"] = "List of Active Reservations"
        context["open_seats"] = self.num_of_open_seats()
        context["cartItems"] = cartItems
        return context


def update_reservation(request, pk, type):
    reservation = Reservation.objects.get(pk=pk)
    if type == "accept":
        reservation.status = "ACCEPTED"
    elif type == "decline":
        reservation.status = "DECLINED"
    else:
        reservation.status = "EXPIRED"
    reservation.save()
    messages.success(request, ("Reservation status successfully updated."))
    return redirect("canteen:reservations")
