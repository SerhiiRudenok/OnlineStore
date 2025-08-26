from django.urls import path

from myapp.views import CategoryCreateView


# Локальний маршрут
urlpatterns = [
    # --- category
    path('category/create/', CategoryCreateView.as_view(), name='category_create'),
    # path('category/<int:pk>/update', CategoryUpdateView.as_view(), name='category_update'),
    # path('category/<int:pk>/delete', CategoryDeleteView.as_view(), name='category_delete'),
    # path('category/<int:pk>/view', CategoryDetailView.as_view(), name='category_detail'),
    # path('category/list', CategoryListView.as_view(), name='category_list'),

    # --- product
    # path('product/<int:category_id>/create/', ProductCreateView.as_view(), name='product_create'),
    # path('product/<int:product_id>/update', ProductUpdateView.as_view(), name='product_update'),
    # path('product/<int:product_id>/delete', ProductDeleteView.as_view(), name='product_delete'),
    # path('product/<int:product_id>/view', ProductDetailView.as_view(), name='product_detail'),
    # path('product/<int:category_id>/list', ProductListView.as_view(), name='product_list'),


]
