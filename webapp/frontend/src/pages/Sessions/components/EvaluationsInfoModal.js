import React from 'react';
import { useTranslation } from 'react-i18next';
import './EvaluationsInfoModal.css';

const EvaluationsInfoModal = ({ sessionId, onClose, preEvaluation, posEvaluation }) => {
    const { t } = useTranslation('common');

    const renderRatingDisplay = (value, label) => {
        return (
            <div className="eval-item full-width">
                <span className="eval-label">{label}:</span>
                <div className="rating-display">
                    {[...Array(11)].map((_, index) => (
                        <div
                            key={index}
                            className={`rating-display-button ${value === index ? 'selected' : ''}`}
                        >
                            {index}
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content evaluations-info-modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>{t('evaluations.title')}</h2>
                    <button className="modal-close-btn" onClick={onClose}>×</button>
                </div>

                <div className="modal-body">
                    {/* Pre-Evaluation */}
                    <div className="evaluation-section">
                        <h3>{t('evaluations.preEvaluation')}</h3>
                        {preEvaluation ? (
                            <div className="evaluation-content">
                                <div className="eval-item">
                                    <span className="eval-label">{t('preEvaluation.medsChanges')}:</span>
                                    <span className="eval-value">{preEvaluation.meds_changes || '-'}</span>
                                </div>
                                <div className="eval-item">
                                    <span className="eval-label">{t('preEvaluation.alone')}:</span>
                                    <span className="eval-value">
                                        {preEvaluation.alone === true 
                                            ? t('common.yes') 
                                            : preEvaluation.alone === false 
                                            ? t('common.no') 
                                            : '-'}
                                    </span>
                                </div>
                                <div className="eval-item">
                                    <span className="eval-label">{t('preEvaluation.recentConditions')}:</span>
                                    <span className="eval-value">{preEvaluation.any_recent_conditions || '-'}</span>
                                </div>
                                <div className="eval-item">
                                    <span className="eval-label">{t('evaluations.submittedAt')}:</span>
                                    <span className="eval-value">
                                        {new Date(preEvaluation.created_at).toLocaleString()}
                                    </span>
                                </div>
                            </div>
                        ) : (
                            <p className="no-data">{t('evaluations.noPreEvaluation')}</p>
                        )}
                    </div>

                    {/* Pos-Evaluation */}
                    <div className="evaluation-section">
                        <h3>{t('evaluations.posEvaluation')}</h3>
                        {posEvaluation ? (
                            <div className="evaluation-content">
                                {posEvaluation.experience !== null && posEvaluation.experience !== undefined && 
                                    renderRatingDisplay(posEvaluation.experience, t('posEvaluation.experience'))
                                }
                                {posEvaluation.difficulty !== null && posEvaluation.difficulty !== undefined && 
                                    renderRatingDisplay(posEvaluation.difficulty, t('posEvaluation.difficulty'))
                                }
                                {posEvaluation.observations && (
                                    <div className="eval-item full-width">
                                        <span className="eval-label">{t('posEvaluation.observations')}:</span>
                                        <p className="eval-text">{posEvaluation.observations}</p>
                                    </div>
                                )}
                                <div className="eval-item">
                                    <span className="eval-label">{t('evaluations.submittedAt')}:</span>
                                    <span className="eval-value">
                                        {new Date(posEvaluation.created_at).toLocaleString()}
                                    </span>
                                </div>
                            </div>
                        ) : (
                            <p className="no-data">{t('evaluations.noPosEvaluation')}</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default EvaluationsInfoModal;

