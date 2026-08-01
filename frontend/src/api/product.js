import request, { downloadFile } from './request'

export function getProducts(params) {
  return request.get('/products', { params })
}

export function exportProducts(params) {
  return downloadFile('/products/export', params)
}

export function getCategories() {
  return request.get('/products/categories')
}

export function createProduct(data) {
  return request.post('/products', data)
}

export function updateProduct(id, data) {
  return request.put(`/products/${id}`, data)
}

export function deleteProduct(id) {
  return request.delete(`/products/${id}`)
}
