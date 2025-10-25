import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import './PatientLogin.css';

const PatientLogin = () => {
    const { t } = useTranslation('common');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (event) => {
        event.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await fetch(`/api/patients/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            if (response.ok) {
                const responseData = await response.json();
                console.log('Patient login successful:', responseData);

                // Store the token and user info
                localStorage.setItem('token', responseData.token);
                localStorage.setItem('user', JSON.stringify(responseData.user));
                localStorage.setItem('userType', 'patient');

                // Redirect to patient dashboard or profile
                navigate('/profile');
            } else {
                const errorData = await response.json();
                console.error('Patient login failed:', errorData);
                setError(errorData.detail || 'Login failed');
            }
        } catch (error) {
            console.error('Error during patient login:', error);
            setError('An error occurred during login');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="patient-login-container">
            <div className="patient-login-box">
                <h1>{t('patientLogin.title', 'Patient Login')}</h1>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="username">{t('patientLogin.username', 'Username')}</label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
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
                    <button onClick={() => navigate('/auth/role-selection')} className="back-button">
                        {t('patientLogin.back', 'Back')}
                    </button>
                    <button onClick={() => navigate('/auth/patient-complete')} className="complete-link">
                        {t('patientLogin.needAccount', 'Complete Profile')}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default PatientLogin;