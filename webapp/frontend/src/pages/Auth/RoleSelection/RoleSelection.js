import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import './RoleSelection.css';

const RoleSelection = () => {
    const { t } = useTranslation('common');

    return (
        <div className="role-selection-container">
            <div className="role-selection-box">
                <h1>{t('roleSelection.title', 'Choose Your Role')}</h1>
                <p>{t('roleSelection.subtitle', 'Select whether you are a doctor or a patient')}</p>

                <div className="role-buttons">
                    <Link to="/auth/doctor-signup" className="role-button doctor-button">
                        <h2>{t('roleSelection.doctor', 'Doctor')}</h2>
                        <p>{t('roleSelection.doctorDesc', 'Register as a healthcare professional')}</p>
                    </Link>

                    <Link to="/auth/patient-complete" className="role-button patient-button">
                        <h2>{t('roleSelection.patient', 'Patient')}</h2>
                        <p>{t('roleSelection.patientDesc', 'Complete your patient profile')}</p>
                    </Link>
                </div>

                <div className="login-link">
                    <p>{t('roleSelection.alreadyHaveAccount', 'Already have an account?')}</p>
                    <Link to="/auth/login-selection">{t('roleSelection.signIn', 'Sign In')}</Link>
                </div>
            </div>
        </div>
    );
};

export default RoleSelection;