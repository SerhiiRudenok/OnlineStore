from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_page, name='index_page'),

    # Booking
    path('booking/create/', views.BookingCreateView.as_view(), name='booking_create'),
    path('booking/detail/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('booking/delete/', views.BookingDeleteView.as_view(), name='booking_delete'),
    path('booking/update/', views.BookingUpdateQuantityView.as_view(), name='booking_update_quantity'),
    path('booking/clear/', views.BookingClearView.as_view(), name='booking_clear'),

    # User
    path('profile/', views.UserDetailView.as_view(), name='profile_user'),
    path('user/profile/update/', views.UserUpdateView.as_view(), name='profile_update'),
    path('user/password/update/', views.UserPasswordUpdateView.as_view(), name='password_update'),
    path('user/comments/', views.UserCommentsListView.as_view(), name='user_comments'),
    path('user/favorites/', views.UserFavoritesListView.as_view(), name='user_favorites'),

    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/confirm/', views.ConfirmLogoutView.as_view(), name='confirm_logout'),

    # Category
    path('category/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('category/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('category/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    path('category/all', views.CategoryListView.as_view(), name='category_list'),

    # Product
    path('product/create/', views.ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    path('product/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('product/<int:pk>/favorite/', views.ProductFavoriteView.as_view(), name='favorite_product'),
    path('search/', views.ProductSearchView.as_view(), name='product_search'),

    # Comment
    path('product/<int:pk>/comment/create/', views.CommentCreateView.as_view(), name='comment_create'),
    path('comment/<int:pk>/update/', views.CommentUpdateView.as_view(), name='comment_update'),
    path('comment/<int:pk>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
    path('product/<int:pk>/comments/', views.CommentListView.as_view(), name='comment_list'),

    # Order
    path('order/create/', views.OrderCreateView.as_view(), name='order_create'),
    path('order/confirm/<int:order_id>/', views.OrderConfirmView.as_view(), name='order_confirm'),
    path('order/list/', views.OrderListView.as_view(), name='order_list'),
    path('order/notifications/', views.OrderNotificationView.as_view(), name='order_notification'),

]