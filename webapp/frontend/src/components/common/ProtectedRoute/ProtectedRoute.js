import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../../contexts';

const ProtectedRoute = ({ children }) => {
    const { isLoggedIn, loading } = useAuth();
    const location = useLocation();

    // Wait for auth state to be loaded before making decisions
    if (loading) {
        return <div className="sessions-loading">Loading...</div>;
    }

    if (!isLoggedIn) {
        // Save the attempted location for redirecting after login
        return <Navigate to="/" replace state={{ from: location }} />;
    }

    return children;
};

export default ProtectedRoute;
