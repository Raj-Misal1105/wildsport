from django.urls import path
from .views import home_view, product_listing_view,product_detail_view, cart_view,checkout_view, order_history_view, order_detail_view, profile_view


urlpatterns = [
    path('', home_view, name='home'),
    path('products/', product_listing_view, name='product-listing'),
    path('products/<slug:slug>/', product_detail_view, name='product-detail'),
    path('cart/', cart_view, name='cart'),
    path('checkout/', checkout_view, name='checkout'),
    path('orders/', order_history_view, name='order-history'),
    path('orders/<int:order_id>/', order_detail_view, name='order-detail-page'),
    path('profile/', profile_view, name='profile-page'),
]