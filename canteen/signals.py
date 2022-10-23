from django.conf import settings
from django.contrib.auth.models import \
    User  # Import the built-in User model, which is a sender
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db.models.signals import \
    post_save  # Import a post_save signal when a user is created
from django.dispatch import receiver  # Import the receiver
from django.template.loader import render_to_string
from django.urls import reverse
from .constants import STAFF_EMAILS
from sms import send_sms

from .models import Customer, DeliveryAddress, Reservation, Seat


# ----CREATE AND UPDATE CUSTOMER----#
@receiver(post_save, sender=User)
def create_customer(sender, instance, created, **kwargs):
    if created:
        new_customer = Customer.objects.create(customer=instance)
        try:
            new_customer.save()
        except Exception as e:
            print(e)


# ----CREATE AND UPDATE CUSTOMER DELIVERY ADDRESS----#
@receiver(post_save, sender=User)
def create_address(sender, instance, created, **kwargs):
    print("ENTERED CREATE ADDRESS")
    if created:
        new_address = DeliveryAddress.objects.create(user=instance)
        try:
            new_address.save()
        except Exception as e:
            print(e)


# ----UPDATE SEAT STATUS----#
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


# ----SEND RESERVATION STATUS NOTIFICATION----#
@receiver(post_save, sender=Reservation)
def send_notifications(sender, instance, created, **kwargs):
    if created:
        customer = instance.customer
    else:
        customer = Customer.objects.get(pk=instance.customer_id)
    try:
        username = customer.customer.username
        customer_cellphone = customer.customer.profile.cellphone
        if customer_cellphone:
            customer_cellphone = "+264" + customer_cellphone[1:]
        subject = "Seat Reservation Notification"
        domain = Site.objects.get_current().domain
        relative_path = reverse("canteen:reservations")
        seat_number = instance.seat.seat_number
        customer_message = render_to_string(
            "canteen/reservation_notifications.html",
            {
                "url": f"{domain}{relative_path}",
                "user": username,
                "status": instance.status,
                "seat_number": seat_number,
            },
        )
        staff_message = render_to_string(
            "canteen/staff_notification.html",
            {
                "url": f"{domain}{relative_path}",
                "seat_number": seat_number
            },
        )
        email_from = settings.DEFAULT_FROM_EMAIL
        recipient = [customer.customer.email]
        send_mail(subject, customer_message, email_from, recipient)
        
        if instance.status == "PENDING":
            send_mail(subject, staff_message, email_from, STAFF_EMAILS)
            sms_message = f"Dear Customer,\nYour reservation for Seat No. {seat_number} has been received and is waiting for approval."
        elif instance.status == "ACCEPTED":
            sms_message = f"Dear Customer,\nYour reservation for Seat No. {seat_number} has been accepted."
        elif instance.status == "DECLINED":
            sms_message = f"Dear Customer,\nYour reservation for Seat No. {seat_number} has been declined. Please try again later or contact us."
        else:
            sms_message = f"Dear Customer,\nYour reservation for Seat No. {seat_number} has expired."
        if customer_cellphone:
            send_sms(
                sms_message, 
                settings.DEFAULT_FROM_SMS, 
                [customer_cellphone], 
                fail_silently=False
            )
    except Exception as e:
        print(e)
