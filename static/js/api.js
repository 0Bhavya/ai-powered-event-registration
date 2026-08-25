class ApiClient {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL;
  }

  get token() {
    return localStorage.getItem('token');
  }

  set token(value) {
    if (value) {
      localStorage.setItem('token', value);
    } else {
      localStorage.removeItem('token');
    }
  }
  
  clearAuth() {
    this.token = null;
    localStorage.removeItem('user');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    
    // For x-www-form-urlencoded (login)
    if (options.body && options.body instanceof URLSearchParams) {
      delete headers['Content-Type'];
    }

    const config = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);
      
      // Attempt to parse JSON if possible
      let data = null;
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        data = await response.json();
      } else if (response.status === 204) {
        data = null; // No content
      } else {
        data = await response.text();
      }

      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
            // unauthorized, clear token
            if(endpoint !== '/auth/login' && endpoint !== '/auth/register') {
                this.clearAuth();
                window.location.href = '/login';
            }
        }
        const errorMsg = data && data.detail ? data.detail : (typeof data === 'string' ? data : 'API Error');
        throw new Error(typeof errorMsg === 'object' ? JSON.stringify(errorMsg) : errorMsg);
      }

      return data;
    } catch (error) {
      throw error;
    }
  }

  get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  post(endpoint, body, isForm = false) {
    return this.request(endpoint, {
      method: 'POST',
      body: isForm ? body : JSON.stringify(body),
    });
  }

  put(endpoint, body) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(body),
    });
  }

  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
}

const api = new ApiClient();
window.api = api;
