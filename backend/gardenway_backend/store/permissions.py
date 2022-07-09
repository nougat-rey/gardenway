from re import T
from rest_framework import permissions
from .serializers import OrderSerializer, CartSerializer
from .models import Order, Cart


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        return bool(request.user and request.user.is_staff)


class IsAdminOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        print(request)
        if request.user.is_staff:
            return True
        elif request.method in ['OPTIONS', 'HEAD']:
            return True
        elif request.method == 'GET':
            if type(obj) is Cart:
                return (request.user.id == CartSerializer(obj).data['customer'])
            elif type(obj) is Order:
                return (request.user.id == OrderSerializer(obj).data['customer'])
        return False
