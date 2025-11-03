import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams, useNavigate } from 'react-router-dom';
import './SessionDetails.css';

const SessionDetails = () => {
    const { t } = useTranslation('common');
    const { sessionId } = useParams();
    const navigate = useNavigate();
    const [session, setSession] = useState(null);
    const [evaluationData, setEvaluationData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchSessionDetails = async () => {
        try {
            const token = localStorage.getItem('token');
            
            // Fetch session info
            const sessionResponse = await fetch(`/api/sessions/${sessionId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!sessionResponse.ok) {
                if (sessionResponse.status === 404) {
                    setError(t('sessions.errors.notFound'));
                } else if (sessionResponse.status === 403) {
                    setError(t('sessions.errors.unauthorized'));
                } else {
                    setError(t('sessions.errors.loadFailed'));
                }
                return;
            }

            const sessionData = await sessionResponse.json();
            setSession(sessionData);

            // If session is completed, fetch evaluation data
            if (sessionData.status === 'completed') {
                const evalResponse = await fetch(`/api/sessions/${sessionId}/evaluation`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (evalResponse.ok) {
                    const evalData = await evalResponse.json();
                    setEvaluationData(evalData);
                }
            }
        } catch (error) {
            setError(t('sessions.errors.loadFailed'));
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSessionDetails();
    }, [sessionId]); // eslint-disable-line react-hooks/exhaustive-deps

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

                {session.status === 'completed' && evaluationData && (
                    <>
                        {/* Memory Reconstruction Results */}
                        {evaluationData.memory_reconstruction && (
                            <div className="details-section evaluation-results">
                                <h2>{t('sessions.details.memoryReconstructionResults')}</h2>
                                <div className="evaluation-content">
                                    <div className="detail-item">
                                        <span className="detail-label">{t('sessions.details.dataset')}:</span>
                                        <span className="detail-value">{evaluationData.memory_reconstruction.dataset}</span>
                                    </div>
                                    <div className="detail-item">
                                        <span className="detail-label">{t('sessions.details.language')}:</span>
                                        <span className="detail-value">{evaluationData.memory_reconstruction.language}</span>
                                    </div>
                                    <div className="detail-item">
                                        <span className="detail-label">{t('sessions.details.segmentationStrategy')}:</span>
                                        <span className="detail-value">{evaluationData.memory_reconstruction.segmentation_strategy}</span>
                                    </div>
                                    
                                    <div className="story-section">
                                        <h3>{t('sessions.details.patientStory')}</h3>
                                        <div className="story-text">
                                            {evaluationData.memory_reconstruction.story || t('sessions.details.noStory')}
                                        </div>
                                    </div>

                                    {evaluationData.memory_reconstruction.sections && evaluationData.memory_reconstruction.sections.length > 0 && (
                                        <div className="sections-container">
                                            <h3>{t('sessions.details.selectedImages')}</h3>
                                            {evaluationData.memory_reconstruction.sections.map((section, index) => (
                                                <div key={section.id} className="section-item">
                                                    <h4>{t('sessions.details.section')} {section.section_number}</h4>
                                                    <p><strong>{t('sessions.details.content')}:</strong> {section.content}</p>
                                                    {section.catalog_item_id && (
                                                        <div className="artwork-info">
                                                            <p><strong>{t('sessions.details.title')}:</strong> {section.title || 'N/A'}</p>
                                                            <p><strong>{t('sessions.details.author')}:</strong> {section.author || 'N/A'}</p>
                                                            <p><strong>{t('sessions.details.year')}:</strong> {section.year || 'N/A'}</p>
                                                        </div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}

                        {/* Art Exploration Results */}
                        {evaluationData.art_exploration && (
                            <div className="details-section evaluation-results">
                                <h2>{t('sessions.details.artExplorationResults')}</h2>
                                <div className="evaluation-content">
                                    <div className="detail-item">
                                        <span className="detail-label">{t('sessions.details.dataset')}:</span>
                                        <span className="detail-value">{evaluationData.art_exploration.dataset}</span>
                                    </div>
                                    <div className="detail-item">
                                        <span className="detail-label">{t('sessions.details.language')}:</span>
                                        <span className="detail-value">{evaluationData.art_exploration.language}</span>
                                    </div>
                                    
                                    <div className="story-section">
                                        <h3>{t('sessions.details.generatedStory')}</h3>
                                        <div className="story-text">
                                            {evaluationData.art_exploration.story_generated || t('sessions.details.noStory')}
                                        </div>
                                    </div>

                                    {evaluationData.art_exploration.images && evaluationData.art_exploration.images.length > 0 && (
                                        <div className="images-container">
                                            <h3>{t('sessions.details.selectedImages')}</h3>
                                            <div className="images-grid">
                                                {evaluationData.art_exploration.images.map((image, index) => (
                                                    <div key={image.id} className="image-item">
                                                        <div className="image-number">{t('sessions.details.image')} {image.image_number}</div>
                                                        <div className="artwork-info">
                                                            <p><strong>{t('sessions.details.title')}:</strong> {image.title || 'N/A'}</p>
                                                            <p><strong>{t('sessions.details.author')}:</strong> {image.author || 'N/A'}</p>
                                                            <p><strong>{t('sessions.details.year')}:</strong> {image.year || 'N/A'}</p>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}

                        {!evaluationData.memory_reconstruction && !evaluationData.art_exploration && (
                            <div className="details-section">
                                <p className="no-results">{t('sessions.details.noResults')}</p>
                            </div>
                        )}
                    </>
                )}

                {session.status === 'completed' && !evaluationData && (
                    <div className="details-section">
                        <p className="no-results">{t('sessions.details.loadingResults')}</p>
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
