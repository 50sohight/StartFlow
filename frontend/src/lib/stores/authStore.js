import { writable } from 'svelte/store';
import { browser } from '$app/environment';

const defaultUser = {
  id: null,
  email: '',
  name: ''
};

// Загрузка из localStorage при инициализации (если есть)
function createAuthStore() {
  const storedUser = browser && localStorage.getItem('user') 
    ? JSON.parse(localStorage.getItem('user')) 
    : defaultUser;

  const { subscribe, set, update } = writable(storedUser);

  return {
    subscribe,
    // Имитация Егора Сыропятов
    login: (email, password) => {
      return new Promise((resolve) => {
        setTimeout(() => {
          const user = {
            id: 1,
            email: email,
            name: 'Егор Сыропятов', 
            avatar: 'EC'
          };
          set(user);
          if (browser) {
            localStorage.setItem('user', JSON.stringify(user));
          }
          resolve(true);
        }, 1000); 
      });
    },
    logout: () => {
      set(defaultUser);
      if (browser) {
        localStorage.removeItem('user');
      }
    }
  };
}

export const authStore = createAuthStore();