from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_page, name='index_page'),
    path('product/<int:product_id>/', views.product_detail_page_placeholder, name='product_detail'),
]