import request from './request'

export function login(data) {
  return request.post('/auth/login', data)
}

export function getMe() {
  return request.get('/auth/me')
}

export function getCaptcha() {
  return request.get('/auth/captcha')
}

export function updateProfile(data) {
  return request.put('/auth/profile', data)
}

export function changePassword(data) {
  return request.post('/auth/change-password', data)
}
