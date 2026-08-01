import request from './request'

export function getSummary() {
  return request.get('/dashboard/summary')
}

export function getGrowth() {
  return request.get('/dashboard/growth')
}

export function getCategories() {
  return request.get('/dashboard/categories')
}
