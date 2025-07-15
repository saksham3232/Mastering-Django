from django.db import models

from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
from django.core.validators import RegexValidator
from django.db.models import Q
# Create your models here.


from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import PermissionsMixin


from .managers import CustomUserManager

from multiselectfield import MultiSelectField


# class UserType(models.Model):
#     CUSTOMER=1
#     SELLER=2
#     TYPE_CHOICES = (
#         (SELLER, 'Seller'),
#         (CUSTOMER, 'Customer'),
#     )
#     id = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, primary_key=True)

#     def __str__(self):
#         return self.get_id_display()


class LowerCaseEmailField(models.EmailField):
    def to_python(self, value):
        """Convert the value to lowercase before saving it to the database."""
        value = super(LowerCaseEmailField, self).to_python(value)
        if isinstance(value, str):
            return value.lower()
        return value



class CustomUser(AbstractBaseUser, PermissionsMixin):
    # username = None
    email = LowerCaseEmailField(_('email address'), unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    # 1
    # is_customer = models.BooleanField(default=True)
    # is_seller = models.BooleanField(default=False)

    # 2.1
    # type = (
    #     (1, 'Seller'),
    #     (2, 'Customer'),
    # )
    # user_type = models.IntegerField(choices=type, default=2)

    # 2.2
    # choices = (
    #     (1, 'Seller'),
    #     (2, 'Customer'),
    # )
    # user_type = MultiSelectField(choices=choices, default=[2], max_length=20, min_count=1, max_count=2)

    # usertype = models.ManyToManyField(UserType)

    class Types(models.TextChoices):
        SELLER = "Seller", "SELLER"
        CUSTOMER = "Customer", "CUSTOMER"

    # Types = (
    #     (1, 'SELLER'),
    #     (2, 'CUSTOMER')
    # )
    # type = models.IntegerField(choices=Types, default=2)

    default_type = Types.CUSTOMER

    # type = models.CharField(_('Type'), max_length=255, choices=Types.choices, default=default_type)
    type = MultiSelectField(choices=Types.choices, default=[], null=True, blank=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


    def save(self, *args, **kwargs):
        if not self.id:
            self.type.append(self.default_type)
        return super().save(*args, **kwargs)
    


class CustomerAdditional(models.Model):
    user=models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.CharField(max_length=1000)

class SellerAdditional(models.Model):
    user=models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    gst=models.CharField(max_length=15, unique=True)
    warehouse_location=models.CharField(max_length=1000)


# Model Managers for proxy models
class SellerManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(Q(type__contains=CustomUser.Types.SELLER))


class CustomerManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(Q(type__contains=CustomUser.Types.CUSTOMER))



# Proxy Models. They do not create a separate table in the database.
class Seller(CustomUser):
    default_type = CustomUser.Types.SELLER
    objects = SellerManager()
    class Meta:
        proxy = True

    def sell(self):
        print("Selling products...")

    @property
    def showAdditional(self):
        return self.selleradditional


class Customer(CustomUser):
    default_type = CustomUser.Types.CUSTOMER
    objects = CustomerManager()
    class Meta:
        proxy = True

    def buy(self):
        print("Buying products...")

    @property
    def showAdditional(self):
        return self.customeradditional
    

class Contact(models.Model):
    email = models.EmailField()
    name = models.CharField()
    phone_regex = RegexValidator(regex=r'^\d{10}$',
                                 message="Phone number should be 10 digits long and contain only numbers.")
    phone = models.CharField(validators=[phone_regex])
    query = models.TextField()

    

# class CustomerAdditional(models.Model):
#     user=models.OneToOneField(CustomUser, on_delete=models.CASCADE)
#     address = models.CharField(max_length=1000)

# class SellerAdditional(models.Model):
#     user=models.OneToOneField(CustomUser, on_delete=models.CASCADE)
#     gst=models.CharField(max_length=15, unique=True)
#     warehouse_location=models.CharField(max_length=1000)



class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=15)
    price = models.FloatField()

    @classmethod
    def updateprice(cls, product_id, price):
        product = cls.objects.filter(product_id=product_id)
        product = product.first()
        product.price = price
        product.save()
        return product
    
    @classmethod
    def create(cls, product_name, price):
        product = Product(product_name=product_name, price=price)
        product.save()
        return product

    def __str__(self):
        return self.product_name
    

class CartManager(models.Manager):
    def create_cart(self, user):
        cart = self.create(user=user)
        # you can perform more operations
        return cart


class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_on = models.DateTimeField(default=timezone.now)

    objects = CartManager()


class ProductInCart(models.Model):
    class Meta:
        unique_together = (('cart', 'product'),)

    product_in_cart_id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()


class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    status_choices = (
        (1, 'Not Packed'),
        (2, 'Ready for Shipment'),
        (3, 'Shipped'),
        (4, 'Delivered'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.IntegerField(choices=status_choices, default=1)


class Deal(models.Model):
    user = models.ManyToManyField(CustomUser)
    deal_name = models.CharField(max_length=255)
