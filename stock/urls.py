from django.urls import path
from .views import StockCreateView

urlpatterns = [
    path('stocks/create/', StockCreateView.as_view(), name='create_stock'),
  
]