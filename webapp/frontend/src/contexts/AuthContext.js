import React, { createContext, useContext, useState, useEffect } from 'react';

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

    useEffect(() => {
        // Check localStorage on mount
        const token = localStorage.getItem('token');
        const type = localStorage.getItem('userType');
        const userData = localStorage.getItem('user');

        if (token) {
            setIsLoggedIn(true);
            setUserType(type);
            setUser(userData ? JSON.parse(userData) : null);
        }
        setLoading(false);
    }, []);

    const login = (token, userData, type) => {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(userData));
        localStorage.setItem('userType', type);
        setIsLoggedIn(true);
        setUserType(type);
        setUser(userData);
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        localStorage.removeItem('userType');
        setIsLoggedIn(false);
        setUserType(null);
        setUser(null);
    };

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
        </AuthContext.Provider>
    );
};