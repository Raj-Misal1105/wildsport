from django.urls import path
from .views import (
    category_list_create, category_detail,
    product_list_create, product_detail, product_image_upload
)

urlpatterns = [
    path('categories/', category_list_create, name='category-list'),
    path('categories/<slug:slug>/', category_detail, name='category-detail'),

    path('products/', product_list_create, name='product-list'),
    path('products/<slug:slug>/', product_detail, name='product-detail'),
    path('products/<slug:slug>/upload-image/', product_image_upload, name='product-image-upload'),
]