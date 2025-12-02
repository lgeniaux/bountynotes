const API_BASE_URL_OVERRIDE_KEY = 'bountynotes.apiBaseUrl';

function getDefaultApiBaseUrl(): string {
  if (typeof window === 'undefined') {
    return 'http://127.0.0.1:8000';
  }

  return `${window.location.protocol}//${window.location.hostname}:8000`;
}

export function resolveApiBaseUrl(): string {
  if (typeof window === 'undefined') {
    return getDefaultApiBaseUrl();
  }

  return window.localStorage.getItem(API_BASE_URL_OVERRIDE_KEY) ?? getDefaultApiBaseUrl();
}
