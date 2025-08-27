"""
URL configuration for OnlineStore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from myapp.views import index_page, RegisterView, ConfirmLogoutView
from myapp.forms import LoginForm
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_page, name='index'),
    path('store/', include('myapp.urls')),
    path('login/', LoginView.as_view(template_name="myapp/login.html", form_class=LoginForm), name='login'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('logout/confirm/', ConfirmLogoutView.as_view(), name='confirm_logout'),
    path('register/', RegisterView.as_view(), name='register'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
