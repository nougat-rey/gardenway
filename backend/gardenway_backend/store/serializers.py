from rest_framework import serializers
from decimal import Decimal
from .models import *


class ProductSerializer(serializers.ModelSerializer):
    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')
    price = serializers.DecimalField(
        max_digits=6, decimal_places=2, source='unit_price')

    def calculate_tax(self, product):
        return product.unit_price*Decimal(1.1)

    class Meta:
        model = Product
        fields = ['id', 'title', 'slug',
                  'inventory', 'price', 'price_with_tax', 'collections']


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count', 'products']

    products_count = serializers.IntegerField(read_only=True)
