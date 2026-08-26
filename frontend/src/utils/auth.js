export const saveAuth = (data) => {
  localStorage.setItem('token', data.access_token)
  localStorage.setItem('user', JSON.stringify({
    role: data.role,
    full_name: data.full_name
  }))
}

export const getUser = () => {
  const user = localStorage.getItem('user')
  return user ? JSON.parse(user) : null
}

export const getToken = () => localStorage.getItem('token')

export const isLoggedIn = () => !!getToken()

export const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  window.location.href = '/login'
}

export const isAdmin = () => {
  const user = getUser()
  return user?.role === 'admin'
}