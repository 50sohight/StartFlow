// src/lib/stores/authStore.js
import { writable } from 'svelte/store';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8078';
const BASE_URL = `${API_BASE_URL}/auth`;

function createAuthStore() {
  const { subscribe, set } = writable(null);

  async function loadUser() {
    try {
      const res = await fetch(`${BASE_URL}/me`, {
        credentials: 'include'
      });
      if (!res.ok) {
        set(null);
        return null;
      }
      const user = await res.json();
      set(user);
      return user;
    } catch {
      set(null);
      return null;
    }
  }

  return {
    subscribe,

    login: async (login, password) => {
      const res = await fetch(`${BASE_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ login, password })
      });
      if (!res.ok) throw new Error('Ошибка авторизации');
      await loadUser();
    },

    register: async (fullname, login, password) => {
      const res = await fetch(`${BASE_URL}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ fullname, login, password })
      });
      if (!res.ok) throw new Error('Ошибка регистрации');
      await loadUser();
    },

  logout: async () => {
    set(null);
    try {
      await fetch(`${BASE_URL}/logout`, {
        method: 'POST',
        credentials: 'include'
      });
    } catch {
      // If the request fails, the user is still logged out locally.
    }
  },

    fetchUser: loadUser
  };
}

export const authStore = createAuthStore();