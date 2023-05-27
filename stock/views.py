from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
# from rest_framework.decorators import api_view
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

from django.db import transaction
from django.utils.crypto import get_random_string


from django.contrib.auth.models import User


from django.contrib.auth.models import User


class StockCreate(APIView):
    # @api_view(['GET', 'POST'])
    def post(self, request):
        investment_date = datetime.strptime(
            request.data['investment_date'], '%Y-%m-%d').date()
        initial_balance = float(request.data.get('initial_balance'))
        stock_data = request.data.get('stocks', [])
        user_stock_id = int(request.data.get('user_stock'))

        # Retrieve the User instance based on the user_stock_id
        try:
            user_stock = User.objects.get(id=user_stock_id)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        list_name = request.data.get('list_name')

        # Generate a random list_id
        list_id = get_random_string(length=16)

        # Check if the user already has a list with the same list_id
        existing_list = Stock.objects.filter(
            user_stock=user_stock, list_id=list_id).exists()
        if existing_list:
            return Response({'error': 'List ID already exists for the user.'}, status=status.HTTP_400_BAD_REQUEST)

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
            price_response = requests.get(
                f"{url}/tickers/{stock_name}/eod/{investment_date}", params)
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
                'list_id': list_id,
                'stock_name': stock_name,
                'allocation': allocation,
                'investment_date': investment_date,
                'initial_investment': investment,
                'price_of_stock': price_of_stock,
                'number_stocks': number_stocks,
                'user_stock': user_stock_id,  # Use the primary key value of the User instance
            })
            if serializer.is_valid():
                stocks.append(serializer.validated_data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            created_stocks = Stock.objects.bulk_create([
                Stock(
                    list_name=stock_data['list_name'],
                    list_id=stock_data['list_id'],
                    stock_name=stock_data['stock_name'],
                    allocation=stock_data['allocation'],
                    investment_date=stock_data['investment_date'],
                    initial_investment=stock_data['initial_investment'],
                    price_of_stock=stock_data['price_of_stock'],
                    number_stocks=stock_data['number_stocks'],
                    user_stock=user_stock,
                ) for stock_data in stocks
            ])

        serializer = StockSerializer(created_stocks, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class StockCreateOne(APIView):
    # @api_view(['GET', 'POST'])
    def post(self, request):
        investment_date = datetime.strptime(
            request.data['investment_date'], '%Y-%m-%d').date()
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
        price_response = requests.get(
            f"{url}/tickers/{stock_name}/eod/{investment_date}", params)
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


class StockBulkUpdateDeleteRetrieveView(generics.UpdateAPIView, generics.DestroyAPIView, generics.ListAPIView):
    serializer_class = StockSerializer

    def get_queryset(self):
        list_id = self.kwargs['list_id']
        return Stock.objects.filter(list_id=list_id)

    def partial_update(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        stocks_data = request.data
        updated_stocks = []

        for stock_data in stocks_data:
            stock_id = stock_data.get('id')
            if stock_id:
                stock = queryset.filter(id=stock_id).first()
                if stock:
                    serializer = self.get_serializer(
                        stock, data=stock_data, partial=True)
                    serializer.is_valid(raise_exception=True)
                    updated_stock = serializer.save()
                    updated_stocks.append(updated_stock)

        # Return the updated stock data in the response
        serializer = self.get_serializer(updated_stocks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StockList(generics.ListAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer


class StockDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer


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
        return Response({'message': 'Registration successful'})


class CheckUserLoggedIn(APIView):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


def get_today_date():
    today = datetime.date.today()
    return today.strftime('%Y-%m-%d')


class StockDataView(APIView):
    def get(self, request, list_id):
        selected_portfolios = Stock.objects.filter(list_id=list_id)
        stock_symbols = [
            portfolio.stock_name for portfolio in selected_portfolios]
        stock_data = []

        for symbol in stock_symbols:
            stock_name = symbol
            investment_date = stock.investment_date

            # Modify the URL to use HTTP instead of HTTPS
            url = f'http://api.marketstack.com/v1/eod?access_key=953023c4e78c08dbd62a7fcf39e06946&symbols={stock_name}&date_from={investment_date}&date_to={get_today_date()}'

            # Make the API call with the modified URL
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                stock_data.append(data)
            if response.status_code == 304:
                return Response(response.content)

        return Response(stock_data)


class StockCurrentDataView(APIView):
    def get(self, request, list_id):
        selected_stocks = Stock.objects.filter(list_id=list_id)
        stock_data = []

        for stock in selected_stocks:
            stock_symbol = stock.stock_name

            url = f'http://api.marketstack.com/v1/tickers/{stock_symbol}/eod/latest?access_key=e938ebffd18b41ae0e7ee5d20ddb1869'

            try:
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for non-2xx status codes

                data = response.json()
                close = data.get('close')

                if close is not None:
                    stock_data.append({'close': close})
                    print(
                        f"Received data for stock {stock_symbol}: close={close}")
                else:
                    print(f"No 'close' data found for stock {stock_symbol}")
            except requests.exceptions.RequestException as e:
                # Handle request exceptions (e.g., network error)
                # You can log the error or handle it in a way that suits your needs
                print(
                    f"Error retrieving data for stock {stock_symbol}: {str(e)}")

        serializer = CurrentStockSerializer(stock_data, many=True)
        return Response(serializer.data)
