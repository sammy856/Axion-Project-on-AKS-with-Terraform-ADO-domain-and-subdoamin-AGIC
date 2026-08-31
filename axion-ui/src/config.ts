/**
 * Centralized API Configuration for Axion UI
 */
const getApiBase = (): string => {
  if (import.meta.env.VITE_API_BASE) {
    return import.meta.env.VITE_API_BASE;
  }
  if (typeof window !== 'undefined' && window.location) {
    const { hostname, protocol } = window.location;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'http://localhost:8000';
    }
    // If accessed via domain (e.g. axion.b18g151.online), route to telemetry subdomain with same protocol
    if (hostname.includes('.')) {
      const parts = hostname.split('.');
      if (parts.length >= 2) {
        const rootDomain = parts.slice(1).join('.');
        return `${protocol}//telemetry.${rootDomain}`;
      }
    }
  }
  return 'http://telemetry.b18g151.online';
};

export const API_BASE = getApiBase();
