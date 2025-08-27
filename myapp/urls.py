from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_page, name='index_page'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),

    # Booking
    path('booking/create/', views.BookingCreateView.as_view(), name='booking_create'),
    path('booking/detail/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('booking/delete/', views.BookingDeleteView.as_view(), name='booking_delete'),

    # ---users
    path('profile/', views.UserDetailView.as_view(), name='profile_user'),
    path('user/profile/update/', views.UserUpdateView.as_view(), name='profile_update'),
    path('user/password/update/', views.UserPasswordUpdateView.as_view(), name='password_update'),
    path('user/comments/', views.UserCommentsListView.as_view(), name='user_comments'),
    path('user/favorites/', views.UserFavoritesListView.as_view(), name='user_favorites'),

]