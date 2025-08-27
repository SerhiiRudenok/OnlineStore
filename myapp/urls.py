from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_page, name='index_page'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),

    # Booking
    path('booking/create/', views.BookingCreateView.as_view(), name='booking_create'),
    path('booking/detail/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('booking/delete/', views.BookingDeleteView.as_view(), name='booking_delete'),

]