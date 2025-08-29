document.addEventListener('DOMContentLoaded', function() {
            const categoryBlocks = document.querySelectorAll('.category-block');

            categoryBlocks.forEach(block => {
                const productList = block.querySelector('.product-list-simple');
                const productCount = productList.querySelectorAll('li').length;

                if (productCount === 0) {
                    block.style.display = 'none';
                }
            });
        });