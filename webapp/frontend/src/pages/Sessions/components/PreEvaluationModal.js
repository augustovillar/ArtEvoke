import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import './PreEvaluationModal.css';

const PreEvaluationModal = ({ sessionId, onClose, onSubmit }) => {
    const { t } = useTranslation('common');
    const [formData, setFormData] = useState({
        meds_changes: '',
        alone: null,
        any_recent_conditions: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleChange = (field, value) => {
        setFormData(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        if (formData.alone === null) {
            setError(t('preEvaluation.errors.aloneRequired'));
            setLoading(false);
            return;
        }

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`/api/sessions/${sessionId}/pre-evaluation`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || t('preEvaluation.errors.submitFailed'));
            }

            const result = await response.json();
            onSubmit(result);
        } catch (err) {
            setError(err.message);
            console.error('Error submitting pre-evaluation:', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content pre-evaluation-modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <p className="modal-description">{t('preEvaluation.description')}</p>
                    <button className="modal-close-btn" onClick={onClose} disabled={loading}>×</button>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="modal-body">
                        {error && <div className="error-message">{error}</div>}

                        {/* Medication Changes */}
                        <div className="form-group">
                            <label htmlFor="meds_changes">{t('preEvaluation.medsChanges')}</label>
                            <textarea
                                id="meds_changes"
                                value={formData.meds_changes}
                                onChange={(e) => handleChange('meds_changes', e.target.value)}
                                placeholder={t('preEvaluation.medsChangesPlaceholder')}
                                rows="3"
                            />
                        </div>

                        {/* Alone Question */}
                        <div className="form-group">
                            <label>
                                {t('preEvaluation.alone')}
                                <span className="required-asterisk">*</span>
                            </label>
                            <div className="radio-group">
                                <label className="radio-label">
                                    <input
                                        type="radio"
                                        name="alone"
                                        checked={formData.alone === true}
                                        onChange={() => handleChange('alone', true)}
                                    />
                                    <span>{t('common.yes')}</span>
                                </label>
                                <label className="radio-label">
                                    <input
                                        type="radio"
                                        name="alone"
                                        checked={formData.alone === false}
                                        onChange={() => handleChange('alone', false)}
                                    />
                                    <span>{t('common.no')}</span>
                                </label>
                            </div>
                        </div>

                        {/* Recent Conditions */}
                        <div className="form-group">
                            <label htmlFor="any_recent_conditions">{t('preEvaluation.recentConditions')}</label>
                            <textarea
                                id="any_recent_conditions"
                                value={formData.any_recent_conditions}
                                onChange={(e) => handleChange('any_recent_conditions', e.target.value)}
                                placeholder={t('preEvaluation.recentConditionsPlaceholder')}
                                rows="3"
                            />
                        </div>
                    </div>

                    <div className="modal-footer">
                        <button 
                            type="submit" 
                            className="btn-submit" 
                            disabled={loading || formData.alone === null}
                        >
                            {loading ? t('common.submitting') : t('common.continue')}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default PreEvaluationModal;

