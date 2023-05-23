from django.contrib.auth.models import AbstractUser
from django.db import models


class Stock(models.Model):
stock_name = models.CharField(max_length=100)
investment_date = models.DateField()
initial_investment = models.IntegerField()
price_of_stock = models.IntegerField()
number_stocks = models.IntegerField()
user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.username} | {self.stock_name}"

class User(AbstractUser):  

    def __str__(self):
        return self.username