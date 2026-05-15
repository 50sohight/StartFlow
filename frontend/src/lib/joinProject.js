// src/lib/api/joinProject.js

const BASE_URL = 'http://localhost:8000';

/**
 * Присоединяется к проекту по коду приглашения.
 * @param {string} code
 * @returns {Promise<{ ok: boolean, message?: string }>}
 */
export async function useInviteLink(code) {
  if (!code?.trim()) {
    return { ok: false, message: 'Введите код приглашения' };
  }

  const res = await fetch(`${BASE_URL}/link/use_link/${encodeURIComponent(code.trim())}`, {
    method: 'POST',
    credentials: 'include'
  });

  if (res.ok) {
    return { ok: true };
  }

  let message = 'Не удалось присоединиться';
  try {
    message = await res.text() || message;
  } catch { /* ignore */ }
  return { ok: false, message };
}