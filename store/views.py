from django.db import IntegrityError
from django.db.models.aggregates import Count
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from .permissions import IsAdminOrReadOnly, IsAdminOrOwner
from .models import *
from .serializers import *
from .filters import *
import logging
logger = logging.getLogger(__name__)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related(
        'images', 'reviews').order_by('title').all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = ProductFilter
    search_fields = ['title', 'description']
    ordering_fields = ['slug', 'unit_price', 'last_update']

    def get_serializer_context(self):
        return{'request': self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item.'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.prefetch_related(
        'products').annotate(products_count=Count('products')).all().order_by('id')
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['title']
    ordering_fields = ['slug']


class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])


class ProductReviewViewSet(ModelViewSet):
    serializer_class = ProductReviewSerializer
    filterset_class = ProductReviewFilter
    search_fields = ['name', 'description']
    ordering_fields = ['rating']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

    def get_queryset(self):
        return ProductReview.objects.filter(
            product_id=self.kwargs['product_pk'])


class CartViewSet(ModelViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer
    filterset_class = CartFilter
    ordering_fields = ['created_at']

    def get_permissions(self):
        if self.action == 'list' or self.action == 'destroy':
            return [IsAdminUser()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        elif self.action == 'retrieve':
            return [IsAdminOrOwner()]
        return [IsAdminUser()]


class CartItemViewSet(ModelViewSet):

    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.prefetch_related('items__product').all()
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    filterset_class = OrderFilter
    ordering_fields = ['placed_at']

    def get_permissions(self):
        if self.action == 'list' or self.action == 'destroy':
            return [IsAuthenticated()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        elif self.action == 'retrieve':
            return [IsAdminOrOwner()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        user = self.request.user

        if self.action == 'list' and not user.is_staff:
            # Non-admins should only see their own orders in list view
            return Order.objects.filter(customer__user=user).prefetch_related('items__product')

        # For retrieve, admins and non-admins need access to the object so permission can be applied
        return Order.objects.prefetch_related('items__product')


    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        if self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        if self.request.user.id:

            serializer = CreateOrderSerializer(data=request.data, context={
                'user_id': self.request.user.id})
            try:
                serializer.is_valid(raise_exception=True)
            
            except ValidationError as e:
                return Response(
                    {'error': 'Invalid Cart ID, Cart not found or Cart is empty.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            try:
                # Retrieve the Cart object
                cart = Cart.objects.get(id=request.data['cart_id'])
            except Cart.DoesNotExist:
                return Response(
                    {'error': 'Cart not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Check if the cart belongs to the authenticated user
            logger.info(f"Requesting user: {self.request.user}")
            logger.info(f"Owner of cart: {cart.customer.user}")
            if cart.customer.user != request.user:
                return Response(
                    {'error': 'You can only create orders for your own cart.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            order = serializer.save()

            serializer = OrderSerializer(order)
            response = Response(
                serializer.data, status=status.HTTP_201_CREATED)
        else:
            # anonymous user does not have a user id to add to the request
            response = Response({'error': 'Anonymous user cannot create an order.'},
                                status=status.HTTP_403_FORBIDDEN)
        return response


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        try:
            serializer = CustomerSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response(
                serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            response = Response(
                {'error': f'Cannot create customer for user {request.data["user_id"]} - either associated user is already connected to a customer or associated user does not exist'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return response

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        (customer, created) = Customer.objects.get_or_create(
            user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class PromotionViewSet(ModelViewSet):
    queryset = Promotion.objects.prefetch_related('products').all()
    serializer_class = PromotionSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = PromotionFilter
    search_fields = ['description']
    ordering_fields = ['discount']
