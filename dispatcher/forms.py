from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from dispatcher.models import Pricing
from orders.models import Order


User = get_user_model()


class RegisterDriverForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'phone_number',
            'passport',
            'car_number',
            'car_brand',
            'is_driver',
        )


class DriverChangeForm(UserChangeForm):
    passport = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'phone_number',
            'passport',
            'car_number',
            'car_brand',
        )


class PricingForm(forms.ModelForm):
    class Meta:
        model = Pricing
        fields = '__all__'
