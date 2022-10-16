from django.contrib import messages
from django.views.generic import View
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from canteen.forms import AddressUpdateForm


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account till it is confirmed
            user.save()
            current_site = get_current_site(request)
            subject = "Activate Your Oshinglish Account"
            message = render_to_string(
                "registration/account_activation_email.html",
                {
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            email_from = settings.DEFAULT_FROM_EMAIL
            admin = "abiatarfestus@outlook.com"
            recipient_list = [admin]
            send_mail(subject, message, email_from, recipient_list)
            messages.success(
                request, ("Registration completed successfully!")
            )
            # return redirect(reverse("index"))
            return redirect("users:confirmation")
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form})


def confirmation(request):
    return render(request, "registration/registration_confirmation.html", {})


@login_required
def profile(request):
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        address_form = AddressUpdateForm(request.POST, instance=request.user.address)
        if user_form.is_valid() and profile_form.is_valid() and address_form.is_valid:
            user_form.save()
            profile_form.save()
            address_form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect("users:profile")  # Redirect back to profile page
        else:
            messages.warning(request, "Profile not updated! Please correct the errors shown below.")
            context = {"user_form": user_form, "profile_form": profile_form, "address_form": address_form}
            return render(request, "users/profile.html", context)
    user_form = UserUpdateForm(instance=request.user)
    profile_form = ProfileUpdateForm(instance=request.user.profile)
    address_form = AddressUpdateForm(instance=request.user.address)
    context = {"user_form": user_form, "profile_form": profile_form, "address_form": address_form}
    return render(request, "users/profile.html", context)


class ActivateAccount(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            current_site = get_current_site(request)
            username = user.username
            subject = "Account activated"
            message = render_to_string(
                "registration/account_activated.html",
                {
                    "domain": current_site.domain,
                    "user": username,
                },
            )
            email_from = settings.DEFAULT_FROM_EMAIL
            admin = "abiatarfestus@outlook.com"
            recipient_list = [admin]
            send_mail(subject, message, email_from, recipient_list)
            messages.success(request, ("The account has been activated."))
            return redirect("home")
        else:
            messages.warning(
                request,
                (
                    "The confirmation link was invalid, possibly because it has already been used."
                ),
            )
            return redirect("home")
