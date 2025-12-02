import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { isTokenExpired } from '../utils/token';
import Toast from '../components/common/Toast';

const AuthContext = createContext();

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [userType, setUserType] = useState(null);
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [toastMessage, setToastMessage] = useState(null);
    const location = useLocation();
    const navigate = useNavigate();
    const { t } = useTranslation('common');

    const login = (token, userData, type) => {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(userData));
        localStorage.setItem('userType', type);
        setIsLoggedIn(true);
        setUserType(type);
        setUser(userData);
    };

    const logout = useCallback(() => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('userType');
        setIsLoggedIn(false);
        setUserType(null);
        setUser(null);
    }, []);

    // Validate token function - memoized to avoid dependency issues
    const validateToken = useCallback(() => {
        const token = localStorage.getItem('token');
        
        if (!token) {
            if (isLoggedIn) {
                logout();
            }
            return false;
        }

        if (isTokenExpired(token)) {
            // Token is expired
            setToastMessage(t('login.sessionExpired', 'Your session has expired. Please log in again.'));
            logout();
            const currentPath = location.pathname;
            const isAuthPage = currentPath.startsWith('/auth/') || 
                              currentPath === '/login' || 
                              currentPath === '/signup';
            
            if (!isAuthPage) {
                setTimeout(() => {
                    navigate('/auth/login-role-selection', { replace: true });
                }, 100);
            }
            return false;
        }

        return true;
    }, [isLoggedIn, logout, navigate, t, location.pathname]);

    // Validate token on mount
    useEffect(() => {
        const token = localStorage.getItem('token');
        const type = localStorage.getItem('userType');
        const userData = localStorage.getItem('user');

        if (token && !isTokenExpired(token)) {
            setIsLoggedIn(true);
            setUserType(type);
            setUser(userData ? JSON.parse(userData) : null);
        } else if (token && isTokenExpired(token)) {
            // Token exists but is expired
            setToastMessage(t('login.sessionExpired', 'Your session has expired. Please log in again.'));
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            localStorage.removeItem('userType');
        }
        setLoading(false);
    }, [t]);

    useEffect(() => {
        if (!loading && isLoggedIn) {
            validateToken();
        }
    }, [location.pathname, loading, isLoggedIn, validateToken]);

    // Also validate token periodically (every 60 seconds)
    useEffect(() => {
        if (!isLoggedIn) return;

        const interval = setInterval(() => {
            if (!validateToken()) {
                clearInterval(interval);
            }
        }, 60000);

        return () => clearInterval(interval);
    }, [isLoggedIn, validateToken]);

    const value = {
        isLoggedIn,
        userType,
        user,
        loading,
        login,
        logout
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
            {toastMessage && (
                <Toast
                    message={toastMessage}
                    type="warning"
                    duration={5000}
                    onClose={() => setToastMessage(null)}
                />
            )}
        </AuthContext.Provider>
    );
};