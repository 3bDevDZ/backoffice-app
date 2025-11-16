/**
 * API client utilities for AJAX requests
 * Provides a simple interface for making API calls with authentication
 */

class APIClient {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
        this.token = this.getToken();
    }
    
    /**
     * Get JWT token from localStorage
     * @returns {string|null} JWT token or null
     */
    getToken() {
        return localStorage.getItem('access_token');
    }
    
    /**
     * Set JWT token in localStorage
     * @param {string} token - JWT token
     */
    setToken(token) {
        this.token = token;
        localStorage.setItem('access_token', token);
    }
    
    /**
     * Clear JWT token
     */
    clearToken() {
        this.token = null;
        localStorage.removeItem('access_token');
    }
    
    /**
     * Get current locale from URL or default
     * @returns {string} Locale code
     */
    getLocale() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('locale') || 'fr';
    }
    
    /**
     * Build request headers
     * @returns {Object} Headers object
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        // Add locale to query params (handled in request methods)
        return headers;
    }
    
    /**
     * Build URL with locale parameter
     * @param {string} endpoint - API endpoint
     * @returns {string} Full URL with locale
     */
    buildURL(endpoint) {
        const url = new URL(endpoint, window.location.origin);
        url.searchParams.set('locale', this.getLocale());
        return url.toString();
    }
    
    /**
     * Handle API response
     * @param {Response} response - Fetch response
     * @returns {Promise} Parsed JSON or error
     */
    async handleResponse(response) {
        if (!response.ok) {
            const error = await response.json().catch(() => ({ message: 'Unknown error' }));
            throw new Error(error.message || `HTTP ${response.status}`);
        }
        
        // Handle 204 No Content
        if (response.status === 204) {
            return null;
        }
        
        return response.json();
    }
    
    /**
     * GET request
     * @param {string} endpoint - API endpoint
     * @param {Object} params - Query parameters
     * @returns {Promise} Response data
     */
    async get(endpoint, params = {}) {
        const url = new URL(endpoint, `${window.location.origin}${this.baseURL}`);
        url.searchParams.set('locale', this.getLocale());
        
        // Add additional query parameters
        Object.keys(params).forEach(key => {
            url.searchParams.set(key, params[key]);
        });
        
        const response = await fetch(url.toString(), {
            method: 'GET',
            headers: this.getHeaders(),
        });
        
        return this.handleResponse(response);
    }
    
    /**
     * POST request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body
     * @returns {Promise} Response data
     */
    async post(endpoint, data = {}) {
        const url = new URL(endpoint, `${window.location.origin}${this.baseURL}`);
        url.searchParams.set('locale', this.getLocale());
        
        const response = await fetch(url.toString(), {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(data),
        });
        
        return this.handleResponse(response);
    }
    
    /**
     * PUT request
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Request body
     * @returns {Promise} Response data
     */
    async put(endpoint, data = {}) {
        const url = new URL(endpoint, `${window.location.origin}${this.baseURL}`);
        url.searchParams.set('locale', this.getLocale());
        
        const response = await fetch(url.toString(), {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(data),
        });
        
        return this.handleResponse(response);
    }
    
    /**
     * DELETE request
     * @param {string} endpoint - API endpoint
     * @returns {Promise} Response data
     */
    async delete(endpoint) {
        const url = new URL(endpoint, `${window.location.origin}${this.baseURL}`);
        url.searchParams.set('locale', this.getLocale());
        
        const response = await fetch(url.toString(), {
            method: 'DELETE',
            headers: this.getHeaders(),
        });
        
        return this.handleResponse(response);
    }
}

// Create global API client instance
window.api = new APIClient();

