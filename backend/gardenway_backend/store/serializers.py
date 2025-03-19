from rest_framework import serializers
from decimal import Decimal
from .models import *
from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer
from django.db import transaction
from signals import order_created

TAX = 1.13


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = ['id', 'username', 'password',
                  'email', 'first_name', 'last_name']


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()

    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone']


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']


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
        fields = ['product', 'rating', 'name', 'description', 'date']


class ProductSerializer(serializers.ModelSerializer):
    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')
    price = serializers.DecimalField(
        max_digits=6, decimal_places=2, source='unit_price')
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)

    def calculate_tax(self, product):
        return round(product.unit_price*Decimal(TAX), 2)

    class Meta:
        model = Product
        fields = ['id', 'title', 'slug',
                  'inventory', 'price', 'price_with_tax', 'images', 'reviews']


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'slug', 'products_count', 'products']

    products_count = serializers.IntegerField(read_only=True)


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()
    total_price_with_tax = serializers.SerializerMethodField()

    def get_total_price(self, cart_item):
        return round(cart_item.quantity * cart_item.product.unit_price, 2)

    def get_total_price_with_tax(self, cart_item):
        return round(self.get_total_price(cart_item)*Decimal(TAX), 2)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity',
                  'total_price', 'total_price_with_tax']


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_price_with_tax = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return round(sum([item.quantity * item.product.unit_price for item in cart.items.all()]), 2)

    def get_total_price_with_tax(self, cart):
        return round(self.get_total_price(cart)*Decimal(TAX), 2)

    class Meta:
        model = Cart
        fields = ['id', 'customer', 'items', 'total_price',
                  'total_price_with_tax', 'created_at']


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                'No product with the given ID was found')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(
                cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            # Create a new one
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)
        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()
    total_price_with_tax = serializers.SerializerMethodField()

    def get_total_price(self, order_item):
        return round(order_item.quantity * order_item.product.unit_price, 2)

    def get_total_price_with_tax(self, order_item):
        return round(self.get_total_price(order_item)*Decimal(TAX), 2)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity',
                  'total_price', 'total_price_with_tax']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total_price = serializers.SerializerMethodField()
    total_price_with_tax = serializers.SerializerMethodField()

    def get_total_price(self, order):
        return round(sum([item.quantity * item.product.unit_price for item in order.items.all()]), 2)

    def get_total_price_with_tax(self, order):
        return round(self.get_total_price(order)*Decimal(TAX), 2)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status',
                  'items', 'total_price', 'total_price_with_tax']


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def save(self, **kwargs):
        with transaction.atomic():
            (customer, created) = Customer.objects.get_or_create(
            id=self.context['user_id'])
            cart_id = self.validated_data['cart_id']
            order = Order.objects.create(customer=customer)
            cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)
            order_items = [
    							OrderItem(
    								order=order,
    								product=item.product,
    								unit_price=item.product.unit_price,
    								quantity=item.quantity
    							) for item in cart_items
    			]
            OrderItem.objects.bulk_create(order_items) 
            Cart.objects.filter(pk=cart_id).delete()
            order_created.send_robust(self.__class__, order-order)
        return order
    
    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError(
                'No cart with the given ID was found')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('The cart is empty')
        return cart_id


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = ['id', 'title', 'slug', 'description', 'discount', 'products']
