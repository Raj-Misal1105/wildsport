from urllib import request

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count
from catalog.models import Category, Product, ProductImage
from orders.models import Order


def is_admin(user):
    return user.is_authenticated and user.is_staff


# ---------------- AUTH ----------------

def admin_login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard-home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user and user.is_staff:
            login(request, user)
            return redirect('dashboard-home')
        else:
            messages.error(request, 'Invalid credentials or you are not an admin.')

    return render(request, 'dashboard/login.html')


def admin_logout_view(request):
    logout(request)
    return redirect('dashboard-login')


# ---------------- DASHBOARD HOME ----------------

@user_passes_test(is_admin, login_url='dashboard-login')
def dashboard_home(request):
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    total_revenue = Order.objects.exclude(status='cancelled').aggregate(total=Sum('total_amount'))['total'] or 0
    low_stock_products = Product.objects.filter(stock__lte=5, is_active=True)
    recent_orders = Order.objects.order_by('-created_at')[:5]

    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
    }
    return render(request, 'dashboard/home.html', context)


# ---------------- CATEGORY MANAGEMENT ----------------

@user_passes_test(is_admin, login_url='dashboard-login')
def category_list(request):
    categories = Category.objects.all().order_by('-created_at')
    return render(request, 'dashboard/category_list.html', {'categories': categories})


@user_passes_test(is_admin, login_url='dashboard-login')
def category_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        icon = request.FILES.get('icon')
        is_active = request.POST.get('is_active') == 'on'

        if Category.objects.filter(name=name).exists():
            messages.error(request, 'Category with this name already exists.')
        else:
            Category.objects.create(name=name, icon=icon, is_active=is_active)
            messages.success(request, 'Category added successfully.')
            return redirect('dashboard-category-list')

    return render(request, 'dashboard/category_form.html', {'category': None})


@user_passes_test(is_admin, login_url='dashboard-login')
def category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        category.name = request.POST.get('name')
        if request.FILES.get('icon'):
            category.icon = request.FILES.get('icon')
        category.is_active = request.POST.get('is_active') == 'on'
        category.save()
        messages.success(request, 'Category updated successfully.')
        return redirect('dashboard-category-list')

    return render(request, 'dashboard/category_form.html', {'category': category})


@user_passes_test(is_admin, login_url='dashboard-login')
def category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, 'Category deleted.')
    return redirect('dashboard-category-list')


# ---------------- PRODUCT MANAGEMENT ----------------

@user_passes_test(is_admin, login_url='dashboard-login')
def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    search = request.GET.get('search')
    if search:
        products = products.filter(name__icontains=search)
    return render(request, 'dashboard/product_list.html', {'products': products, 'search': search or ''})


@user_passes_test(is_admin, login_url='dashboard-login')
def product_add(request):
    categories = Category.objects.filter(is_active=True)
    if request.method == 'POST':
        product = Product.objects.create(
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            brand=request.POST.get('brand'),
            price=request.POST.get('price'),
            discount_price=request.POST.get('discount_price') or None,
            stock=request.POST.get('stock'),
            size_type=request.POST.get('size_type', 'none'), 
            available_sizes=request.POST.get('available_sizes', ''),
            is_active=request.POST.get('is_active') == 'on'
        )
        product.categories.set(request.POST.getlist('categories'))   # <-- naya

        images = request.FILES.getlist('images')
        for idx, img in enumerate(images):
            ProductImage.objects.create(product=product, image=img, is_primary=(idx == 0))

        messages.success(request, 'Product added successfully.')
        return redirect('dashboard-product-list')

    return render(request, 'dashboard/product_form.html', {'product': None, 'categories': categories})


@user_passes_test(is_admin, login_url='dashboard-login')
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.filter(is_active=True)

    if request.method == 'POST':
        product.categories.set(request.POST.getlist('categories'))
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.brand = request.POST.get('brand')
        product.price = request.POST.get('price')
        product.discount_price = request.POST.get('discount_price') or None
        product.stock = request.POST.get('stock')
        product.size_type = request.POST.get('size_type', 'none')
        product.available_sizes = request.POST.get('available_sizes', '')
        product.is_active = request.POST.get('is_active') == 'on'
        product.save()

        images = request.FILES.getlist('images')
        for img in images:
            ProductImage.objects.create(product=product, image=img, is_primary=not product.images.exists())

        messages.success(request, 'Product updated successfully.')
        return redirect('dashboard-product-list')

    return render(request, 'dashboard/product_form.html', {'product': product, 'categories': categories})


@user_passes_test(is_admin, login_url='dashboard-login')
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, 'Product deleted.')
    return redirect('dashboard-product-list')


@user_passes_test(is_admin, login_url='dashboard-login')
def product_image_delete(request, image_id):
    image = get_object_or_404(ProductImage, id=image_id)
    product_id = image.product.id
    image.delete()
    messages.success(request, 'Image removed.')
    return redirect('dashboard-product-edit', product_id=product_id)


# ---------------- ORDER MANAGEMENT ----------------

@user_passes_test(is_admin, login_url='dashboard-login')
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'dashboard/order_list.html', {'orders': orders, 'status_filter': status_filter or ''})


@user_passes_test(is_admin, login_url='dashboard-login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        messages.success(request, f'Order status updated to {new_status}.')
        return redirect('dashboard-order-detail', order_id=order.id)

    return render(request, 'dashboard/order_detail.html', {'order': order})