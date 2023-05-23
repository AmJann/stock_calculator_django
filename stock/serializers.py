from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

# class StockSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Stock
#         fields = '__all__'

class StockSerializer(serializers.Serializer):
    stock_name = serializers.CharField(max_length=100)
    allocation = serializers.FloatField()