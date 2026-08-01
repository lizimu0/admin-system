import request, { downloadFile } from './request'

export function getUsers(params) {
  return request.get('/users', { params })
}

export function exportUsers(params) {
  return downloadFile('/users/export', params)
}

export function createUser(data) {
  return request.post('/users', data)
}

export function updateUser(id, data) {
  return request.put(`/users/${id}`, data)
}

export function deleteUser(id) {
  return request.delete(`/users/${id}`)
}

export function getRoleOptions() {
  return request.get('/users/roles/options')
}
