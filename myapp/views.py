from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Product

from .models import Product

# --- index
def index_page(req):
    products = Product.objects.filter(is_active=True).all()
    context = {
        'products': products
    }
    return render(req, 'myapp/template.html', context)


# --- Category
class CategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    pass

