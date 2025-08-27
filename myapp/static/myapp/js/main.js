document.addEventListener('DOMContentLoaded', function() {

    // --- Общие переменные и вспомогательные функции ---
    const totalPriceElement = document.getElementById('total-price');

    function updateTotalPrice(newPrice) {
        if (totalPriceElement) {
            totalPriceElement.innerText = `${newPrice} грн`;
        }
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // --- Логика для навигации ---
    const navLinks = document.querySelectorAll('.product-tabs-nav .tab-link');
    if (navLinks.length > 0) {
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navLinks.forEach(l => l.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }

    const backButton = document.querySelector('.back-button');
    if (backButton) {
        backButton.addEventListener('click', function(event) {
            event.preventDefault();
            window.location.href = '/';
        });
    }

    const historyBackButton = document.querySelector('.back-button-slide');
    if (historyBackButton) {
        historyBackButton.addEventListener('click', function(event) {
            event.preventDefault();
            window.history.back();
        });
    }

    // --- Логика для корзины (добавление и удаление) ---
    document.body.addEventListener('click', function(event) {
        const addToCartBtn = event.target.closest('.add-to-cart-btn');
        const removeItemBtn = event.target.closest('.remove-item-btn');

        if (addToCartBtn) {
            const productId = addToCartBtn.dataset.productId;
            fetch('/store/booking/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: `product_id=${productId}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const toastElement = document.getElementById('cartToast');
                    if (toastElement) {
                        const toast = new bootstrap.Toast(toastElement);
                        toast.show();
                    }
                    if (data.total_price !== undefined) {
                        updateTotalPrice(data.total_price);
                    }

                    // Находим родительский элемент и кнопки
                    const parentContainer = addToCartBtn.closest('.product-actions');
                    const addedLink = parentContainer.querySelector('.added-to-cart-link');

                    addToCartBtn.classList.add('d-none');
                    if (addedLink) {
                        addedLink.classList.remove('d-none');
                    }
                } else {
                    console.error('Не удалось добавить в корзину:', data.error);
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
            });
        } else if (removeItemBtn) {
            const cartItem = removeItemBtn.closest('.cart-item');
            const productId = removeItemBtn.dataset.productId;

            fetch('/store/booking/delete/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: `product_id=${productId}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    cartItem.remove();
                    if (data.total_price !== undefined) {
                        updateTotalPrice(data.total_price);
                    }

                    // Переключаем кнопки на всех страницах
                    // Находим все кнопки "Додати в кошик" с нужным ID
                    const addToCartButtons = document.querySelectorAll(`.add-to-cart-btn[data-product-id="${data.deleted_product_id}"]`);
                    // Находим все кнопки "Товар в кошику" с нужным ID
                    const addedLinks = document.querySelectorAll(`.added-to-cart-link[href*="${data.deleted_product_id}"]`);

                    // Показываем кнопки "Додати в кошик"
                    addToCartButtons.forEach(btn => {
                        btn.classList.remove('d-none');
                    });

                    // Скрываем кнопки "Товар в кошику"
                    addedLinks.forEach(link => {
                        link.classList.add('d-none');
                    });

                } else {
                    console.error('Не удалось удалить товар:', data.error);
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
            });
        }
    });
});