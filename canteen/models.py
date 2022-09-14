from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
# from django_resized import ResizedImageField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _




class Customer(models.Model):
    customer = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)

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
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    seat_number = models.IntegerField(unique=True, blank=False, null=False)
    reserved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        selected_table = Table.objects.get(id=self.table.id)
        number_of_seats = Seat.objects.filter(table=self.table.id).count()
        print(f"SELECTED_TABLE: {selected_table}")
        print(f"NUMBER_OF_SEATS: {number_of_seats}")
        if number_of_seats >= selected_table.max_seats:
            return  # The table has reached maximum seats
        super(Seat, self).save(*args, **kwargs)

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
        print(f"RESERVISTS: {reservists}")
        if selected_seat.reserved:
            raise ValidationError({"seat": _("The selected seat is already reserved.")})  # The seat you want is already reserved || remove this by showing open seats only
        elif self.customer in reservists:
            raise ValidationError({"seat": _("The customer already has an active reservation.")}) # You already have a pending resevation || remove this by disabling reservation when already waiting

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
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.id)

    # @property
    # def shipping(self):
    #     shipping = False
    #     orderitems = self.orderitem_set.all()
    #     for i in orderitems:
    #         if i.product.digital == False:
    #             shipping = True
    #     return shipping

    # @property
    # def get_cart_total(self):
    #     orderitems = self.orderitem_set.all()
    #     total = sum([item.get_total for item in orderitems])
    #     return total

    # @property
    # def get_cart_items(self):
    #     orderitems = self.orderitem_set.all()
    #     total = sum([item.quantity for item in orderitems])
        # return total


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total


# class ShippingAddress(models.Model):
#     customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
#     order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
#     address = models.CharField(max_length=200, null=False)
#     city = models.CharField(max_length=200, null=False)
#     state = models.CharField(max_length=200, null=False)
#     zipcode = models.CharField(max_length=200, null=False)
#     date_added = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.address
