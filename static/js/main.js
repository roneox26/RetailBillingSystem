// Cart management
let cart = [];

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
}

function updateCartDisplay() {
    const cartTable = document.getElementById('cartTable');
    const totalElement = document.getElementById('total');
    
    if (!cartTable) return;
    
    cartTable.innerHTML = cart.map(item => `
        <tr>
            <td>${item.name}</td>
            <td>${item.quantity}</td>
            <td>$${item.price.toFixed(2)}</td>
            <td>$${(item.price * item.quantity).toFixed(2)}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="removeFromCart('${item.productId}')">
                    Remove
                </button>
            </td>
        </tr>
    `).join('');
    
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    totalElement.textContent = `$${total.toFixed(2)}`;
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.productId !== productId);
    updateCartDisplay();
}

function checkout() {
    if (cart.length === 0) {
        alert('Cart is empty!');
        return;
    }
    
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    
    fetch('/api/transactions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            items: cart,
            total: total
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Transaction completed successfully!');
            cart = [];
            updateCartDisplay();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error processing transaction');
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
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(product)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Product added successfully!');
            location.reload();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error adding product');
    });
}
