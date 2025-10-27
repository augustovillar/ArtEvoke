import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../../contexts';
import './DoctorLogin.css';

const DoctorLogin = () => {
    const { t } = useTranslation('common');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const { login } = useAuth();

    const handleSubmit = async (event) => {
        event.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await fetch(`/api/doctors/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            if (response.ok) {
                const responseData = await response.json();
                console.log('Doctor login successful:', responseData);

                // Use auth context to login
                login(responseData.token, responseData.user, 'doctor');

                // Redirect to doctor dashboard or profile
                navigate('/profile');
            } else {
                const errorData = await response.json();
                console.error('Doctor login failed:', errorData);
                setError(errorData.detail || t('doctorLogin.errorGeneral', 'Login failed'));
            }
        } catch (error) {
            console.error('Error during doctor login:', error);
            setError(t('doctorLogin.errorOccurred', 'An error occurred during login'));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="doctor-login-container">
            <div className="doctor-login-box">
                <h1>{t('doctorLogin.title', 'Doctor Login')}</h1>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="email">{t('doctorLogin.email', 'Email')}</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="password">{t('doctorLogin.password', 'Password')}</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    <button type="submit" disabled={loading} className="login-button">
                        {loading ? t('doctorLogin.loggingIn', 'Signing In...') : t('doctorLogin.loginButton', 'Sign In')}
                    </button>
                </form>

                {error && <div className="error-message">{error}</div>}

                <div className="links">
                    <button onClick={() => navigate('/auth/login-role-selection')} className="back-button">
                        {t('doctorLogin.back', 'Back')}
                    </button>
                    <button onClick={() => navigate('/auth/doctor-signup')} className="signup-link">
                        {t('doctorLogin.needAccount', 'Need an account?')}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default DoctorLogin;