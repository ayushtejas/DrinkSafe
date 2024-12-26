from django.urls import path

from products import views

app_name = 'products'

urlpatterns = [

    path('products/', views.ProductViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='product-list'),

    path('products/<uuid:uuid>/', views.ProductViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='product-detail'),
]
