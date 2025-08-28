document.addEventListener('DOMContentLoaded', function() {
    const authModal = document.getElementById('authModal');

    // Слушаем событие открытия модального окна
    authModal.addEventListener('show.bs.modal', function(event) {
        // Определяем, какая кнопка вызвала модальное окно
        const relatedButton = event.relatedTarget;
        const action = relatedButton.dataset.action;

        // Вызываем функцию для переключения форм
        switchForm(action);
    });

    // Функция для переключения видимости форм и изменения заголовка
    function switchForm(action) {
        const loginForm = document.getElementById('login-form');
        const registerForm = document.getElementById('register-form');
        const modalTitle = document.getElementById('authModalLabel');

        if (action === 'login') {
            loginForm.style.display = 'block';
            registerForm.style.display = 'none';
            modalTitle.textContent = 'Вхід до акаунту';
        } else if (action === 'register') {
            loginForm.style.display = 'none';
            registerForm.style.display = 'block';
            modalTitle.textContent = 'Створити акаунт';
        }
    }

    // Ниже идет код для отправки форм через AJAX,
    // который был в предыдущих ответах.
    // Его не нужно менять, так как он работает правильно.

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', e => {
            e.preventDefault();
            submitAuthForm(loginForm);
        });
    }

    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', e => {
            e.preventDefault();
            submitAuthForm(registerForm);
        });
    }

    function submitAuthForm(form) {
        const formData = new FormData(form);
        fetch(form.action, {
            method: 'POST',
            body: new URLSearchParams(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                alert('Ошибка: ' + JSON.stringify(data.errors));
            }
        })
        .catch(error => console.error('Ошибка:', error));
    }
});