from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from catalog.models import Category, Product


def home_view(request):
    categories = Category.objects.filter(is_active=True, parent=None)[:10]
    best_sellers = Product.objects.filter(is_active=True).order_by('-rating_avg')[:5]
    top_picks = Product.objects.filter(is_active=True).order_by('-created_at')[:5]

    context = {
        'categories': categories,
        'best_sellers': best_sellers,
        'top_picks': top_picks,
    }
    return render(request, 'home.html', context)


def product_listing_view(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True, parent=None)

 
    search = request.GET.get('search')
    category_slug = request.GET.get('category')
    brand = request.GET.getlist('brand')         
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    min_rating = request.GET.get('rating')
    sort = request.GET.get('sort')
    page_number = request.GET.get('page', 1)

    if search:
        products = products.filter(name__icontains=search)
    if category_slug:
        products = products.filter(categories__slug=category_slug).distinct()
    if brand:
        products = products.filter(brand__in=brand)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if min_rating:
        products = products.filter(rating_avg__gte=min_rating)

    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == 'popularity':
        products = products.order_by('-rating_avg')
    else:
        products = products.order_by('-created_at')


    all_brands = Product.objects.filter(is_active=True).values_list('brand', flat=True).distinct()

    # ---- pagination ----
    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'categories': categories,
        'all_brands': all_brands,
        'selected_category': category_slug,
        'selected_brands': brand,
        'search_query': search or '',
        'current_sort': sort or '',
    }
    return render(request, 'product_listing.html', context)


def product_detail_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        categories__in=product.categories.all(), is_active=True
    ).exclude(id=product.id).distinct()[:4]

    sizes_list = []
    if product.available_sizes:
        sizes_list = [s.strip() for s in product.available_sizes.split(',') if s.strip()]

    context = {
        'product': product,
        'related_products': related_products,
        'sizes_list': sizes_list,   
    }
    return render(request, 'product_detail.html', context)


def cart_view(request):
    return render(request, 'cart.html')


def checkout_view(request):
    return render(request, 'checkout.html')

def order_history_view(request):
    return render(request, 'order_history.html')


def order_detail_view(request, order_id):
    return render(request, 'order_detail.html', {'order_id': order_id})


def profile_view(request):
    return render(request, 'profile.html')