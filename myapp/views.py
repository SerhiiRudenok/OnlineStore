from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group, User
from django.contrib.auth import login, logout
from django.views.generic import TemplateView, View, ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse

from myapp.models import Product, Category, Comment
from myapp.forms import MyUserRegistrationForm, UserPasswordUpdateForm, UserUpdateForm
from myapp.forms import CategoryForm, ProductForm



# --- index
def index_page(req):
    products = Product.objects.filter(is_active=True).order_by('?')[:10]
    context = {
        'products': products
    }
    return render(req, 'myapp/index.html', context)





# --- Category
class CategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'myapp/category/category_create.html'
    permission_required = 'myapp.add_category'
    success_url = reverse_lazy('category_list')


class CategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'myapp/category/category_update.html'
    permission_required = 'myapp.change_category'
    success_url = reverse_lazy('category_list')


class CategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Category
    template_name = 'myapp/category/category_delete.html'
    permission_required = 'myapp.delete_category'
    success_url = reverse_lazy('category_list')


class CategoryListView(ListView):
    model = Category
    template_name = 'myapp/category/category_list.html'
    context_object_name = 'categories'




# --- Product
class ProductCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'myapp/product/product_create.html'
    permission_required = 'myapp.add_product'

    def get_success_url(self):
        return reverse_lazy('product_detail', kwargs={'pk': self.object.pk})


class ProductUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'myapp/product/product_update.html'
    context_object_name = 'product'
    permission_required = 'myapp.change_product'

    def get_success_url(self):
        return reverse_lazy('product_detail', kwargs={'pk': self.object.pk})


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


class ProductDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Product
    template_name = 'myapp/product/product_delete.html'
    context_object_name = 'product'
    permission_required = 'myapp.delete_product'
    success_url = reverse_lazy('product_list')



class ProductListView(ListView):
    model = Product
    template_name = 'myapp/product/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        category_id = self.request.GET.get('category')
        sort_order = self.request.GET.get('sort')

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if sort_order == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_order == 'price_desc':
            queryset = queryset.order_by('-price')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = int(self.request.GET['category']) if self.request.GET.get('category', '').isdigit() else 0
        context['selected_sort'] = self.request.GET.get('sort', '')
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
        if request.user.is_authenticated:
            return redirect(reverse('index'))

        form = AuthenticationForm()
        return render(request, 'myapp/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(reverse('index'))
        else:
            return render(request, 'myapp/login.html', {'form': form})




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
        return reverse_lazy('profile_user')

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user



class UserPasswordUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserPasswordUpdateForm
    template_name = 'myapp/user/password_update.html'

    def get_success_url(self):
        return reverse_lazy('profile_user')

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



class ProductFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.favorites.filter(id=request.user.id).exists():
            product.favorites.remove(request.user)
        else:
            product.favorites.add(request.user)
        return redirect('product_detail', pk=pk)


# список всіх улюблених товарів
class UserFavoritesListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'myapp/user/user_favorites.html'
    context_object_name = 'favorite_product'
    paginate_by = 10

    def get_queryset(self):
        self.profile_user = self.request.user
        return self.profile_user.favorite_product.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.profile_user
        return context


