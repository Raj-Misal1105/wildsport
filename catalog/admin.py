from django.contrib import admin
from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'is_active', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_categories', 'brand', 'price', 'discount_price', 'stock', 'is_active')
    list_filter = ('categories', 'brand', 'is_active')
    search_fields = ('name', 'brand')
    filter_horizontal = ('categories',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]

    def get_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])
    get_categories.short_description = 'Categories'