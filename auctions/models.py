from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Listing(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=2500)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    category = models.CharField(max_length=64)
    creation_date = models.DateTimeField(auto_now=True)
    watchlist = models.ManyToManyField(User, blank=True, related_name="watchlist")
    active = models.BooleanField(default=True)
    image = models.URLField(max_length=200, null=True, blank=True)


class Bid(models.Model):
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="history")


class Comment(models.Model):
    comment = models.CharField(max_length=10000)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
