// Cart management
let cart = [];
let discountPercent = 0;
let vatPercent = 15; // Default VAT 15%

function addToCart(productId, name, price) {
    const existingItem = cart.find(item => item.productId === productId);

    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            productId,
            name,
            price: parseFloat(price),
            quantity: 1
        });
    }

    updateCartDisplay();
    showToast(`${name} added to cart`, 'success');
}

function updateCartDisplay() {
    const cartTable = document.getElementById('cartTable');
    const subtotalElement = document.getElementById('subtotal');
    const discountElement = document.getElementById('discountAmount');
    const vatElement = document.getElementById('vatAmount');
    const totalElement = document.getElementById('total');

    if (!cartTable) return;

    if (cart.length === 0) {
        cartTable.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Cart is empty</td></tr>';
        if (subtotalElement) subtotalElement.textContent = '৳0.00';
        if (discountElement) discountElement.textContent = '৳0.00';
        if (vatElement) vatElement.textContent = '৳0.00';
        if (totalElement) totalElement.textContent = '৳0.00';
        return;
    }

    cartTable.innerHTML = cart.map(item => `
        <tr>
            <td>${item.name}</td>
            <td>
                <input type="number" min="1" value="${item.quantity}" 
                       onchange="updateQuantity('${item.productId}', this.value)"
                       class="form-control form-control-sm" style="width: 60px;">
            </td>
            <td>৳${item.price.toFixed(2)}</td>
            <td><strong>৳${(item.price * item.quantity).toFixed(2)}</strong></td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="removeFromCart('${item.productId}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');

    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const discountAmount = (subtotal * discountPercent) / 100;
    const afterDiscount = subtotal - discountAmount;
    const vatAmount = (afterDiscount * vatPercent) / 100;
    const total = afterDiscount + vatAmount;

    if (subtotalElement) subtotalElement.textContent = `৳${subtotal.toFixed(2)}`;
    if (discountElement) discountElement.textContent = `৳${discountAmount.toFixed(2)}`;
    if (vatElement) vatElement.textContent = `৳${vatAmount.toFixed(2)}`;
    if (totalElement) totalElement.textContent = `৳${total.toFixed(2)}`;
}

function updateDiscount(value) {
    discountPercent = parseFloat(value) || 0;
    if (discountPercent < 0) discountPercent = 0;
    if (discountPercent > 100) discountPercent = 100;
    updateCartDisplay();
}

function updateVAT(value) {
    vatPercent = parseFloat(value) || 0;
    if (vatPercent < 0) vatPercent = 0;
    if (vatPercent > 100) vatPercent = 100;
    updateCartDisplay();
}

function updateQuantity(productId, quantity) {
    const item = cart.find(item => item.productId === productId);
    if (item) {
        item.quantity = parseInt(quantity) || 1;
        updateCartDisplay();
    }
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.productId != productId);
    updateCartDisplay();
    showToast('Item removed from cart', 'info');
}

function checkout() {
    if (cart.length === 0) {
        showToast('Cart is empty!', 'warning');
        return;
    }

    const btn = event.target;
    showLoading(btn);

    fetch('/api/transactions', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            items: cart,
            discount_percent: discountPercent,
            vat_percent: vatPercent
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading(btn);
        if (data.status === 'success' && data.transaction_id) {
            showToast('Transaction completed!', 'success');
            setTimeout(() => window.location.href = `/invoice/${data.transaction_id}`, 1000);
            cart = [];
            discountPercent = 0;
            updateCartDisplay();
        } else {
            showToast(data.message || 'Transaction failed', 'danger');
        }
    })
    .catch(error => {
        hideLoading(btn);
        showToast('Error processing transaction', 'danger');
    });
}

// Product management
function addProduct(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const product = {
        name: formData.get('name'),
        price: formData.get('price'),
        stock: formData.get('stock')
    };

    fetch('/api/products', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(product)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showToast('Product added successfully!', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast(data.message || 'Error adding product', 'danger');
        }
    })
    .catch(error => {
        showToast('Error adding product', 'danger');
    });
}