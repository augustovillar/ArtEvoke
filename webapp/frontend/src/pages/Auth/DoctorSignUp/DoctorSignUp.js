import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import './DoctorSignUp.css';

const DoctorSignUp = () => {
    const { t } = useTranslation('common');
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        name: '',
        date_of_birth: '',
        specialization: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await fetch(`/api/doctors/signup`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            if (response.ok) {
                const responseData = await response.json();
                console.log('Doctor signup successful:', responseData);
                // Redirect to login page
                navigate('/auth/doctor-login');
            } else {
                const errorData = await response.json();
                console.error('Doctor signup failed:', errorData);
                setError(errorData.detail || 'Registration failed');
            }
        } catch (error) {
            console.error('Error during doctor signup:', error);
            setError('An error occurred during registration');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="doctor-signup-container">
            <div className="doctor-signup-box">
                <h1>{t('doctorSignup.title', 'Doctor Registration')}</h1>
                <form onSubmit={handleSubmit}>
                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="name">{t('doctorSignup.name', 'Full Name')}</label>
                            <input
                                type="text"
                                id="name"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="email">{t('doctorSignup.email', 'Email')}</label>
                            <input
                                type="email"
                                id="email"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="date_of_birth">{t('doctorSignup.dateOfBirth', 'Date of Birth')}</label>
                            <input
                                type="date"
                                id="date_of_birth"
                                name="date_of_birth"
                                value={formData.date_of_birth}
                                onChange={handleChange}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="specialization">{t('doctorSignup.specialization', 'Specialization')}</label>
                            <input
                                type="text"
                                id="specialization"
                                name="specialization"
                                value={formData.specialization}
                                onChange={handleChange}
                                required
                                placeholder="e.g., Neurology, Psychiatry"
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">{t('doctorSignup.password', 'Password')}</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <button type="submit" disabled={loading} className="signup-button">
                        {loading ? t('doctorSignup.signingUp', 'Creating Account...') : t('doctorSignup.signupButton', 'Create Doctor Account')}
                    </button>
                </form>

                {error && <div className="error-message">{error}</div>}

                <div className="back-link">
                    <button onClick={() => navigate('/auth/role-selection')} className="back-button">
                        {t('doctorSignup.back', 'Back')}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default DoctorSignUp;