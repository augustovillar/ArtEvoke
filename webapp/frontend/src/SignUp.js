import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import './SignUp.css';

const SignUp = () => {
    const { t } = useTranslation();
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

    const handleSubmit = async (event) => {
        event.preventDefault();

        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`/api/signup`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, email, password }),
            });

            if (response.ok) {
                console.log(response.message);
                navigate('/login');
            } else {
                const errorData = await response.json();
                setError(errorData.message || t('signup.errorGeneral'));
            }
        } catch (error) {
            setError(t('signup.errorOccurred'));
            console.error('Error during signup:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className='box'>
            <h1>{t('signup.title')}</h1>
            <form onSubmit={handleSubmit}>
                <div>
                    <label htmlFor="username">{t('signup.username')}</label>
                    <input
                        type="text"
                        id="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label htmlFor="email">{t('signup.email')}</label>
                    <input
                        type="email"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label htmlFor="password">{t('signup.password')}</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button type="submit" disabled={loading}>
                    {loading ? t('signup.signingUp') : t('signup.signupButton')}
                </button>
                <div className="create-account-link">
                    <Link to="/login">{t('signup.loginLink')}</Link>
                </div>
            </form>

            {error && <div style={{ color: 'red' }}>{error}</div>}
        </div>
    );
};

export default SignUp;
