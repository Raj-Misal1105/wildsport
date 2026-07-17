from rest_framework import serializers
from .models import Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'parent', 'is_active', 'created_at']
        read_only_fields = ['slug']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Category.objects.all(), source='categories', required=False
    )
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'categories', 'category_ids', 'name', 'slug', 'description', 'brand',
        'price', 'discount_price', 'final_price', 'stock', 'rating_avg',
        'size_type', 'available_sizes',
        'is_active', 'images', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'rating_avg']

    def get_final_price(self, obj):
        return obj.discount_price or obj.price