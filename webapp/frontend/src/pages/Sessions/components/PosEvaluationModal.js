import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import './PosEvaluationModal.css';

const PosEvaluationModal = ({ sessionId, onClose, onSubmit }) => {
    const { t } = useTranslation('common');
    const [formData, setFormData] = useState({
        experience: null,
        difficulty: null,
        observations: ''
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

        // Validate required fields
        if (formData.experience === null || formData.difficulty === null) {
            setError(t('posEvaluation.errors.requiredFields'));
            setLoading(false);
            return;
        }

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`/api/sessions/${sessionId}/pos-evaluation`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || t('posEvaluation.errors.submitFailed'));
            }

            const result = await response.json();
            onSubmit(result);
        } catch (err) {
            setError(err.message);
            console.error('Error submitting pos-evaluation:', err);
        } finally {
            setLoading(false);
        }
    };

    const renderRatingButtons = (field, label) => {
        return (
            <div className="form-group">
                <label>
                    {label}
                    <span className="required-asterisk">*</span>
                </label>
                <div className="rating-group">
                    {[...Array(11)].map((_, index) => (
                        <button
                            key={index}
                            type="button"
                            className={`rating-button ${formData[field] === index ? 'selected' : ''}`}
                            onClick={() => handleChange(field, index)}
                            disabled={loading}
                        >
                            {index}
                        </button>
                    ))}
                </div>
                <div className="rating-labels">
                    <span>{t('posEvaluation.ratingMin')}</span>
                    <span>{t('posEvaluation.ratingMax')}</span>
                </div>
            </div>
        );
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content pos-evaluation-modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <p className="modal-description">{t('posEvaluation.description')}</p>
                    <button className="modal-close-btn" onClick={onClose} disabled={loading}>×</button>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="modal-body">
                        {error && <div className="error-message">{error}</div>}

                        {/* Experience Rating */}
                        {renderRatingButtons('experience', t('posEvaluation.experience'))}

                        {/* Difficulty Rating */}
                        {renderRatingButtons('difficulty', t('posEvaluation.difficulty'))}

                        {/* Observations */}
                        <div className="form-group">
                            <label htmlFor="observations">{t('posEvaluation.observations')}</label>
                            <textarea
                                id="observations"
                                value={formData.observations}
                                onChange={(e) => handleChange('observations', e.target.value)}
                                placeholder={t('posEvaluation.observationsPlaceholder')}
                                rows="4"
                            />
                        </div>
                    </div>

                    <div className="modal-footer">
                        <button 
                            type="submit" 
                            className="btn-submit" 
                            disabled={loading || formData.experience === null || formData.difficulty === null}
                        >
                            {loading ? t('common.submitting') : t('common.submit')}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default PosEvaluationModal;

