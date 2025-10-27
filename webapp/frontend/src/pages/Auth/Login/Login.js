import React, { useState } from 'react';
import { Link } from "react-router-dom";
import { useTranslation } from 'react-i18next';
import './Login.css';

const Login = () => {
    const { t } = useTranslation('common');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (event) => {
        event.preventDefault(); // Prevent default form submission behavior
    
        try {
            const response = await fetch(`/api/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });
    
            if (response.ok) {
                // Login successful
                const responseData = await response.json();
                console.log('Login successful:', responseData);
    
                // Store the token in localStorage
                localStorage.setItem('token', responseData.token);
                localStorage.setItem('user', JSON.stringify(responseData.user));
    
                window.location.href = '/profile';
            } else {
                // Login failed
                const errorData = await response.json();
                console.error('Login failed:', errorData);
                setError(t('login.errorInvalid'));
            }
        } catch (error) {
            console.error('Error during login:', error);
            setError(t('login.errorGeneral'));
        }
    };
    

    return (
        <div className="box">
            <h1>{t('login.title')}</h1>
            <form onSubmit={handleSubmit}>
                <div>
                    <label htmlFor="email">{t('login.email', 'Email')}</label>
                    <input
                        type="email"
                        id="email"
                        name="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label htmlFor="password">{t('login.password')}</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button type="submit">{t('login.submit')}</button>
                <div className="create-account-link">
                    <Link to="/signup">{t('login.createAccount')}</Link>
                </div>
            </form>
            {error && <p style={{ color: 'red' }}>{error}</p>}
        </div>
    );
};

export default Login;
