from products.models import Products
from rest_framework import serializers

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['uuid', 'name', 'description', 'quantity', 'price',
                 'created', 'modified', 'is_active']
        read_only_fields = ['uuid', 'created', 'modified']