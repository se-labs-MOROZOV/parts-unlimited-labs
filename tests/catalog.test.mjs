import test from "node:test";
import assert from "node:assert/strict";
import { PRODUCTS, filterProducts, calculateTotal, formatPrice } from "../docs/catalog.mjs";

test("есть восемь демонстрационных товаров", () => {
  assert.equal(PRODUCTS.length, 8);
  assert.equal(new Set(PRODUCTS.map((p) => p.id)).size, 8);
});
test("у всех товаров цена положительная", () => {
  assert.ok(PRODUCTS.every((p) => p.price > 0 && Number.isInteger(p.stock) && p.stock >= 0));
});
test("пустой поиск возвращает полный каталог", () => {
  assert.equal(filterProducts("").length, PRODUCTS.length);
});
test("поиск не учитывает регистр", () => {
  assert.equal(filterProducts("ФИЛЬТР").length, 2);
});
test("поиск обрезает пробелы по краям", () => {
  assert.equal(filterProducts("  фильтр ").length, 2);
});
test("фильтр категории выделяет нужные товары", () => {
  assert.equal(filterProducts("", "Электрика").length, 2);
});
test("поиск и фильтр категории применяются вместе", () => {
  assert.equal(filterProducts("диск", "Тормозная система").length, 1);
});
test("стоимость пустой корзины нулевая", () => {
  assert.equal(calculateTotal([]), 0);
});
test("стоимость корзины зависит от количества", () => {
  assert.equal(calculateTotal([{ id: "P001", quantity: 2 }, { id: "P005", quantity: 3 }]), 2120);
});
test("нельзя добавить неизвестный товар", () => {
  assert.throws(() => calculateTotal([{ id: "UNKNOWN", quantity: 1 }]));
});
test("нельзя добавить больше товара, чем на складе", () => {
  assert.throws(() => calculateTotal([{ id: "P007", quantity: 4 }]));
});
test("сумма форматируется как рубли", () => {
  assert.match(formatPrice(500), /500/);
});
