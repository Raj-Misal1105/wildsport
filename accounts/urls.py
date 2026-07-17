from django.urls import path
from .views import register_view, login_view, logout_view, profile_view,address_list_create,address_delete

urlpatterns = [
    path('register/', register_view, name='api-register'),
    path('login/', login_view, name='api-login'),
    path('logout/', logout_view, name='api-logout'),
    path('profile/', profile_view, name='api-profile'),
    path('addresses/', address_list_create, name='api-address-list'),
    path('addresses/<int:address_id>/', address_delete, name='api-address-delete'),
]