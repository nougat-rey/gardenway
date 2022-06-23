from rest_framework import serializers
from decimal import Decimal
from .models import *


class ProductImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id, **validated_data)

    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductSerializer(serializers.ModelSerializer):
    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')
    price = serializers.DecimalField(
        max_digits=6, decimal_places=2, source='unit_price')
    images = ProductImageSerializer(many=True, read_only=True)

    def calculate_tax(self, product):
        return product.unit_price*Decimal(1.1)

    class Meta:
        model = Product
        fields = ['id', 'title', 'slug',
                  'inventory', 'price', 'price_with_tax', 'collections', 'images']


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count', 'products']

    products_count = serializers.IntegerField(read_only=True)


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'customer', 'items', 'total_price']
