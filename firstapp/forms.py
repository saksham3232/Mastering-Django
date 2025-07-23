from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser,Contact, Customer, Seller, SellerAdditional, ProductInCart
from django import forms
from django.core.validators import RegexValidator


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email',)


class ContactUsForm(forms.ModelForm):
    # email = forms.EmailField(required=True) 
    # name = forms.CharField(required=True, max_length=50, label='Name')
    # phone_regex = RegexValidator(regex=r'^\d{10}$', message="Phone number should be 10 digits long and contain only numbers.")
    # phone = forms.CharField(required=True, max_length=255, validators=[phone_regex], label='Phone Number')
    # query = forms.CharField( widget=forms.Textarea, required=False, label='Your Query')

    class Meta:
        model = Contact
        fields = [
            'email',
            'phone',
            'name',
            'query'
        ]


class RegistrationFormSeller(UserCreationForm):
    gst = forms.CharField(max_length=10)
    warehouse_location = forms.CharField(max_length=1000)
    class Meta:
        model = Seller
        fields = [
            'email',
            'name',
            'password1',
            'password2',
            'gst',
            'warehouse_location'
        ]

class RegistrationForm(UserCreationForm):
    class Meta:
        model = Customer
        fields = [
            'email',
            'name',
            'password1',
            'password2',
        ]


class RegistrationFormSeller2(forms.ModelForm):
    class Meta:
        model = SellerAdditional
        fields = [
            'gst',
            'warehouse_location'
        ]


class CartForm(forms.ModelForm):
    class Meta:
        model = ProductInCart
        fields = [
            'quantity',
        ]