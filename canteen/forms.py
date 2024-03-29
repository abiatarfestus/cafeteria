from unicodedata import name

from django import forms
from pyexpat import model
from users.models import Profile

from .models import Customer, DeliveryAddress, Order, Reservation, Seat


class AddressUpdateForm(forms.ModelForm):
    class Meta:
        model = DeliveryAddress
        fields = ["address"]
        widgets = {
            "address": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg mb-2",
                    "name": "address",
                    "required": True,                 
                }
            )
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["cellphone"]
        widgets = {
            "cellphone": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg mb-2",
                    "required":True,
                }
            )
        }


class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["payment_method", "delivery", "reference"]
        widgets = {
            "delivery": forms.CheckboxInput(
                attrs={
                    "type": "checkbox",
                    "class": "form-check mb-2",
                    "name": "delivery",
                    "id": "delivery",
                }
            ),
            "payment_method": forms.Select(
                attrs={
                    "class": "form-control form-control-lg mb-2",
                    "id": "paymentMethod",
                    "required":True
                }
            ),
            "reference": forms.TextInput(
                attrs={
                    "class": "form-control form-control-lg mb-2", 
                    "disabled": "disabled",
                    "id": "reference",
                    "required":True,
                }
            ),
        }
        


class ReservationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["customer"].disabled = True

    class Meta:
        model = Reservation
        fields = ["customer", "seat"]

    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        empty_label="Select customer",
        widget=forms.Select(attrs={"class": "form-control form-control-lg mb-2"}),
    )

    seat = forms.ModelChoiceField(
        queryset=Seat.objects.filter(status="OPEN").order_by("seat_number"),
        empty_label="Select the seat",
        widget=forms.Select(attrs={"class": "form-control form-control-lg mb-2"}),
    )

class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True, widget=forms.TextInput(attrs={"class": "form-control form-control-lg mb-2"}))
    subject = forms.CharField(required=True, widget=forms.TextInput(attrs={"class": "form-control form-control-lg mb-2"}))
    message = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control form-control-lg mb-2"}), required=True)