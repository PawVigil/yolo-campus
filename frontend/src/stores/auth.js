import { reactive } from 'vue'

export const authStore = reactive({
  token: localStorage.getItem('token') || null,
  username: localStorage.getItem('username') || null,

  get isLoggedIn() {
    return !!this.token
  },

  login(token, username) {
    this.token = token
    this.username = username
    localStorage.setItem('token', token)
    localStorage.setItem('username', username)
  },

  logout() {
    this.token = null
    this.username = null
    localStorage.removeItem('token')
    localStorage.removeItem('username')
  },
})
