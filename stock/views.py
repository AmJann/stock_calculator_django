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
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
import requests



from django.shortcuts import get_object_or_404

class StockCreate(APIView):
    def post(self, request):
        investment_date = datetime.strptime(request.data['investment_date'], '%Y-%m-%d').date()
        initial_balance = float(request.data.get('initial_balance'))
        stock_data = request.data.get('stocks', [])
        user_stock = int(request.data.get('user_stock'))
        list_name = request.data.get('list_name')

        # Check if the user already has a list with the same name
        existing_list = Stock.objects.filter(user_stock=user_stock, list_name=list_name).exists()
        if existing_list:
            return Response({'error': 'List name already exists for the user.'}, status=status.HTTP_400_BAD_REQUEST)

        stocks = []
        for stock in stock_data:
            stock_name = stock['stock_name']
            allocation = stock['allocation']

            # Make API call to retrieve stock price
            url = os.environ['STOCK_URL']
            api_key = os.environ['STOCK_API_KEY']
            params = {
                'access_key': api_key
            }
            price_response = requests.get(f"{url}/tickers/{stock_name}/eod/{investment_date}", params)
            if price_response.status_code == 200:
                data = price_response.json()
                if 'open' in data:
                    price_of_stock = data['open']
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
                'list_name': list_name,
                'stock_name': stock_name,
                'allocation': allocation,
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


class StockCreateOne(APIView):
    def post(self, request):
        investment_date = datetime.strptime(request.data['investment_date'], '%Y-%m-%d').date()
        initial_balance = float(request.data.get('initial_balance'))
        stock_name = request.data.get('stock_name')
        allocation = request.data.get('allocation')
        user_stock = int(request.data.get('user_stock'))
        list_name = request.data.get('list_name')

        # Make API call to retrieve stock price
        url = os.environ['STOCK_URL']
        api_key = os.environ['STOCK_API_KEY']
        params = {
            'access_key': api_key
        }
        price_response = requests.get(f"{url}/tickers/{stock_name}/eod/{investment_date}", params)
        if price_response.status_code == 200:
            data = price_response.json()
            if 'open' in data:
                price_of_stock = data['open']
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
            'list_name': list_name,
            'stock_name': stock_name,
            'allocation': allocation,
            'investment_date': investment_date,
            'initial_investment': investment,
            'price_of_stock': price_of_stock,
            'number_stocks': number_stocks,
            'user_stock': user_stock
        })
        if serializer.is_valid():
            stock = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import generics

class StockBulkUpdateDeleteRetrieveView(generics.UpdateAPIView, generics.DestroyAPIView, generics.ListAPIView):
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        list_name = self.kwargs['list_name']
        return Stock.objects.filter(list_name=list_name)

    def update(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class StockList(generics.ListAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]

class StockDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]

class Login(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class Logout(APIView):
    def post(self, request):
        logout(request)
        return Response({'detail': 'Logged out'})


class Registration(APIView):
    def post(self, request):
        User = get_user_model()
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.create_user(username=username, password=password)

class CheckUserLoggedIn(APIView):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
