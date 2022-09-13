from django.db import models
from django.contrib.auth.models import User
# from django_resized import ResizedImageField

# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        if len(self.user.first_name) == 0 or len(self.user.last_name) == 0:
            return self.user.username
        else:
            return f"{self.user.first_name} {self.user.last_name}"

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

    def __str__(self):
        return f"{self.seat_number}"

class Reservation(models.Model):
    RESERVATION_STATUS = [
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("DECLINED", "Declined"),
    ]
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    status = models.CharField(max_length=8, choices=RESERVATION_STATUS, default="PENDING")

    def __str__(self):
        return f"{self.id}"


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    price = models.FloatField()
    # image = models.ImageField(
    #     default="product_pics/placeholder.png", upload_to="product_pics"
    # )

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
