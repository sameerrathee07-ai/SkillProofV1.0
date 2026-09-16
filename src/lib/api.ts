const rawBaseUrl = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').trim();
export const API_BASE_URL = rawBaseUrl.replace(/\/+$/, '');

export async function apiFetch(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem('skillproof_token');

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const response = await fetch(`${API_BASE_URL}${cleanEndpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    localStorage.removeItem('skillproof_token');
    localStorage.removeItem('skillproof_user');
    window.dispatchEvent(new CustomEvent('skillproof:unauthorized'));
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const errorMsg = data.detail || 'An error occurred while communicating with server.';
    throw new Error(errorMsg);
  }

  return data;
}
