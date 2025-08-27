from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView, View
from django.http import JsonResponse

from myapp.models import Product, Category


# --- index
def index_page(req):
    products = Product.objects.filter(is_active=True).all()
    context = {
        'products': products
    }
    return render(req, 'myapp/index.html', context)




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

class ProductDetailView(DetailView):
    model = Product
    template_name = 'myapp/product/product_detail.html'
    context_object_name = 'product'


# Вспомогательная функция для расчета общей стоимости
def get_cart_total_price(request):
    cart = request.session.get('cart', [])  # Корзина - это список
    total_price = 0
    # Получаем все ID товаров из списка
    product_ids = [int(product_id) for product_id in cart]
    # За один запрос получаем все объекты Product
    products = Product.objects.in_bulk(product_ids)
    for product_id_str in cart:
        product = products.get(int(product_id_str))
        if product:
            total_price += product.price
    return total_price


# --- Booking
class BookingDetailView(TemplateView):
    template_name = 'myapp/booking/booking_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('cart', [])  # Корзина - это список
        cart_items = []

        # Получаем все ID товаров из списка
        product_ids = [int(product_id) for product_id in cart]
        # За один запрос получаем все объекты Product
        products = Product.objects.in_bulk(product_ids)

        # Формируем список товаров для шаблона
        for product_id_str in cart:
            product = products.get(int(product_id_str))
            if product:
                cart_items.append({
                    'product': product,
                })

        context['cart_items'] = cart_items
        context['total_price'] = get_cart_total_price(self.request)
        return context


class BookingCreateView(View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')

        if product_id is None:
            return JsonResponse({'success': False, 'error': 'Product ID is missing.'}, status=400)

        cart = request.session.get('cart', [])  # Корзина - это список

        cart.append(str(product_id))  # Добавляем каждый товар как отдельный элемент

        request.session['cart'] = cart
        total_price = get_cart_total_price(request)
        return JsonResponse({'success': True, 'total_price': total_price})


class BookingDeleteView(View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')

        if product_id is None:
            return JsonResponse({'success': False, 'error': 'Product ID is missing.'}, status=400)

        cart = request.session.get('cart', [])

        # Создаем новый список, исключая все вхождения удаляемого товара
        updated_cart = [item for item in cart if item != str(product_id)]

        request.session['cart'] = updated_cart
        total_price = get_cart_total_price(request)
        return JsonResponse({'success': True, 'total_price': total_price})