import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import './PatientComplete.css';

const PatientComplete = () => {
    const { t } = useTranslation('common');
    const [formData, setFormData] = useState({
        email: '',
        code: '',
        username: '',
        password: '',
        date_of_birth: '',
        education_level: '',
        occupation: '',
        diseases: '',
        medications: '',
        visual_impairment: false,
        hearing_impairment: false,
        household_income: '',
        ethnicity: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData({
            ...formData,
            [name]: type === 'checkbox' ? checked : value
        });
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await fetch(`/api/patients/complete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    ...formData,
                    household_income: formData.household_income ? parseFloat(formData.household_income) : null
                }),
            });

            if (response.ok) {
                const responseData = await response.json();
                console.log('Patient completion successful:', responseData);
                // Redirect to patient login
                navigate('/auth/patient-login');
            } else {
                const errorData = await response.json();
                console.error('Patient completion failed:', errorData);
                setError(errorData.detail || 'Profile completion failed');
            }
        } catch (error) {
            console.error('Error during patient completion:', error);
            setError('An error occurred during profile completion');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="patient-complete-container">
            <div className="patient-complete-box">
                <h1>{t('patientComplete.title', 'Complete Your Patient Profile')}</h1>
                <p>{t('patientComplete.subtitle', 'Enter the email and code provided by your doctor')}</p>

                <form onSubmit={handleSubmit}>
                    {/* Doctor-provided info */}
                    <div className="section">
                        <h3>{t('patientComplete.doctorInfo', 'Information from Doctor')}</h3>
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="email">{t('patientComplete.email', 'Email')}</label>
                                <input
                                    type="email"
                                    id="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    required
                                    placeholder="Email provided by doctor"
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="code">{t('patientComplete.code', 'Access Code')}</label>
                                <input
                                    type="text"
                                    id="code"
                                    name="code"
                                    value={formData.code}
                                    onChange={handleChange}
                                    required
                                    placeholder="4-digit code from doctor"
                                    maxLength="4"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Account info */}
                    <div className="section">
                        <h3>{t('patientComplete.accountInfo', 'Account Information')}</h3>
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="username">{t('patientComplete.username', 'Username')}</label>
                                <input
                                    type="text"
                                    id="username"
                                    name="username"
                                    value={formData.username}
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="password">{t('patientComplete.password', 'Password')}</label>
                                <input
                                    type="password"
                                    id="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                        </div>
                    </div>

                    {/* Personal info */}
                    <div className="section">
                        <h3>{t('patientComplete.personalInfo', 'Personal Information')}</h3>
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="date_of_birth">{t('patientComplete.dateOfBirth', 'Date of Birth')}</label>
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
                                <label htmlFor="education_level">{t('patientComplete.educationLevel', 'Education Level')}</label>
                                <select
                                    id="education_level"
                                    name="education_level"
                                    value={formData.education_level}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="">{t('patientComplete.select', 'Select...')}</option>
                                    <option value="Elementary">Elementary</option>
                                    <option value="High School">High School</option>
                                    <option value="Bachelor">Bachelor's Degree</option>
                                    <option value="Master">Master's Degree</option>
                                    <option value="PhD">PhD</option>
                                    <option value="Other">Other</option>
                                </select>
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="occupation">{t('patientComplete.occupation', 'Occupation')}</label>
                                <input
                                    type="text"
                                    id="occupation"
                                    name="occupation"
                                    value={formData.occupation}
                                    onChange={handleChange}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="ethnicity">{t('patientComplete.ethnicity', 'Ethnicity')}</label>
                                <input
                                    type="text"
                                    id="ethnicity"
                                    name="ethnicity"
                                    value={formData.ethnicity}
                                    onChange={handleChange}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label htmlFor="household_income">{t('patientComplete.householdIncome', 'Household Income (optional)')}</label>
                            <input
                                type="number"
                                id="household_income"
                                name="household_income"
                                value={formData.household_income}
                                onChange={handleChange}
                                step="0.01"
                            />
                        </div>
                    </div>

                    {/* Health info */}
                    <div className="section">
                        <h3>{t('patientComplete.healthInfo', 'Health Information')}</h3>
                        <div className="form-group">
                            <label htmlFor="diseases">{t('patientComplete.diseases', 'Medical Conditions (optional)')}</label>
                            <textarea
                                id="diseases"
                                name="diseases"
                                value={formData.diseases}
                                onChange={handleChange}
                                rows="3"
                                placeholder="List any medical conditions..."
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="medications">{t('patientComplete.medications', 'Current Medications (optional)')}</label>
                            <textarea
                                id="medications"
                                name="medications"
                                value={formData.medications}
                                onChange={handleChange}
                                rows="3"
                                placeholder="List current medications..."
                            />
                        </div>

                        <div className="checkbox-group">
                            <label className="checkbox-label">
                                <input
                                    type="checkbox"
                                    name="visual_impairment"
                                    checked={formData.visual_impairment}
                                    onChange={handleChange}
                                />
                                {t('patientComplete.visualImpairment', 'Visual Impairment')}
                            </label>
                            <label className="checkbox-label">
                                <input
                                    type="checkbox"
                                    name="hearing_impairment"
                                    checked={formData.hearing_impairment}
                                    onChange={handleChange}
                                />
                                {t('patientComplete.hearingImpairment', 'Hearing Impairment')}
                            </label>
                        </div>
                    </div>

                    <button type="submit" disabled={loading} className="complete-button">
                        {loading ? t('patientComplete.completing', 'Completing Profile...') : t('patientComplete.completeButton', 'Complete Profile')}
                    </button>
                </form>

                {error && <div className="error-message">{error}</div>}

                <div className="back-link">
                    <button onClick={() => navigate('/auth/role-selection')} className="back-button">
                        {t('patientComplete.back', 'Back')}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default PatientComplete;