from django.urls import path
from .views import test_view, ProductDetailView

urlpatterns = [
    path('', test_view, name='base'),
    # строим url по категории и slug товара
    path('products/<str:ct_model>/<str:slug>/', ProductDetailView.as_view(), name='product_detail')
]
