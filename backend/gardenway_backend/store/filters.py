from re import I
from django_filters.rest_framework import FilterSet
from .models import Product, Order, Cart, ProductReview, Promotion


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
            'customer_id': ['exact'],
            'placed_at': ['gt', 'lt']
        }


class CartFilter(FilterSet):
    class Meta:
        model = Cart
        fields = {
            'customer': ['exact'],
            'created_at': ['gt', 'lt']
        }


class ProductReviewFilter(FilterSet):
    class Meta:
        model = ProductReview
        fields = {
            'rating': ['gt'],
            'date': ['gt', 'lt']
        }


class PromotionFilter(FilterSet):
    class Meta:
        model = Promotion
        fields = {
            'discount': ['gt', 'lt']
        }
