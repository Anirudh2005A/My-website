document.addEventListener("DOMContentLoaded", function () {
    updateCartCount();

    // Add to Cart Buttons
    document.querySelectorAll(".add-to-cart").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            let productId = this.getAttribute("data-id");
            addToCart(productId);
        });
    });

    // Remove from Cart Buttons
    document.querySelectorAll(".remove-from-cart").forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            let productId = this.getAttribute("data-id");
            removeFromCart(productId);
        });
    });
});

// Function to add product to cart
function addToCart(productId) {
    fetch(`/add_to_cart/${productId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Product added to cart!");
                updateCartCount();
            }
        })
        .catch(error => console.error("Error adding to cart:", error));
}

// Function to remove product from cart
function removeFromCart(productId) {
    fetch(`/remove_from_cart/${productId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Product removed from cart!");
                location.reload(); // Refresh the page to update the cart
            }
        })
        .catch(error => console.error("Error removing from cart:", error));
}

// Function to update cart count
function updateCartCount() {
    fetch("/cart_count")
        .then(response => response.json())
        .then(data => {
            document.getElementById("cart-count").innerText = data.count;
        })
        .catch(error => console.error("Error fetching cart count:", error));
}
