// Учебные товары Parts Unlimited. Только демонстрационные данные.
export const PRODUCTS = Object.freeze([
  { id: "P001", name: "Масляный фильтр", category: "Фильтры", price: 490, stock: 12 },
  { id: "P002", name: "Воздушный фильтр", category: "Фильтры", price: 720, stock: 8 },
  { id: "P003", name: "Тормозные колодки", category: "Тормозная система", price: 2590, stock: 5 },
  { id: "P004", name: "Тормозной диск", category: "Тормозная система", price: 3400, stock: 6 },
  { id: "P005", name: "Свеча зажигания", category: "Двигатель", price: 380, stock: 20 },
  { id: "P006", name: "Ремень генератора", category: "Двигатель", price: 1150, stock: 9 },
  { id: "P007", name: "Аккумулятор", category: "Электрика", price: 6800, stock: 3 },
  { id: "P008", name: "Лампа фары", category: "Электрика", price: 610, stock: 15 },
]);

export function filterProducts(query = "", category = "Все") {
  const phrase = String(query).trim().toLocaleLowerCase("ru-RU");
  return PRODUCTS.filter((p) =>
    (category === "Все" || p.category === category) &&
    (phrase === "" || p.name.toLocaleLowerCase("ru-RU").includes(phrase))
  );
}

export function calculateTotal(cartItems) {
  return cartItems.reduce((sum, item) => {
    const product = PRODUCTS.find((p) => p.id === item.id);
    if (!product) throw new Error(`Неизвестный товар: ${item.id}`);
    if (!Number.isInteger(item.quantity) || item.quantity < 1 || item.quantity > product.stock) {
      throw new Error(`Некорректное количество для ${item.id}`);
    }
    return sum + product.price * item.quantity;
  }, 0);
}

export function formatPrice(value) {
  return new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB", maximumFractionDigits: 0 }).format(value);
}
