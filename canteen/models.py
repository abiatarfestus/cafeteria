from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
# from django_resized import ResizedImageField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_cellphone(value):
    """
    Validate whether the cellphone number is a valid MTC/TN number
    """
    # print(F"VALUE: {value}")
    if len(value)<10:
        raise ValidationError(
            _(f"Cellphone number must have 10 digits."),
            params={'value': value},
        )
    elif value[:3] not in ["081", "085"]:
        raise ValidationError(
            _(f"A valid cellphone number must start with '081' or '085'"),
            params={'value': value},
        )
    for digit in value:
        if digit not in "0123456789":
            raise ValidationError(
                _(f"Cellphone number must contain digits only."),
                params={'value': value},
            )

def minimum_qantity(value):
    """
    Validate that quantity of an order item is not < 1
    """
    # print(F"VALUE: {value}")
    if value < 1:
        raise ValidationError(
            _(f"You cannot add an item with 0 quantity."),
            params={'value': value},
        )

class Customer(models.Model):
    customer = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    cellphone = models.CharField(max_length=10, validators=[validate_cellphone])

    def __str__(self):
        return f"{self.customer.username}"

class Table(models.Model):
    table_number = models.IntegerField(unique=True, blank=False, null=False, default=0)
    max_seats = models.IntegerField(blank=False, null=False, default=0)
    description = models.CharField(blank=True, null=True, max_length=250)
    # empty_seats = models.IntegerField()

    def __str__(self):
        return f"{self.table_number}"

class Seat(models.Model):
    SEAT_STATUS = [
        ("OPEN", "Open"),
        ("PENDING", "Pending"),
        ("RESERVED", "Reserved"),
    ]
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    seat_number = models.IntegerField(unique=True, blank=False, null=False)
    status = models.CharField(max_length=8, choices=SEAT_STATUS, editable=False, default="OPEN")

    def clean(self):
        selected_table = Table.objects.get(id=self.table.id)
        number_of_seats = Seat.objects.filter(table=self.table.id).count()
        print(f"SELECTED_TABLE: {selected_table}")
        print(f"MAX_SEATS: {selected_table.max_seats}")
        print(f"NUMBER_OF_SEATS: {number_of_seats}")
        if not self.id:
            if number_of_seats >= selected_table.max_seats:
                raise ValidationError({"table": _(f"Table {selected_table.table_number} has reached maximum seats.")})

    def __str__(self):
        return f"{self.seat_number}"

class Reservation(models.Model):
    RESERVATION_STATUS = [
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("DECLINED", "Declined"),
        ("EXPIRED", "Expired"),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    status = models.CharField(max_length=8, choices=RESERVATION_STATUS, default="PENDING")
    time_reserved = models.DateTimeField(auto_now_add=True)


    def clean(self):
        selected_seat = Seat.objects.get(id=self.seat.id)
        print(f"SELECTED_SEAT: {selected_seat}")
        active_reservations = Reservation.objects.filter(Q(status="PENDING") | Q(status="ACCEPTED")).select_related("customer")
        print(f"ACTIVE RESERVATIONS: {active_reservations}")
        reservists = [reservation.customer for reservation in active_reservations]
        active_reservation_ids = [reservation.id for reservation in active_reservations]
        print(f"RESERVISTS: {reservists}")
        if selected_seat.status in ["PENDING", "RESERVED"]:
            if not self.id: # New record
                raise ValidationError({"seat": _("The selected seat is already reserved.")})  # The seat you want is already reserved || remove this by showing open seats only
            else:
                if self.id not in active_reservation_ids and self.status in ["PENDING", "ACCEPTED"]:
                    raise ValidationError({"seat": _("The selected seat is already reserved.")})
        if self.customer in reservists:
            if not self.id: # New record
                raise ValidationError({"customer": _("The customer already has an active reservation.")}) # You already have a pending resevation || remove this by disabling reservation when already waiting
            else:
                if self.id not in active_reservation_ids and self.status in ["PENDING", "ACCEPTED"]:
                    raise ValidationError({"customer": _("The customer already has an active reservation.")})
        

    def __str__(self):
        return f"{self.id}"


class Product(models.Model):
    PRODUCT_TYPES = [
        ("FOOD", "Food"),
        ("DRINK", "Drink"),
        ("OTHER", "Other"),
    ]
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    product_type = models.CharField(max_length=5, choices=PRODUCT_TYPES)
    price = models.FloatField()
    # image = models.ImageField(
    #     default="product_pics/placeholder.png", upload_to="product_pics"
    # )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "name",
                    "description",
                    "product_type"
                ],
                name="unique_products",
            )
        ]

    def __str__(self):
        return self.name

    # @property
    # def imageURL(self):
    #     try:
    #         url = self.image.url
    #     except:
    #         url = ""
    #     return url


class Order(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True
    )
    date_ordered = models.DateTimeField(auto_now_add=True)
    delivery = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)
    # transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.id)

    def clean(self):
        if not self.id:
            active_orders = Order.objects.filter(complete=False)
            print(f"ACTIVE ORDERS: {active_orders}")
            active_orderers = [order.customer for order in active_orders]
            print(f"ORDERERS: {active_orderers}")
            print(f"THIS ORDERER: {self.customer}")
            if self.customer in active_orderers:
                raise ValidationError({"customer": _("This customer already has an open order.")})

    @property
    def get_order_total(self):
        order_items = self.order_items
        total = sum([item.get_total for item in order_items])
        return total

    @property
    def get_order_items(self):
        order_items = self.order_items
        total = sum([item.quantity for item in order_items])
        return total


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, related_name="order_items")
    quantity = models.IntegerField(validators=[minimum_qantity], default=1, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "product",
                    "order",
                ],
                name="unique_order_items",
            )
        ]

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


class DeliveryAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
