from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from django.contrib.auth import get_user_model
from .models import *
from .serializers import *

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime
from .models import Stock
from .serializers import StockSerializer

class StockCreateView(APIView):
    def post(self, request):
        start_date = datetime.strptime(request.data.get('start_date'), '%Y-%m-%d').date()
        initial_balance = float(request.data.get('initial_balance'))
        stock_data = request.data.get('stocks', [])  # Assuming input is in the format {"stocks": [{"stock_name": "AAPL", "allocation": 0.2}, ...]}
        
        total_allocation = sum(stock['allocation'] for stock in stock_data)
        investments = [stock['allocation'] / total_allocation * initial_balance for stock in stock_data]
        
        stocks = []
        for stock, investment in zip(stock_data, investments):
            serializer = StockSerializer(data=stock)
            if serializer.is_valid():
                stock_instance = Stock(
                    stock_name=serializer.validated_data['stock_name'],
                    investment_date=start_date,
                    initial_investment=investment,
                    price_of_stock=0,  # You can set this value accordingly
                    number_stocks=0,  # You can set this value accordingly
                    user=request.user
                )
                stocks.append(stock_instance)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        Stock.objects.bulk_create(stocks)
        return Response("Stocks created successfully", status=status.HTTP_201_CREATED)

class RegistrationView(APIView):
    def post(self, request):
        User = get_user_model()
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.create_user(username=username, password=password)

class CheckUserLoggedInView(APIView):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
