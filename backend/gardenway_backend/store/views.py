from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Collection, Product
from .serializers import CollectionSerializer, ProductSerializer
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404

# TODO: Convert to class-based views


@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        queryset = Product.objects.all()
        serializer = ProductSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def product_detail(request, id):
    if request.method == 'GET':
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    elif request.method == 'PUT' or request.method == 'PATCH':
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        product = get_object_or_404(Product, pk=id)
        if product.orderitem_set.count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item.'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def collection_list(request):
    if request.method == 'GET':
        queryset = Collection.objects.annotate(
            products_count=Count('products'))
        serializer = CollectionSerializer(queryset, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@ api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def collection_detail(request, pk):
    collection = get_object_or_404(
        Collection.objects.annotate(
            products_count=Count('products')), pk=pk)
    if request.method == 'GET':
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)
    elif request.method == 'PUT' or request.method == 'PATCH':
        serializer = CollectionSerializer(collection, data=request)
        serializer.is_valid(raise_exception=True)
        serializer.save()
    elif request.method == 'DELETE':
        if collection.products.count() > 0:
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
