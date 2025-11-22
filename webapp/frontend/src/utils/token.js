/**
 * Decodes a JWT token without verification (client-side only)
 * @param {string} token - JWT token string
 * @returns {object|null} - Decoded payload or null if invalid
 */
export const decodeToken = (token) => {
    if (!token) return null;
    
    try {
        const parts = token.split('.');
        if (parts.length !== 3) return null;
        
        const payload = parts[1];
        const decoded = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')));
        return decoded;
    } catch (error) {
        console.error('Error decoding token:', error);
        return null;
    }
};

/**
 * Checks if a JWT token is expired
 * @param {string} token - JWT token string
 * @returns {boolean} - True if token is expired or invalid, false otherwise
 */
export const isTokenExpired = (token) => {
    if (!token) return true;
    
    const decoded = decodeToken(token);
    if (!decoded) return true;
    
    if (!decoded.exp) return true;
    
    const expirationTime = decoded.exp * 1000;
    const currentTime = Date.now();
    
    return currentTime >= (expirationTime - 5000);
};

/**
 * Gets the expiration time of a token
 * @param {string} token - JWT token string
 * @returns {Date|null} - Expiration date or null if invalid
 */
export const getTokenExpiration = (token) => {
    if (!token) return null;
    
    const decoded = decodeToken(token);
    if (!decoded || !decoded.exp) return null;
    
    return new Date(decoded.exp * 1000);
};

