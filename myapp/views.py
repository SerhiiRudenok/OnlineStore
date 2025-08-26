from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from myapp.models import Product, Category



# --- index
def index_page(req):
    products = Product.objects.filter(is_active=True).all()
    context = {
        'products': products
    }
    return render(req, 'myapp/template.html', context)


def product_detail_page_placeholder(request, product_id):
    return render(request, 'myapp/product_detail.html')


# --- Category
class CategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Category
    # form_class = CategoryForm
    template_name = 'myapp/category/category_create.html'
    permission_required = 'myapp.add_category'




# --- Product
class ProductCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Product
    # form_class = ProductForm
    fields = ['name', 'category', 'description', 'price', 'image']
    template_name = 'myapp/product/product_create.html'
    permission_required = 'myapp.add_product'