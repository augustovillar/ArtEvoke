import React from 'react';
import { useTranslation } from 'react-i18next';
import './ErrorModal.css';

const ErrorModal = ({ isOpen, message, onClose }) => {
    const { t } = useTranslation('common');

    if (!isOpen) return null;

    return (
        <div className="error-modal-overlay" onClick={onClose}>
            <div className="error-modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="error-modal-header">
                    <h3>{t('common.error', 'Error')}</h3>
                    <button className="error-modal-close" onClick={onClose}>×</button>
                </div>
                <div className="error-modal-body">
                    <p>{message}</p>
                </div>
                <div className="error-modal-footer">
                    <button className="error-modal-button" onClick={onClose}>
                        {t('common.close', 'Close')}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ErrorModal;

