from django.db import models
from django.contrib.auth import get_user_model


class Stock(models.Model):
    list_name = models.CharField(max_length=100)
    list_id = models.CharField(max_length=16)
    allocation = models.FloatField()
    stock_name = models.CharField(max_length=100)
    investment_date = models.DateField()
    initial_investment = models.FloatField()
    price_of_stock = models.FloatField()
    number_stocks = models.FloatField()
    user_stock = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='stocks')

    def __str__(self):
        formatted_date = self.investment_date.strftime('%Y-%m-%d')
        return f"{self.user_stock.username} | {self.stock_name} | {self.list_name}"



