from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.admin_login_view, name='dashboard-login'),
    path('logout/', views.admin_logout_view, name='dashboard-logout'),
    path('', views.dashboard_home, name='dashboard-home'),

    path('categories/', views.category_list, name='dashboard-category-list'),
    path('categories/add/', views.category_add, name='dashboard-category-add'),
    path('categories/<int:category_id>/edit/', views.category_edit, name='dashboard-category-edit'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='dashboard-category-delete'),

    path('products/', views.product_list, name='dashboard-product-list'),
    path('products/add/', views.product_add, name='dashboard-product-add'),
    path('products/<int:product_id>/edit/', views.product_edit, name='dashboard-product-edit'),
    path('products/<int:product_id>/delete/', views.product_delete, name='dashboard-product-delete'),
    path('products/image/<int:image_id>/delete/', views.product_image_delete, name='dashboard-product-image-delete'),

    path('orders/', views.order_list, name='dashboard-order-list'),
    path('orders/<int:order_id>/', views.order_detail, name='dashboard-order-detail'),
]