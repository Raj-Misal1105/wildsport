from rest_framework import serializers
from .models import Order, OrderItem
from catalog.serializers import ProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_detail', 'quantity', 'price_at_purchase', 'selected_size']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'items', 'total_amount', 'status',
            'payment_method', 'shipping_address', 'created_at', 'updated_at'
        ]
        read_only_fields = ['order_number', 'user', 'total_amount', 'status']


class CheckoutSerializer(serializers.Serializer):
    
    shipping_address = serializers.CharField()
    payment_method = serializers.ChoiceField(choices=[('COD', 'Cash on Delivery')], default='COD')