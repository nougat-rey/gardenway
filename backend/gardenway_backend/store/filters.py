from django_filters.rest_framework import FilterSet
from .models import Product, Order


class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            'unit_price': ['gt', 'lt'],
            'collections': ['exact'],
            'promotions': ['exact']
        }


class OrderFilter(FilterSet):
    class Meta:
        model = Order
        fields = {
            'payment_status': ['exact'],
            'customer_id': ['exact']
        }
