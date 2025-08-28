from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group, User
from django.contrib.auth import login, logout
from django.views.generic import TemplateView, View, ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm

from myapp.models import Product, Category, Comment
from myapp.forms import MyUserRegistrationForm, UserPasswordUpdateForm, UserUpdateForm



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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.request.session.get('cart', [])

        # Проверяем, есть ли текущий товар в корзине
        context['is_in_cart'] = str(self.object.id) in cart

        return context




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
        cart = self.request.session.get('cart', [])
        cart_items = []

        #все ID товаров из списка
        product_ids = [int(product_id) for product_id in cart]
        products = Product.objects.in_bulk(product_ids)

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

        cart = request.session.get('cart', [])
        cart.append(str(product_id))
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

        # Добавляем product_id в JSON-ответ
        return JsonResponse({'success': True, 'total_price': total_price, 'deleted_product_id': product_id})






# --- Login
class LoginView(View):
    def get(self, request):
        # We need to pass the forms to the template for initial rendering
        login_form = AuthenticationForm()
        register_form = MyUserRegistrationForm()
        context = {
            'login_form': login_form,
            'register_form': register_form
        }
        return render(request, 'myapp/login.html', context)

    def post(self, request):
        if 'login_submit' in request.POST:
            login_form = AuthenticationForm(data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return JsonResponse({'success': True, 'redirect_url': '/'})
            else:
                return JsonResponse({'success': False, 'errors': login_form.errors})

        elif 'register_submit' in request.POST:
            register_form = MyUserRegistrationForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                hr_group = Group.objects.get(name='Client')
                user.groups.add(hr_group)
                login(request, user)
                return JsonResponse({'success': True, 'redirect_url': '/'})
            else:
                return JsonResponse({'success': False, 'errors': register_form.errors})

        return JsonResponse({'success': False, 'error': 'Invalid request'})

# --- Register
class RegisterView(View):
    def get(self, request):
        form = MyUserRegistrationForm()
        context = {
            'form': form
        }
        return render(request, 'myapp/register.html', context)

    def post(self, request):
        form = MyUserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            hr_group = Group.objects.get(name='Client')
            user.groups.add(hr_group)

            login(request, user)
            return redirect('index')

        return render(request, 'myapp/register.html', {'form': form})


class ConfirmLogoutView(LoginRequiredMixin, View):
    template_name = 'myapp/user/confirm_logout.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        logout(request)
        return redirect('index')


# --- User
class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'myapp/user/profile.html'
    context_object_name = 'profile_user'

    def get_object(self, queryset=None):
        return self.request.user

    # кількість коментарів кожного користувача 'comments_count'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['comments_count'] = Comment.objects.filter(user=user).count()
        return context



class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'myapp/user/profile_update.html'

    def get_success_url(self):
        return reverse_lazy('profile_user', kwargs={'user_id': self.request.user.id})

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user



class UserPasswordUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserPasswordUpdateForm
    template_name = 'myapp/user/password_update.html'

    def get_success_url(self):
        return reverse_lazy('profile_user', kwargs={'user_id': self.request.user.id})

    def get_object(self, queryset=None):
        return self.request.user

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


# список всіх коментарів користувача
class UserCommentsListView(LoginRequiredMixin, ListView):
    model = Comment
    template_name = 'myapp/user/user_comments.html'
    context_object_name = 'comments'
    paginate_by = 10

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user).select_related('product')



# список всіх улюблених товарів
class UserFavoritesListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'myapp/user/user_favorites.html'
    context_object_name = 'favorite_products'
    paginate_by = 10

    def get_queryset(self):
        self.profile_user = self.request.user
        return self.profile_user.favorite_product.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.profile_user
        return context


