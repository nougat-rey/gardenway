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


class ProductReviewSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductReview.objects.create(product_id=product_id, **validated_data)

    class Meta:
        model = ProductReview
        fields = ['product', 'name', 'description', 'date']


class ProductSerializer(serializers.ModelSerializer):
    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')
    price = serializers.DecimalField(
        max_digits=6, decimal_places=2, source='unit_price')
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)

    def calculate_tax(self, product):
        return product.unit_price*Decimal(1.1)

    class Meta:
        model = Product
        fields = ['id', 'title', 'slug',
                  'inventory', 'price', 'price_with_tax', 'collections', 'images', 'reviews']


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count', 'products']

    products_count = serializers.IntegerField(read_only=True)
