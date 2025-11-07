import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import './ConsentForm.css';

const ConsentForm = ({ onAccept, onDecline, showDecline = true }) => {
    const { t } = useTranslation('common');
    const [consentAccepted, setConsentAccepted] = useState(false);

    const handleAccept = () => {
        if (consentAccepted) {
            onAccept();
        }
    };

    const handleDecline = () => {
        onDecline();
    };

    return (
        <div className="consent-form-container">
            <div className="consent-form-box">
                <h1>{t('consent.title', 'Participant Consent Form')}</h1>
                
                <div className="consent-content">
                    <section className="consent-section">
                        <h2>{t('consent.purpose.title', 'Purpose')}</h2>
                        <p>{t('consent.purpose.text', 'This platform allows users to share personal stories, which are then transformed into sequences of images in collaboration with partner museums. The goal of this test is to evaluate and improve the platform\'s usability, relevance, and impact based on participant feedback.')}</p>
                    </section>

                    <section className="consent-section">
                        <h2>{t('consent.voluntary.title', 'Voluntary Participation')}</h2>
                        <p>{t('consent.voluntary.text', 'Your participation is completely voluntary. You may stop using the platform or withdraw your participation at any time, without any consequences.')}</p>
                    </section>

                    <section className="consent-section">
                        <h2>{t('consent.information.title', 'Information Collected')}</h2>
                        <p>{t('consent.information.intro', 'To participate, we will ask only for the following basic information:')}</p>
                        <ul>
                            <li>{t('consent.information.age', 'Age (to confirm eligibility)')}</li>
                            <li>{t('consent.information.education', 'Level of Education (for research contextualization)')}</li>
                        </ul>
                        <p>{t('consent.information.additional', 'Additionally, the stories you share and the feedback you provide during your use of the platform may be collected. No personal identification data (such as full name, address, or contact information) will be required.')}</p>
                    </section>

                    <section className="consent-section">
                        <h2>{t('consent.dataUse.title', 'How Your Data Will Be Used')}</h2>
                        <p>{t('consent.dataUse.text', 'Your contributions will be used only for research and development purposes, specifically to improve the platform experience and evaluate how effectively it supports storytelling and cultural engagement.')}</p>
                        <p>{t('consent.dataUse.noSale', 'No data will be sold, shared, or used for commercial or targeted advertising purposes.')}</p>
                    </section>

                    <section className="consent-section">
                        <h2>{t('consent.conflicts.title', 'Conflicts of Interest')}</h2>
                        <p>{t('consent.conflicts.text', 'By agreeing to participate, you confirm that:')}</p>
                        <ul>
                            <li>{t('consent.conflicts.voluntary', 'You are participating voluntarily.')}</li>
                            <li>{t('consent.conflicts.noConflicts', 'You have no conflicts of interest related to this research or platform.')}</li>
                        </ul>
                    </section>

                    <section className="consent-section">
                        <h2>{t('consent.confidentiality.title', 'Confidentiality')}</h2>
                        <p>{t('consent.confidentiality.text', 'Your participation will remain anonymous. Any results or insights shared publicly will not contain information that could identify you.')}</p>
                    </section>

                    <section className="consent-section">
                        <h2>{t('consent.agreement.title', 'Consent Agreement')}</h2>
                        <p>{t('consent.agreement.intro', 'By checking the box below and/or continuing to use this platform, I declare that:')}</p>
                        <ul>
                            <li>{t('consent.agreement.voluntary', 'I am participating voluntarily.')}</li>
                            <li>{t('consent.agreement.age', 'I am over the age required to consent in my country/region.')}</li>
                            <li>{t('consent.agreement.understand', 'I understand how my data will be used.')}</li>
                            <li>{t('consent.agreement.noConflicts', 'I have no conflicts of interest regarding the use or evaluation of this platform.')}</li>
                            <li>{t('consent.agreement.agree', 'I agree to the terms stated above.')}</li>
                        </ul>
                    </section>

                    <div className="consent-checkbox">
                        <label className="consent-checkbox-label">
                            <input
                                type="checkbox"
                                checked={consentAccepted}
                                onChange={(e) => setConsentAccepted(e.target.checked)}
                                required
                            />
                            <span>{t('consent.checkbox.label', 'I agree and consent to participate')}</span>
                        </label>
                    </div>
                </div>

                <div className="consent-actions">
                    <button
                        type="button"
                        onClick={handleAccept}
                        disabled={!consentAccepted}
                        className="consent-accept-button"
                    >
                        {t('consent.accept', 'Accept and Continue')}
                    </button>
                    {showDecline && (
                        <button
                            type="button"
                            onClick={handleDecline}
                            className="consent-decline-button"
                        >
                            {t('consent.decline', 'Decline')}
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ConsentForm;

