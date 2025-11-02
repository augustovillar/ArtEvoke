import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../../contexts';

const ProtectedRoute = ({ children }) => {
    const { isLoggedIn } = useAuth();

    if (!isLoggedIn) {
        return <Navigate to="/" replace />;
    }

    return children;
};

export default ProtectedRoute;
