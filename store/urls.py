from .views import *
from rest_framework_nested import routers
from django.conf.urls.static import static
from settings.common import MEDIA_URL, MEDIA_ROOT

router = routers.DefaultRouter()
router.register('products', ProductViewSet)
router.register('collections', CollectionViewSet)
router.register('promotions', PromotionViewSet)
router.register('carts', CartViewSet)
router.register('orders', OrderViewSet)
router.register('customers', CustomerViewSet)

products_router = routers.NestedDefaultRouter(
    router, 'products', lookup='product')
products_router.register(
    'images', ProductImageViewSet, basename='product-images')
products_router.register(
    'reviews', ProductReviewViewSet, basename='product-reviews')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + products_router.urls + carts_router.urls
if settings.DEBUG:
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)