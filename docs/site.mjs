import { PRODUCTS, filterProducts, calculateTotal, formatPrice } from "./catalog.mjs";

const search = document.querySelector("#search");
const category = document.querySelector("#category");
const catalog = document.querySelector("#catalog");
const count = document.querySelector("#count");
const cartList = document.querySelector("#cart-list");
const total = document.querySelector("#total");
const cart = new Map();

for (const item of [...new Set(PRODUCTS.map((product) => product.category))]) {
  const option = document.createElement("option");
  option.value = item;
  option.textContent = item;
  category.append(option);
}

function renderCatalog() {
  const results = filterProducts(search.value, category.value);
  catalog.replaceChildren();
  count.textContent = `Найдено товаров: ${results.length}`;
  for (const product of results) {
    const card = document.createElement("article");
    card.className = "product";
    const heading = document.createElement("h3");
    heading.textContent = product.name;
    const details = document.createElement("p");
    details.textContent = `${product.category} · На складе: ${product.stock}`;
    const price = document.createElement("strong");
    price.textContent = formatPrice(product.price);
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = "Добавить в корзину";
    button.disabled = (cart.get(product.id) ?? 0) >= product.stock;
    button.addEventListener("click", () => {
      cart.set(product.id, (cart.get(product.id) ?? 0) + 1);
      renderCatalog();
      renderCart();
    });
    card.append(heading, details, price, button);
    catalog.append(card);
  }
}

function renderCart() {
  cartList.replaceChildren();
  const cartItems = [...cart.entries()].map(([id, quantity]) => ({ id, quantity }));
  for (const { id, quantity } of cartItems) {
    const product = PRODUCTS.find((p) => p.id === id);
    const li = document.createElement("li");
    li.textContent = `${product.name} × ${quantity} – ${formatPrice(product.price * quantity)}`;
    cartList.append(li);
  }
  total.textContent = formatPrice(calculateTotal(cartItems));
}

search.addEventListener("input", renderCatalog);
category.addEventListener("change", renderCatalog);
renderCatalog();
renderCart();
