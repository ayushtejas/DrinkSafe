from products.models import Products
from products.permissions import IsAdminOrReadOnly
from products.serializers import ProductSerializer
from rest_framework import viewsets, permissions

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Products.objects.all()
    permission_classes = [IsAdminOrReadOnly,permissions.IsAuthenticated]
    lookup_field = 'uuid'
    ordering = ['-created']

    def perform_destroy(self,instance):
        instance.is_active = False
        instance.save()
