from django.contrib import admin
from django.db.models.aggregates import Count
from . import models


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'unit_price',
                    'inventory_status']
    list_editable = ['unit_price']
    list_per_page = 10

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory == 0:
            return 'Empty'
        elif product.inventory < 10:
            return 'Low'
        else:
            return 'Ok'


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        return collection.products_count

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count('product'))


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']


@admin.register(models.Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['description', 'discount']
