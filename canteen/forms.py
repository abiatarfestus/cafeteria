from pyexpat import model
from unicodedata import name
from django import forms
from .models import DeliveryAddress, Order, Reservation, Seat, Customer

class AddressUpdateForm(forms.ModelForm):
    class Meta:
        model = DeliveryAddress
        fields = ["address"]
        widgets = {
            "address": forms.TextInput(
                attrs={"class": "form-control form-control-lg mb-2", "name":"address", "id":"address-field"}
            )
        }

class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["delivery"]
        widgets = {
            "delivery": forms.CheckboxInput(attrs={'type': 'checkbox', 'class': 'form-check form-check-inline', "name":"delivery", "id":"delivery-check"})
        }

class ReservationForm(forms.ModelForm):
    seat = forms.ModelChoiceField(
        queryset=Seat.objects.filter(status="OPEN").order_by("seat_number"),
        empty_label="Select the seat",
        widget=forms.Select(
            attrs={
                "class": "form-control form-control-lg mb-2"
            }
        ),
    )
    class Meta:
        model = Reservation
        fields = ["seat"]