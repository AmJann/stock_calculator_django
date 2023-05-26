from django.urls import path
from .views import *

urlpatterns = [
    path('stocks/create/', StockCreate.as_view(), name='stocks-create'),
    path('stock/create/', StockCreateOne.as_view(), name='stock-create'),
    path('stocks/', StockList.as_view(), name='stock-list'),
    path('stocks/<int:pk>/', StockDetail.as_view(), name='stock-detail'),
    path('stocks/bulk-update-delete-retrieve/<slug:list_id>/',
         StockBulkUpdateDeleteRetrieveView.as_view(), name='stock-list'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('registration/', Registration.as_view(), name='registration'),
    path('check-user/', CheckUserLoggedIn.as_view(), name='check-user-logged-in'),
]
