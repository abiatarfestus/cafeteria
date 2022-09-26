import json
import datetime
from .models import *
from django.views import generic
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from django.views.generic.edit import CreateView
from .forms import OrderUpdateForm, AddressUpdateForm, ReservationForm
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .utils import cookieCart, cartData, guestOrder

def home(request):
    return render(request, "canteen/home.html",{})


def canteen(request):
    data = cartData(request)

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    products = Product.objects.all()
    context = {"products": products, "cartItems": cartItems}
    return render(request, "canteen/canteen.html", context)


def cart(request):
    data = cartData(request)

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "canteen/cart.html", context)


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
            messages.warning(request, "Delivery infomation not updated! Please correct the errors shown below.")
            context = {"items": items, "order": order, "cartItems": cartItems, "user_form": order_form, "address_form": address_form}
            return render(request, "canteen/checkout.html", context)
    order_form = OrderUpdateForm(instance=order)
    address_form = AddressUpdateForm(instance=request.user.address)
    context = {"items": items, "order": order, "cartItems": cartItems, "order_form": order_form, "address_form": address_form}
    return render(request, "canteen/checkout.html", context)


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


class ReservationCreateView(
    LoginRequiredMixin, SuccessMessageMixin, CreateView
):
    form_class = ReservationForm
    model = Reservation
    extra_context = {
        "operation": "Reserve your seat in the Cafeteria",
    }
    success_message = f"Reservation of Seat __ was successfully submitted!"

    def form_valid(self, form):
        form.instance.customer = self.request.user.customer
        return super().form_valid(form)

# List View
# Templates for displaying List and Detail views
list_view = "canteen/list_view.html"
detail_view = "canteen/detail_view.html"

class ReservationListView(generic.ListView):
    paginate_by = 10
    model = Reservation
    template_name = list_view

    def get_queryset(self):
        return Reservation.objects.filter(Q(status="PENDING") | Q(status="ACCEPTED")).order_by("customer")

    def get_context_data(self, **kwargs):
        context = super(ReservationListView, self).get_context_data(**kwargs)
        context["heading"] = "List of Active Reservations"
        return context