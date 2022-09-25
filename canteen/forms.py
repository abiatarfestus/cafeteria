from unicodedata import name
from django import forms
from .models import DeliveryAddress, Order

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