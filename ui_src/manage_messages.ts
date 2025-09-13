// Code which sets up axios interceptor to inject error messages from api response to
// into the messages area on the page (part of base template).

// messages-interceptor.ts
import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

type ServerMessage = {
  level: 'debug' | 'info' | 'success' | 'warning' | 'error';
  message: string;
};

function levelToBootstrapClass(level: ServerMessage['level']): string {
  switch (level) {
    case 'success':
      return 'alert-success';
    case 'warning':
      return 'alert-warning';
    case 'error':
      return 'alert-danger';
    case 'info':
      return 'alert-info';
    case 'debug':
    default:
      return 'alert-secondary';
  }
}

function createAlertElement(msg: ServerMessage): HTMLDivElement {
  const alertDiv = document.createElement('div');
  // Match the template’s structure/classes
  alertDiv.className = `alert ${levelToBootstrapClass(msg.level)} alert-dismissible fade show`;
  alertDiv.setAttribute('role', 'alert');

  // Message text
  alertDiv.append(document.createTextNode(msg.message));

  // Close button (Bootstrap will wire this up since its JS is loaded)
  const closeBtn = document.createElement('button');
  closeBtn.type = 'button';
  closeBtn.className = 'btn-close';
  closeBtn.setAttribute('data-bs-dismiss', 'alert');
  closeBtn.setAttribute('aria-label', 'Close');

  alertDiv.appendChild(closeBtn);
  return alertDiv;
}

function injectMessagesFromHeader(headerValue?: string | null): void {
  if (!headerValue) {
    console.log('[messages] No X-Server-Messages header present');
    return;
  }

  let parsed: ServerMessage[] | null = null;
  try {
    parsed = JSON.parse(headerValue);
  } catch {
    console.warn('[messages] X-Server-Messages header present but could not be parsed as JSON');
    // Silently ignore malformed header
    return;
  }

  if (!Array.isArray(parsed) || parsed.length === 0) {
    console.log('[messages] X-Server-Messages header present but contains no messages');
    return;
  }

  console.log(`[messages] Found ${parsed.length} message(s) in X-Server-Messages header`);

  const container = document.getElementById('messages-container');
  if (!container) {
    console.warn('[messages] messages-container element not found in DOM');
    return;
  }

  for (const m of parsed) {
    // Basic shape check
    if (!m || typeof m.message !== 'string' || typeof m.level !== 'string') continue;
    container.appendChild(createAlertElement(m as ServerMessage));
  }
}

export function setupAxiosMessageInterceptor(instance: AxiosInstance = axios): void {
  instance.interceptors.response.use(
    (response: AxiosResponse) => {
      // Axios lowercases response header keys in the browser
      const header = response.headers?.['x-server-messages'];
      
      injectMessagesFromHeader(header);
      return response;
    },
    (error: AxiosError) => {
      const header = error.response?.headers?.['x-server-messages'];
      injectMessagesFromHeader(header);
      // Re-throw so callers still see the error
      return Promise.reject(error);
    }
  );
}

// Example: call this once at app startup
// setupAxiosMessageInterceptor();