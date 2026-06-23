import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCartStore = defineStore('cart', () => {
  const items = ref([])

  const count = computed(() => items.value.reduce((s, i) => s + i.quantity, 0))
  const total = computed(() => items.value.reduce((s, i) => s + i.price * i.quantity, 0))

  function add(product, quantity = 1) {
    const existing = items.value.find((i) => i.product_id === product.id)
    if (existing) {
      existing.quantity += quantity
    } else {
      items.value.push({
        product_id: product.id,
        name: product.name,
        price: product.price,
        seller_name: product.seller_name,
        quantity,
      })
    }
  }

  function remove(product_id) {
    items.value = items.value.filter((i) => i.product_id !== product_id)
  }

  function updateQty(product_id, quantity) {
    const item = items.value.find((i) => i.product_id === product_id)
    if (item) {
      if (quantity <= 0) remove(product_id)
      else item.quantity = quantity
    }
  }

  function clear() {
    items.value = []
  }

  return { items, count, total, add, remove, updateQty, clear }
})
