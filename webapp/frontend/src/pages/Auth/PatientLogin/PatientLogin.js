import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../../contexts';
import './PatientLogin.css';

const PatientLogin = () => {
    const { t } = useTranslation('common');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const { login } = useAuth();

    const handleSubmit = async (event) => {
        event.preventDefault();
        // Validate form first
        if (!email || !password) {
            setError(t('patientLogin.fillFields', 'Please fill in all fields.'));
            return;
        }

        setError('');
        setLoading(true);

        try {
            const response = await fetch(`/api/patients/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            if (response.ok) {
                const responseData = await response.json();
                console.log('Patient login successful:', responseData);

                // Use auth context to login
                login(responseData.token, responseData.user, 'patient');

                // Redirect to patient dashboard or profile
                navigate('/profile');
            } else {
                const errorData = await response.json();
                console.error('Patient login failed:', errorData);
                setError(errorData.detail || t('patientLogin.errorGeneral', 'Login failed'));
            }
        } catch (error) {
            console.error('Error during patient login:', error);
            setError(t('patientLogin.errorOccurred', 'An error occurred during login'));
        } finally {
            setLoading(false);
        }
    };

    // Show login form first
    return (
        <div className="patient-login-container">
            <div className="patient-login-box">
                <h1>{t('patientLogin.title', 'Patient Login')}</h1>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="email">{t('patientLogin.email', 'Email')}</label>
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
                        <label htmlFor="password">{t('patientLogin.password', 'Password')}</label>
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
                        {loading ? t('patientLogin.loggingIn', 'Signing In...') : t('patientLogin.loginButton', 'Sign In')}
                    </button>
                </form>

                {error && <div className="error-message">{error}</div>}

                <div className="links">
                    <button onClick={() => navigate('/auth/login-role-selection')} className="back-button">
                        {t('patientLogin.back', 'Back')}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default PatientLogin;