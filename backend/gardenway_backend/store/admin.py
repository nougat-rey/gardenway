from django.contrib import admin, messages
from django.db.models.aggregates import Count
from . import models
from django.utils.html import format_html


class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low'),
            ('0', 'Empty')
        ]

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(inventory=0)
        elif self.value() == '<10':
            return queryset.filter(inventory__lt=10)


@admin.register(models.ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['pk', 'image', 'product']
    list_per_page = 10
    ordering = ['pk']


class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    readonly_fields = ['thumbnail']

    def thumbnail(self, instance):
        if instance.image.name != '':
            return format_html(f'<img src="{instance.image.url}" class="thumbnail"/>')
        return ''


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'unit_price',
                    'inventory_status']
    list_editable = ['unit_price']
    list_per_page = 10
    list_filter = ['last_update', InventoryFilter]
    actions = ['clear_inventory']
    search_fields = ['title']
    prepopulated_fields = {
        'slug': ['title']
    }
    inlines = [ProductImageInline]

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory == 0:
            return 'Empty'
        elif product.inventory < 10:
            return 'Low'
        else:
            return 'Ok'

    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request, f'{updated_count} products were successfully updated', messages.ERROR)

    class Media:
        css = {
            'all': ['static_store/styles.css']
        }


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    list_per_page = 10
    search_fields = ['title']
    prepopulated_fields = {
        'slug': ['title']
    }

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        return collection.products_count

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count('products'))


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone']
    list_per_page = 10
    search_fields = ['first_name__istartswith', 'last_name__istartswith']


class PromotionFilter(admin.SimpleListFilter):
    title = 'promotion'
    parameter_name = 'promotion'

    def lookups(self, request, model_admin):
        return [
            (f'<{10+1}', 'Small Sale'),
            (f'<{25+1}', 'Medium Sale'),
            ('<100', 'Huge Sale')
        ]

    def queryset(self, request, queryset):
        if self.value() == f'<{10+1}':
            return queryset.filter(discount__lt=10+1)
        elif self.value() == f'<{25+1}':
            return queryset.filter(discount__lt=50+1).filter(discount__gt=10)

        elif self.value() == '<100':
            return queryset.filter(discount__lt=100).filter(discount__gt=50)


@ admin.register(models.Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['description', 'discount']
    list_per_page = 10
    list_filter = [PromotionFilter]
    search_fields = ['description']


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    min_num = 1
    max_num = 100
    model = models.OrderItem


@ admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
    list_display = ['id', 'placed_at', 'customer']
    list_per_page = 10
    list_filter = ['placed_at']
    search_field = ['customer']


class CartItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    min_num = 1
    max_num = 100
    model = models.CartItem


@ admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [CartItemInline]
    list_display = ['id', 'created_at', 'customer']
    list_per_page = 10
    list_filter = ['created_at']
    search_field = ['customer']


@admin.register(models.Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['customer_id', 'street', 'city']
    list_per_page = 10
