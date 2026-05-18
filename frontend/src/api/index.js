const BASE = '/api'

async function request(method, path, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  }
  if (body !== undefined) opts.body = JSON.stringify(body)
  const res = await fetch(BASE + path, opts)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

export const api = {
  // Users
  listUsers: () => request('GET', '/users'),
  createUser: (data) => request('POST', '/users', data),
  deleteUser: (id) => request('DELETE', `/users/${id}`),
  startContainer: (id) => request('POST', `/users/${id}/start`),
  stopContainer: (id) => request('POST', `/users/${id}/stop`),
  restartContainer: (id) => request('POST', `/users/${id}/restart`),
  getStatus: (id) => request('GET', `/users/${id}/status`),
  getLogs: (id, lines = 100) => request('GET', `/users/${id}/logs?lines=${lines}`),
  getUserConfig: (id) => request('GET', `/users/${id}/config`),
  updateUserConfig: (id, config_json) => request('PUT', `/users/${id}/config`, { config_json }),

  // Template
  getTemplate: () => request('GET', '/template'),
  updateTemplate: (config_json) => request('PUT', '/template', { config_json }),

  // System
  systemStatus: () => request('GET', '/system/status'),
}
