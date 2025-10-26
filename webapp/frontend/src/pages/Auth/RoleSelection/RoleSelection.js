import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import './RoleSelection.css';

const RoleSelection = ({ mode = 'signup', title, bottomText }) => {
    const { t } = useTranslation('common');

    const signUpButtons = [
        { title: t('roleSelection.doctorButton'), link: '/auth/doctor-signup', className: 'doctor-button' },
        { title: t('roleSelection.patientButton'), link: '/auth/patient-complete', className: 'patient-button' }
    ];

    const loginButtons = [
        { title: t('roleSelection.doctorButton'), link: '/auth/doctor-login', className: 'doctor-button' },
        { title: t('roleSelection.patientButton'), link: '/auth/patient-login', className: 'patient-button' }
    ];

    const buttons = mode === 'login' ? loginButtons : signUpButtons;
    const bottomButton = mode === 'login'
        ? { text: t('roleSelection.signUpButton'), link: '/auth/role-selection' }
        : { text: t('roleSelection.signInButton'), link: '/auth/login-role-selection' };

    const defaultTitle = mode === 'login' ? t('roleSelection.signInTitle') : t('roleSelection.signUpTitle');
    const defaultBottomText = mode === 'login' ? t('roleSelection.dontHaveAccount') : t('roleSelection.alreadyHaveAccount');

    return (
        <div className="role-selection-container">
            <div className="role-selection-box">
                <h1>{title || defaultTitle}</h1>
                <p>{t('roleSelection.subtitle')}</p>

                <div className="role-buttons">
                    {buttons.map((button, index) => (
                        <Link key={index} to={button.link} className={`role-button ${button.className}`}>
                            <h2>{button.title}</h2>
                        </Link>
                    ))}
                </div>

                <div className="bottom-link">
                    <p>{bottomText || defaultBottomText}</p>
                    <Link to={bottomButton.link} className="link-button">{bottomButton.text}</Link>
                </div>
            </div>
        </div>
    );
};

export default RoleSelection;