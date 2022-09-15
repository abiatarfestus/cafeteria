from django.db.models.signals import (
    post_save,
)  # Import a post_save signal when a user is created
from django.contrib.auth.models import (
    User,
)  # Import the built-in User model, which is a sender
from django.dispatch import receiver  # Import the receiver
from .models import Customer, Reservation, Seat


# @receiver(post_save, sender=User)
# def create_customer(sender, instance, created, **kwargs):
#     if created:
#         Customer.objects.create(customer=instance)
#         # print("CUSTOMER CREATION SIGNAL EXECUTED")


# @receiver(post_save, sender=User)
# def save_customer(sender, instance, **kwargs):
#     try:
#         instance.customer.save()
#         # print("CUSTOMER SAVE SIGNAL EXECUTED")
#     except Exception as e:
#         print(e)

@receiver(post_save, sender=Reservation)
def update_seat_status(sender, instance, created, **kwargs):
    try:
        seat = Seat.objects.get(id=instance.seat)
        if instance.status == "PENDING":
            seat.update(status="PENDING")
            print(f"STATUS of Seat {seat.seat_number} {seat.status}")
        elif instance.status == "ACCEPTED":
            seat.update(status="RESERVED")
            print(f"STATUS of Seat {seat.seat_number} {seat.status}")
        else:
            seat.update(status="OPEN")
            print(f"STATUS of Seat {seat.seat_number} {seat.status}")
    except Exception as e:
        print(e)