import request from './request'

export function getOperationLogs(params) {
  return request.get('/logs/operation', { params })
}

export function getLoginLogs(params) {
  return request.get('/logs/login', { params })
}
