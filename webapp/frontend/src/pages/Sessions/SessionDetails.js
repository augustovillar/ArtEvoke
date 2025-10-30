import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams, useNavigate } from 'react-router-dom';
import './SessionDetails.css';

const SessionDetails = () => {
    const { t } = useTranslation('common');
    const { sessionId } = useParams();
    const navigate = useNavigate();
    const [session, setSession] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchSessionDetails();
    }, [sessionId]);

    const fetchSessionDetails = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`/api/sessions/${sessionId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setSession(data);
            } else if (response.status === 404) {
                setError(t('sessions.errors.notFound'));
            } else if (response.status === 403) {
                setError(t('sessions.errors.unauthorized'));
            } else {
                setError(t('sessions.errors.loadFailed'));
            }
        } catch (error) {
            setError(t('sessions.errors.loadFailed'));
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    const getStatusClass = (status) => {
        switch (status) {
            case 'pending': return 'status-pending';
            case 'in_progress': return 'status-in-progress';
            case 'completed': return 'status-completed';
            default: return '';
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    if (loading) {
        return <div className="session-details-loading">{t('common.loading')}</div>;
    }

    if (error) {
        return (
            <div className="session-details-error">
                <p>{error}</p>
                <button onClick={() => navigate(-1)} className="btn-back">
                    {t('common.back')}
                </button>
            </div>
        );
    }

    if (!session) {
        return null;
    }

    return (
        <div className="session-details-container">
            <div className="session-details-header">
                <button onClick={() => navigate(-1)} className="btn-back">
                    ← {t('common.back')}
                </button>
                <h1>{t('sessions.details.title')}</h1>
            </div>

            <div className="session-details-content">
                <div className="details-section">
                    <h2>{t('sessions.details.generalInfo')}</h2>
                    <div className="details-grid">
                        <div className="detail-item">
                            <span className="detail-label">{t('sessions.mode')}:</span>
                            <span className="detail-value">{t(`sessions.modes.${session.mode}`)}</span>
                        </div>
                        <div className="detail-item">
                            <span className="detail-label">{t('sessions.status')}:</span>
                            <span className={`detail-value session-status ${getStatusClass(session.status)}`}>
                                {t(`sessions.statuses.${session.status}`)}
                            </span>
                        </div>
                        <div className="detail-item">
                            <span className="detail-label">{t('sessions.interruptionTime')}:</span>
                            <span className="detail-value">{session.interruption_time} {t('sessions.details.seconds')}</span>
                        </div>
                    </div>
                </div>

                <div className="details-section">
                    <h2>{t('sessions.details.timeline')}</h2>
                    <div className="details-grid">
                        <div className="detail-item">
                            <span className="detail-label">{t('sessions.createdAt')}:</span>
                            <span className="detail-value">{formatDate(session.created_at)}</span>
                        </div>
                        <div className="detail-item">
                            <span className="detail-label">{t('sessions.startedAt')}:</span>
                            <span className="detail-value">{formatDate(session.started_at)}</span>
                        </div>
                        <div className="detail-item">
                            <span className="detail-label">{t('sessions.completedAt')}:</span>
                            <span className="detail-value">{formatDate(session.ended_at)}</span>
                        </div>
                    </div>
                </div>

                {session.status === 'completed' && (
                    <div className="details-section">
                        <h2>{t('sessions.details.results')}</h2>
                        <div className="details-grid">
                            {session.memory_reconstruction_id && (
                                <div className="detail-item">
                                    <span className="detail-label">{t('sessions.details.memoryReconstructionId')}:</span>
                                    <span className="detail-value">{session.memory_reconstruction_id}</span>
                                </div>
                            )}
                            {session.art_exploration_id && (
                                <div className="detail-item">
                                    <span className="detail-label">{t('sessions.details.artExplorationId')}:</span>
                                    <span className="detail-value">{session.art_exploration_id}</span>
                                </div>
                            )}
                        </div>
                        {!session.memory_reconstruction_id && !session.art_exploration_id && (
                            <p className="no-results">{t('sessions.details.noResults')}</p>
                        )}
                    </div>
                )}

                {session.status === 'pending' && (
                    <div className="details-section">
                        <div className="info-message">
                            <p>{t('sessions.details.pendingMessage')}</p>
                        </div>
                    </div>
                )}

                {session.status === 'in_progress' && (
                    <div className="details-section">
                        <div className="info-message">
                            <p>{t('sessions.details.inProgressMessage')}</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SessionDetails;
