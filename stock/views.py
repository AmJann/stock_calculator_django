from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from django.contrib.auth import get_user_model
from .models import *
from .serializers import *
import os
import environ
from dotenv import load_dotenv
from django.contrib.auth import get_user_model


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime
import requests


class StockCreateView(APIView):
    def post(self, request):
        investment_date = datetime.strptime(request.data['investment_date'], '%Y-%m-%d').date()
        initial_balance = float(request.data.get('initial_balance'))
        stock_data = request.data.get('stocks', [])
        user_stock = int(request.data.get('user_stock'))

        stocks = []
        for stock in stock_data:
            stock_name = stock['stock_name']
            allocation = stock['allocation']

            # Make API call to retrieve stock price
            url = os.environ['STOCK_URL']
            api_key = os.environ['STOCK_API_KEY']
            params = {
                'access_key': '7acc9a4809f1f6db994b674a1caf65f2'
            }
            price_response = requests.get(f"http://api.marketstack.com/v1/tickers/{stock_name}/eod/{investment_date}", params)
            if price_response.status_code == 200:
                data = price_response.json()
                if 'open' in data:
                    price_of_stock = data['open']
                    Response(price_of_stock)
                else:
                    # Handle the case when stock price data is not available
                    error_message = f"Failed to retrieve stock price data. Response content: {price_response.content}"
                    return Response(error_message, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Handle the case when stock price API call fails
                error_message = f"Failed to retrieve stock price. Response content: {price_response.content}"
                return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

            investment = initial_balance * allocation
            number_stocks = investment / price_of_stock

            serializer = StockSerializer(data={
                'stock_name': stock_name,
                'investment_date': investment_date,
                'initial_investment': investment,
                'price_of_stock': price_of_stock,
                'number_stocks': number_stocks,
                'user_stock': user_stock
            })
            if serializer.is_valid():
                stocks.append(serializer.save())
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        created_stocks = Stock.objects.bulk_create(stocks)
        serializer = StockSerializer(created_stocks, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)








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
