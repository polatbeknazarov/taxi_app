from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from dispatcher.models import Pricing


User = get_user_model()


class RegisterDriverForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "passport",
            "car_number",
            "car_brand",
            "is_driver",
        )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if not username.isascii():
            raise forms.ValidationError(
                "Имя пользователя может содержать только латинские символы."
            )

        return username.lower()

    def clean_first_name(self):
        first_name = self.cleaned_data["first_name"]

        return first_name.title()

    def clean_last_name(self):
        last_name = self.cleaned_data["last_name"]

        return last_name.title()

    def clean_car_brand(self):
        car_brand = self.cleaned_data["car_brand"]

        return car_brand.title()


class DriverChangeForm(UserChangeForm):
    passport = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "passport",
            "car_number",
            "car_brand",
        )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if not username.isascii():
            raise forms.ValidationError(
                "Имя пользователя может содержать только латинские символы."
            )

        return username.lower()

    def clean_first_name(self):
        first_name = self.cleaned_data["first_name"]

        return first_name.title()

    def clean_last_name(self):
        last_name = self.cleaned_data["last_name"]

        return last_name.title()


class PricingForm(forms.ModelForm):
    class Meta:
        model = Pricing
        fields = "__all__"
