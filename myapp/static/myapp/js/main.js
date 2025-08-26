
//product_detail
//код для визуального переключения между все про товар, характеристики и отзывы
document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('.product-tabs-nav .tab-link');

    navLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            //убирает активный класс
            navLinks.forEach(l => l.classList.remove('active'));

            //доавляет актив в нужное значение (что было нажато) файл
            this.classList.add('active');
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const backButton = document.querySelector('.back-button');

    if (backButton) {
        backButton.addEventListener('click', function(event) {
            event.preventDefault();
            window.location.href = '/';
        });
    }
});