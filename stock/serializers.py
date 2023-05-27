from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *



User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'

class CurrentStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = currentStock
        field = '__all__'
