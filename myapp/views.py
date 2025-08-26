from django.shortcuts import render
from .models import Product

def index_page(req):
    products = Product.objects.filter(is_active=True).all()
    context = {
        'products': products
    }
    return render(req, 'myapp/template.html', context)

def product_detail_page_placeholder(request, product_id):
    return render(request, 'myapp/product_detail.html')

