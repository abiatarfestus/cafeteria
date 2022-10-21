import datetime
import json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView

from .forms import AddressUpdateForm, OrderUpdateForm, ReservationForm, ProfileUpdateForm
from .models import *
from .utils import cartData
from .forms import ContactForm
from users.models import Profile
from .constants import ADMIN_EMAILS
from .constants import STAFF_EMAILS
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string


def home(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    context = {"cartItems": cartItems}
    return render(request, "canteen/home.html", context)


# @login_required
def menu(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    context = {"cartItems": cartItems}
    return render(request, "canteen/menu.html", context)


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
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
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
                "profile_form": profile_form,
            }
            return render(request, "canteen/checkout.html", context)
    order_form = OrderUpdateForm(instance=order)
    address_form = AddressUpdateForm(instance=request.user.address)
    profile_form = ProfileUpdateForm(instance=request.user.profile)
    context = {
        "items": items,
        "order": order,
        "cartItems": cartItems,
        "order_form": order_form,
        "address_form": address_form,
        "profile_form": profile_form,
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
def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, submitted=False)
    # else:
    #     customer, order = guestOrder(request, data)

    total_cost = float(data["form"]["total_cost"])
    delivery = data["form"]["delivery"]
    payment_method = data["form"]["payment_method"]
    if "delivery_address" in data["form"]:
        address = data["form"]["delivery_address"]
    else:
        address = None
    if "reference" in data["form"]:
        reference = data["form"]["reference"]
    else:
        reference = None
    if "cellphone" in data["form"]:
        cellphone = data["form"]["cellphone"]
    else:
        cellphone = None
    order.transaction_id = transaction_id

    delivery_address, created = DeliveryAddress.objects.get_or_create(user=request.user)
    if address:
        delivery_address.address = address
        delivery_address.save()

    profile, created = Profile.objects.get_or_create(user=request.user)
    if cellphone:
        profile.cellphone = cellphone
        profile.save()

    if delivery:
        order.delivery = True
    if total_cost == order.get_cart_total:
        order.submitted = True
        order.status = "SUBMITTED"
    order.save()

    print(order.submitted)
    if order.submitted:
        try:
            print("Sending email...")
            username = request.user.username
            cellphone = request.user.profile.cellphone
            address = request.user.address.address
            order_items = OrderItem.objects.filter(order=order)
            subject = "Confirmation of Order"
            customer_message = render_to_string(
                "canteen/customer_order_confirmation.html",
                {
                    "cellphone": cellphone,
                    "user": username,
                    "address": address,
                    "order": order,
                    "order_items": order_items,
                    "total_cost": total_cost,
                },
            )
            # staff_message = render_to_string(
            #     "canteen/staff_order_confirmation.html",
            #     {
            #         "order": order,
            #         "order_items": order_items,
            #         "total_cost": total_cost,
            #         "cellphone": cellphone,
            #         "user": username,
            #         "address": address,
            #     },
            # )
            email_from = settings.DEFAULT_FROM_EMAIL
            recipient = [request.user.email]
            send_mail(subject, customer_message, email_from, recipient)
            # send_mail(subject, staff_message, email_from, STAFF_EMAILS)
        except Exception as e:
            print(e)

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
        context = super(ReservationCreateView, self).get_context_data(**kwargs)
        context["heading"] = "Reserve your seat in the Cafeteria"
        context["active_reservists"] = self.get_active_reservists()
        context["open_seats"] = self.num_of_open_seats()
        data = cartData(self.request)
        cartItems = data["cartItems"]
        context["cartItems"] = cartItems
        return context

    def get_initial(self):
        return {"customer": self.request.user.customer}


# List View
# Templates for displaying List and Detail views
reservation_list = "canteen/reservation_list.html"
reservation_details = "canteen/reservation_details.html"


class ReservationListView(LoginRequiredMixin, generic.ListView):
    paginate_by = 10
    model = Reservation
    template_name = reservation_list

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

def contact(request):
    if request.method == "GET":
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data["subject"]
            from_email = form.cleaned_data["from_email"]
            message = form.cleaned_data['message']
            try:
                send_mail(subject, message, from_email, ADMIN_EMAILS)
            except BadHeaderError:
                return HttpResponse("Invalid header found.")
            messages.success(request, ("Message sent successfully. Thank you for engaging us!"))
            return redirect("home")
    
    data = cartData(request)
    cartItems = data["cartItems"]
    context = {"cartItems": cartItems, "form": form}
    return render(request, "canteen/contact.html", context)

def help(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    context = {"cartItems": cartItems}
    return render(request, "canteen/help.html", context)