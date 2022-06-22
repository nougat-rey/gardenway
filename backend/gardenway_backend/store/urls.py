from . import views
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet)
router.register('collections', views.CollectionViewSet)

products_router = routers.NestedDefaultRouter(
    router, 'products', lookup='product')
products_router.register(
    'images', views.ProductImageViewSet, basename='product-images')
products_router.register(
    'reviews', views.ProductReviewViewSet, basename='product-reviews')

urlpatterns = router.urls + products_router.urls
