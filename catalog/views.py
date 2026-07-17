from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, ProductImageSerializer


# ---------------- CATEGORY ----------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def category_list_create(request):
    if request.method == 'GET':
        categories = Category.objects.filter(is_active=True)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    # POST -> sirf admin
    if not request.user.is_staff:
        return Response({"error": "Only admin can create category"}, status=status.HTTP_403_FORBIDDEN)

    serializer = CategorySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)

    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    # PUT/PATCH/DELETE -> sirf admin
    if not request.user.is_staff:
        return Response({"error": "Only admin can modify category"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'DELETE':
        category.delete()
        return Response({"message": "Category deleted"}, status=status.HTTP_204_NO_CONTENT)

    partial = request.method == 'PATCH'
    serializer = CategorySerializer(category, data=request.data, partial=partial)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


# ---------------- PRODUCT ----------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_list_create(request):
    if request.method == 'GET':
        products = Product.objects.filter(is_active=True)

        # ---- filters ----
        search = request.GET.get('search')
        category = request.GET.get('category')
        brand = request.GET.get('brand')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        sort = request.GET.get('sort')
        page_number = request.GET.get('page', 1)

        if search:
            products = products.filter(name__icontains=search)
        if category:
            products = products.filter(categories__slug=category).distinct()
        if brand:
            products = products.filter(brand__icontains=brand)
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)

        if sort == 'price_low':
            products = products.order_by('price')
        elif sort == 'price_high':
            products = products.order_by('-price')
        elif sort == 'newest':
            products = products.order_by('-created_at')
        elif sort == 'popularity':
            products = products.order_by('-rating_avg')

        # ---- pagination ----
        paginator = Paginator(products, 12)   # 12 products per page
        page_obj = paginator.get_page(page_number)

        serializer = ProductSerializer(page_obj, many=True)
        return Response({
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "results": serializer.data
        })

    # POST -> sirf admin
    if not request.user.is_staff:
        return Response({"error": "Only admin can create product"}, status=status.HTTP_403_FORBIDDEN)

    serializer = ProductSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    if not request.user.is_staff:
        return Response({"error": "Only admin can modify product"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'DELETE':
        product.delete()
        return Response({"message": "Product deleted"}, status=status.HTTP_204_NO_CONTENT)

    partial = request.method == 'PATCH'
    serializer = ProductSerializer(product, data=request.data, partial=partial)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


# ---------------- PRODUCT IMAGE (upload alag se) ----------------

@api_view(['POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_image_upload(request, slug):
    if not request.user.is_staff:
        return Response({"error": "Only admin can upload images"}, status=status.HTTP_403_FORBIDDEN)

    product = get_object_or_404(Product, slug=slug)
    serializer = ProductImageSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(product=product)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
