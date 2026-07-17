from django.urls import path
from .views import view_cart, add_to_cart, update_cart_item, remove_cart_item, clear_cart

urlpatterns = [
    path('', view_cart, name='cart-view'),
    path('add/', add_to_cart, name='cart-add'),
    path('update/<int:item_id>/', update_cart_item, name='cart-update'),
    path('remove/<int:item_id>/', remove_cart_item, name='cart-remove'),
    path('clear/', clear_cart, name='cart-clear'),
]