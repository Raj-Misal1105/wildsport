from django.urls import path
from .views import checkout, order_list, order_detail, cancel_order

urlpatterns = [
    path('checkout/', checkout, name='order-checkout'),
    path('', order_list, name='order-list'),
    path('<int:order_id>/', order_detail, name='order-detail'),
    path('<int:order_id>/cancel/', cancel_order, name='order-cancel'),
]