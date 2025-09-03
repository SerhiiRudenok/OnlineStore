from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group, User
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError, PermissionDenied
from django.db.models import Avg, Q
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from collections import defaultdict

from myapp.models import Product, Category, Comment, Booking, BookingItem, Order, OrderItem, OrderNotification
from myapp.forms import MyUserRegistrationForm, UserPasswordUpdateForm, UserUpdateForm
from myapp.forms import CategoryForm, ProductForm, CommentForm



# --- index
def index_page(req):
    products = Product.objects.filter(is_active=True).order_by('?')[:10]
    enriched_products = []
    for product in products:
        comments = Comment.objects.filter(product=product)
        avg_rating, review_count = get_review_stats(comments)
        enriched_products.append({
            'product': product,
            'average_rating': avg_rating,
            'review_count': review_count,
            'review_count_text': pluralize_reviews(review_count)
        })

    context = {
        'products': enriched_products
    }

    return render(req, 'myapp/index.html', context)



# --- Статистика коментарів та оцінок
def get_review_stats(comments_queryset):
    stats = comments_queryset.aggregate(avg_rating=Avg('rating'))
    average_rating = stats['avg_rating'] or 0.0     # average_rating — обчислює середню оцінку (від 1 до 5) серед усіх коментарів.
    review_count = comments_queryset.count()        # review_count — рахує загальну кількість коментарів по товару.
    return round(average_rating, 1), review_count



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


#  Возвращает правильную форму слова "відгук" в зависимости от количества
def pluralize_reviews(count):

    if count % 10 == 1 and count % 100 != 11:
        return f"{count} відгук"
    elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
        return f"{count} відгуки"
    else:
        return f"{count} відгуків"

class ProductDetailView(DetailView):
    model = Product
    template_name = 'myapp/product/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        user = self.request.user

        # --- Перевірка: чи є товар у кошику поточного користувача
        if user.is_authenticated:
            booking = Booking.objects.filter(user=user).first()
            if booking:
                context['is_in_cart'] = booking.items.filter(product=product).exists()
            else:
                context['is_in_cart'] = False
        else:
            context['is_in_cart'] = False

        # --- Перевірка: чи є товар у списку бажань поточного користувача
        context['is_favorite'] = (
            user.is_authenticated and user in product.favorites.all()
        )

        # --- Відгуки
        comments_queryset = Comment.objects.filter(product=product)
        average_rating, review_count = get_review_stats(comments_queryset)
        context['average_rating'] = average_rating
        context['review_count'] = review_count
        context['review_count_text'] = pluralize_reviews(review_count)

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
        products = context['products']

        enriched_products = []
        for product in products:
            comments_queryset = Comment.objects.filter(product=product)
            average_rating, review_count = get_review_stats(comments_queryset)
            # --- Відгуки
            product.average_rating = average_rating
            product.review_count = review_count
            product.review_count_text = pluralize_reviews(review_count)
            enriched_products.append(product)
        # --- Категорії
        context['products'] = enriched_products
        context['categories'] = Category.objects.all()
        context['selected_category'] = int(self.request.GET['category']) if self.request.GET.get('category', '').isdigit() else 0
        context['selected_sort'] = self.request.GET.get('sort', '')
        return context


class ProductSearchView(ListView):
    model = Product
    template_name = 'myapp/product/product_search.html'
    context_object_name = 'products'

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        category_id = self.request.GET.get('category')
        sort_option = self.request.GET.get('sort')

        queryset = Product.objects.filter(is_active=True)

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        if sort_option == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_option == 'price_desc':
            queryset = queryset.order_by('-price')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        category_id = self.request.GET.get('category', '')
        try:
            context['selected_category'] = int(category_id)
        except (ValueError, TypeError):
            context['selected_category'] = ''
        context['selected_sort'] = self.request.GET.get('sort', '')
        context['categories'] = Category.objects.all()

        # Підрахунок кількості товарів у кожній категорії
        category_counts = defaultdict(int)
        for product in context['products']:
            category_counts[product.category] += 1

        # Сортуємо за назвою категорії
        context['result_categories'] = sorted(category_counts.items(), key=lambda x: x[0].name)
        return context



# --- Booking (Кошик)
class BookingCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        if not product_id:
            return JsonResponse({'success': False, 'error': 'Product ID is missing.'}, status=400)

        product = get_object_or_404(Product, pk=product_id)

        booking, _ = Booking.objects.get_or_create(user=request.user)
        item, created = BookingItem.objects.get_or_create(booking=booking, product=product)

        if not created:
            item.quantity += 1
            item.save()

        return JsonResponse({'success': True, 'total_price': booking.get_total_price()})


class BookingDetailView(LoginRequiredMixin, TemplateView):
    model = Booking
    template_name = 'myapp/booking/booking_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = Booking.objects.filter(user=self.request.user).first()

        if booking:
            items = booking.items.select_related('product')
            cart_items = []
            for item in items:
                cart_items.append({
                    'product': item.product,
                    'quantity': item.quantity,
                    'total': item.quantity * item.product.price,
                })
            context['cart_items'] = cart_items
            context['total_price'] = booking.get_total_price()
        else:
            context['cart_items'] = []
            context['total_price'] = 0

        return context


      # відаляє один товар із кошика
class BookingDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        if not product_id:
            return JsonResponse({'success': False, 'error': 'Product ID is missing.'}, status=400)

        booking = Booking.objects.filter(user=request.user).first()
        if not booking:
            return JsonResponse({'success': False, 'error': 'No booking found.'}, status=404)

        item = booking.items.filter(product_id=product_id).first()
        if item:
            item.delete()

        return JsonResponse({
            'success': True,
            'total_price': booking.get_total_price(),
            'deleted_product_id': product_id
        })


      # зміна кількості товару у кошику (+/-)
class BookingUpdateQuantityView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')

        if not product_id or quantity is None:
            return HttpResponseRedirect(reverse('booking_detail'))

        try:
            quantity = max(1, int(quantity))  # Мінімум 1
        except ValueError:
            return HttpResponseRedirect(reverse('booking_detail'))

        booking = Booking.objects.filter(user=request.user).first()
        if not booking:
            return HttpResponseRedirect(reverse('booking_detail'))

        item = booking.items.filter(product_id=product_id).first()
        if item:
            item.quantity = quantity
            item.save()

        return HttpResponseRedirect(reverse('booking_detail'))


      # повне очищення кошика
class BookingClearView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        booking = Booking.objects.filter(user=request.user).first()
        if booking:
            booking.items.all().delete()

        return HttpResponseRedirect(reverse('booking_detail'))



# --- Order (Замовлення)
class OrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        booking = Booking.objects.filter(user=request.user).first()
        if not booking or not booking.items.exists():
            return render(request, 'myapp/booking/booking_detail.html')

        items = booking.items.select_related('product')
        item_totals = [
            {
                'name': item.product.name,
                'quantity': item.quantity,
                'price': item.product.price,
                'total': item.quantity * item.product.price
            }
            for item in items
        ]

        payment_method = request.GET.get('payment_method', 'cash_on_delivery')
        delivery_method = request.GET.get('delivery_method', 'nova_poshta_branch')
        delivery_address = request.GET.get('delivery_address', '')
        show_card_fields = payment_method == 'card'

        context = {
            'booking': booking,
            'items': item_totals,
            'total_price': booking.get_total_price(),
            'delivery_choices': Order.DELIVERY_CHOICES,
            'payment_choices': Order.PAYMENT_CHOICES,
            'selected_payment_method': payment_method,
            'selected_delivery_method': delivery_method,
            'delivery_address': delivery_address,
            'show_card_fields': show_card_fields,
        }

        return render(request, 'myapp/order/order_create.html', context)

    def post(self, request):
        if request.POST.get('action_type') != 'submit_order':
            return redirect('order_create')

        booking = Booking.objects.filter(user=request.user).first()
        if not booking or not booking.items.exists():
            return redirect('order_create')

        delivery_method = request.POST.get('delivery_method', 'nova_poshta_branch')
        delivery_address = request.POST.get('delivery_address', '')
        payment_method = request.POST.get('payment_method', 'cash_on_delivery')
        show_card_fields = payment_method == 'card'

        if show_card_fields:
            card_number = request.POST.get('card_number', '')
            card_month = request.POST.get('card_month', '')
            card_year = request.POST.get('card_year', '')
            card_cvv = request.POST.get('card_cvv', '')

            if not (card_number.isdigit() and len(card_number) == 16):
                return self._render_with_error(request, booking, "Некоректний номер картки", delivery_method, delivery_address, payment_method)
            if not (card_month.isdigit() and len(card_month) == 2 and 1 <= int(card_month) <= 12):
                return self._render_with_error(request, booking, "Некоректний місяць", delivery_method, delivery_address, payment_method)
            if not (card_year.isdigit() and len(card_year) == 2):
                return self._render_with_error(request, booking, "Некоректний рік", delivery_method, delivery_address, payment_method)
            if not (card_cvv.isdigit() and len(card_cvv) == 3):
                return self._render_with_error(request, booking, "Некоректний CVV", delivery_method, delivery_address, payment_method)

        total_price = booking.get_total_price()
        order = Order(
            user=request.user,
            date=timezone.now(),
            total_price=total_price,
            delivery_method=delivery_method,
            delivery_address=delivery_address,
            payment_method=payment_method
        )

        try:
            order.full_clean()
        except ValidationError as e:
            return self._render_with_error(
                request,
                booking,
                error_message=e.messages[0],  # показує перше повідомлення
                delivery_method=delivery_method,
                delivery_address=delivery_address,
                payment_method=payment_method
            )

        order.save()

        for item in booking.items.select_related('product'):
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        booking.items.all().delete()

        return redirect(f"{reverse('order_confirm', args=[order.id])}?success=1")

    def _render_with_error(self, request, booking, error_message, delivery_method, delivery_address, payment_method):
        items = booking.items.select_related('product')
        item_totals = [
            {
                'name': item.product.name,
                'quantity': item.quantity,
                'price': item.product.price,
                'total': item.quantity * item.product.price
            }
            for item in items
        ]
        context = {
            'booking': booking,
            'items': item_totals,
            'total_price': booking.get_total_price(),
            'delivery_choices': Order.DELIVERY_CHOICES,
            'payment_choices': Order.PAYMENT_CHOICES,
            'selected_payment_method': payment_method,
            'selected_delivery_method': delivery_method,
            'delivery_address': delivery_address,
            'show_card_fields': payment_method == 'card',
            'error_message': error_message,
        }
        return render(request, 'myapp/order/order_create.html', context)


class OrderConfirmView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        # для взаємодії двох сторінок: order_notification та order_confirm
        came_from_order_notification = request.GET.get('from_notification') == '1'
        # доступ дозволено власнику або менеджеру
        is_manager = request.user.groups.filter(name='Manager').exists()
        if order.user != request.user and not is_manager:
            raise PermissionDenied("У вас немає доступу до цього замовлення.")

        items_with_total = []
        for item in order.items.all():
            total = item.price * item.quantity
            items_with_total.append({
                'product': item.product,
                'quantity': item.quantity,
                'price': item.price,
                'total': total,
            })

        show_success_message = request.GET.get('success') == '1'

        context = {
            'order': order,
            'order_items': items_with_total,
            'show_success_message': show_success_message,
            'came_from_order_notification': came_from_order_notification,
        }
        return render(request, 'myapp/order/order_confirm.html', context)


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'myapp/order/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-date')


      # --- Сигнал Менеджеру про нове Замовлення
class OrderNotificationView(LoginRequiredMixin, View):
    def get(self, request):
        filter_value = request.GET.get('filter')

        # всі сповіщення
        notifications_all = request.user.user_notifications.all()
        unread_count = notifications_all.filter(is_read=False).count()
        read_count = notifications_all.filter(is_read=True).count()
        total_count = notifications_all.count()

        # фільтр для відображення
        if filter_value == 'read':
            notifications = notifications_all.filter(is_read=True)
        elif filter_value == 'all':
            notifications = notifications_all
        else:
            filter_value = 'unread'
            notifications = notifications_all.filter(is_read=False)

        notifications = notifications.order_by('-created_at')

        return render(request, 'myapp/order/order_notification.html', {
            'notifications': notifications,
            'notifications_all': notifications_all,
            'filter_value': filter_value,
            'unread_count': unread_count,
            'read_count': read_count,
            'total_count': total_count
        })

    def post(self, request):
        notification_id = request.POST.get('notification_id')
        if notification_id:
            notification = request.user.user_notifications.filter(pk=notification_id).first()
            if notification and not notification.is_read:
                notification.is_read = True
                notification.save()
        return redirect(request.path)



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

    # кількість коментарів кожного користувача 'user_comments_count'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['user_comments_count'] = Comment.objects.filter(user=user).count()
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


# кнопка "Улюблений товар (favorites)"
class ProductFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        if product.favorites.filter(id=request.user.id).exists():
            product.favorites.remove(request.user)
        else:
            product.favorites.add(request.user)

        fallback_url = reverse('product_detail', kwargs={'pk': pk})
        return redirect(request.META.get('HTTP_REFERER', fallback_url))


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


# --- Comment
class CommentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'myapp/comment/comment_create.html'
    permission_required = 'myapp.add_comment'

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, pk=kwargs['pk'])

        if Comment.objects.filter(product=self.product, user=request.user).exists():
            return HttpResponse(status=204)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context

    def form_valid(self, form):
        form.instance.product = self.product
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('product_detail', kwargs={'pk': self.product.pk})


class CommentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'myapp/comment/comment_update.html'
    context_object_name = 'comment'
    permission_required = 'myapp.change_comment'

    def get_success_url(self):
        return reverse_lazy('product_detail', kwargs={'pk': self.object.product.pk})


class CommentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Comment
    template_name = 'myapp/comment/comment_delete.html'
    context_object_name = 'comment'
    permission_required = 'myapp.delete_comment'

    def has_permission(self):
        comment = self.get_object()
        user = self.request.user
        is_manager = user.groups.filter(name='Manager').exists()
        return comment.user == user or is_manager

    def get_success_url(self):
        return reverse_lazy('product_detail', kwargs={'pk': self.object.product.pk})


    # список всіх коментарів конкретного товару
class CommentListView(ListView):
    model = Comment
    template_name = 'myapp/comment/comment_list.html'
    context_object_name = 'comments'

    def get_queryset(self):
        self.product = get_object_or_404(Product, pk=self.kwargs.get('pk'))
        return Comment.objects.filter(product=self.product).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = context['comments']

        average_rating, review_count = get_review_stats(comments)

        user = self.request.user
        has_commented = False
        user_comment = None
        is_manager = False

        if user.is_authenticated:
            user_comment = comments.filter(user=user).first()
            has_commented = user_comment is not None
            is_manager = user.groups.filter(name='Manager').exists()

        context.update({
            'product': self.product,
            'average_rating': average_rating,
            'review_count': review_count,
            'has_commented': has_commented,
            'user_comment': user_comment,
            'is_manager': is_manager,
        })
        return context
