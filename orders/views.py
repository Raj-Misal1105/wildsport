from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Order, OrderItem
from .serializers import OrderSerializer, CheckoutSerializer
from cart.models import Cart


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout(request):
    serializer = CheckoutSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    if not cart_items.exists():
        return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

    
    for item in cart_items:
        if item.product.stock < item.quantity:
            return Response(
                {"error": f"'{item.product.name}' has only {item.product.stock} left in stock"},
                status=status.HTTP_400_BAD_REQUEST
            )

    with transaction.atomic():   
        order = Order.objects.create(
            user=request.user,
            total_amount=cart.total_price,
            payment_method=serializer.validated_data.get('payment_method', 'COD'),
            shipping_address=serializer.validated_data['shipping_address']
        )

        for item in cart_items:
            price = item.product.discount_price or item.product.price
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_purchase=price,
                selected_size=item.selected_size
            )
            
            item.product.stock -= item.quantity
            item.product.save()

        cart_items.delete()   

    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    serializer = OrderSerializer(order)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status in ['shipped', 'delivered', 'cancelled']:
        return Response({"error": f"Order already {order.status}, cannot cancel"}, status=status.HTTP_400_BAD_REQUEST)

    order.status = 'cancelled'
    order.save()

    
    for item in order.items.all():
        if item.product:
            item.product.stock += item.quantity
            item.product.save()

    return Response(OrderSerializer(order).data)