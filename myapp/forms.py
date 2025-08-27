from django import forms
from myapp.models import Category, Product, Comment
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError



class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        labels = {
                    'name': 'Назва категорії',
                }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'image']
        labels = {
                    'name': 'Назва товару',
                    'category': 'Категорія',
                    'description': 'Опис',
                    'price': 'Ціна',
                    'image': 'Зображення',
                }



# --- RegistrationForm
class MyUserRegistrationForm(UserCreationForm):
    username = forms.CharField(
        label='Логін',
        help_text='Логін має бути унікальним. Не більше 150 символів. Тільки літери, цифри та символи @/./+/-/_',
    )
    password1 = forms.CharField(
        label='Пароль',
        help_text='Пароль має містити щонайменше 8 символів, мінімум одну літеру та одну цифру.',
        widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        label='Підтвердження пароля',
        help_text='Повторіть той самий пароль для підтвердження.',
        widget=forms.PasswordInput()
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


# --- LoginForm
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Логін")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

# --- UpdateUserForm
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Ім`я',
            'last_name': 'Прізвище',
            'email': 'Ел.пошта',
        }


# --- UpdateUserPassword
class UserPasswordUpdateForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Новий пароль',
        widget=forms.PasswordInput(),
        help_text='Пароль має містити щонайменше 8 символів, мінімум одну літеру та одну цифру.'
    )
    password2 = forms.CharField(
        label='Підтвердження пароля',
        widget=forms.PasswordInput(),
        help_text='Повторіть той самий пароль для підтвердження.'
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        labels = {
            'username': 'Логін',
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError("Паролі не співпадають.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user



# --- CommentForm
RATING_CHOICES = [
    (5, '⭐⭐⭐⭐⭐ 5 - чудово'),
    (4, '⭐⭐⭐⭐ 4 - добре'),
    (3, '⭐⭐⭐ 3 - нормально'),
    (2, '⭐⭐ 2 - так собі'),
    (1, '⭐ 1 - погано'),
]

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'rating']
        labels = {
            'text': 'Текст відгуку',
            'rating': 'Оцінка (найвищий бал 5)',
        }
        widgets = {
            'rating': forms.Select(choices=RATING_CHOICES)
        }
