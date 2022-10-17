from django.db.models.signals import (
    post_save,
)  # Import a post_save signal when a user is created
from django.contrib.auth.models import (
    User,
)  # Import the built-in User model, which is a sender

from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail
from django.dispatch import receiver  # Import the receiver
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site
from .models import Customer, DeliveryAddress, Reservation, Seat

#----CREATE AND UPDATE CUSTOMER----#
@receiver(post_save, sender=User)
def create_customer(sender, instance, created, **kwargs):
    if created:
        new_customer = Customer.objects.create(customer=instance)
        try:
            new_customer.save()
        except Exception as e:
            print(e)

#----CREATE AND UPDATE CUSTOMER DELIVERY ADDRESS----#
@receiver(post_save, sender=User)
def create_address(sender, instance, created, **kwargs):
    print("ENTERED CREATE ADDRESS")
    if created:
        new_address = DeliveryAddress.objects.create(user=instance)
        try:
            new_address.save()
        except Exception as e:
            print(e)

#----UPDATE SEAT STATUS----#
@receiver(post_save, sender=Reservation)
def update_seat_status(sender, instance, created, **kwargs):
    try:
        seat = Seat.objects.get(id=instance.seat_id)
        if instance.status == "PENDING":
            seat.status = "PENDING"
            seat.save()
            print(f"STATUS of Seat {seat.seat_number} was changed to {seat.status}")
        elif instance.status == "ACCEPTED":
            seat.status = "RESERVED"
            seat.save()
            print(f"STATUS of Seat {seat.seat_number} was changed to {seat.status}")
        else:
            seat.status = "OPEN"
            seat.save()
            print(f"STATUS of Seat {seat.seat_number} was changed to {seat.status}")
    except Exception as e:
        print(e)

#----SEND RESERVATION STATUS NOTIFICATION----#
@receiver(post_save, sender=Reservation)
def notify_customer(sender, instance, created, **kwargs):
    if not created:
        customer = Customer.objects.get(pk=instance.customer_id)
        try:
            if instance.status == "EXPIRED":
                return
            username = customer.customer.username
            subject = "Reservation Status Notification"
            domain = Site.objects.get_current().domain
            relative_path = reverse("canteen:reservations")
            message = render_to_string(
                "canteen/reservation_updated.html",
                {
                    "url": f"{domain}{relative_path}",
                    "user": username,
                    "status": instance.status
                },
            )
            email_from = settings.DEFAULT_FROM_EMAIL
            recepient = customer.customer.email
            recipient_list = [recepient]
            send_mail(subject, message, email_from, recipient_list)
        except Exception as e:
            print(e)