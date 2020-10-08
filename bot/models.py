from enum import Enum

from django.db import models


class User(models.Model):
    user_id = models.BigIntegerField()
    full_name = models.CharField(max_length=256)
    username = models.CharField(max_length=256, null=True)
    balance = models.DecimalField(max_digits=24, decimal_places=2, default=0)
    admin = models.BooleanField(default=False)
    ban_status = models.BooleanField(default=False)
    start_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id} - {self.full_name} - {self.balance} USD"


class Category(models.Model):
    name = models.CharField(max_length=256)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=24, decimal_places=2, default=0)
    doc = models.CharField(max_length=256, null=True, blank=True)
    data = models.TextField(default='')
    for_one_user = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=256)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=False, null=False)
    # price = models.DecimalField(max_digits=24, decimal_places=2, default=0)
    # doc = models.CharField(max_length=256, null=True, blank=True)
    # data = models.TextField(default='')
    # for_one_user = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} - {self.category.price} USD'


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=False, null=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.full_name} - {self.product.name} - {self.product.category.price} USD'


class PaymentStatus(Enum):
    unconfirmed = '0'
    confirmed = '2'


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    address = models.CharField(max_length=256)
    status = models.SmallIntegerField(default=PaymentStatus.unconfirmed.value)
    txid = models.CharField(max_length=256, blank=True, null=True)
    value = models.DecimalField(max_digits=24, decimal_places=2, default=0)
    date_updated = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.user_id} ({self.user.full_name}) - {self.address} - {self.status}'
