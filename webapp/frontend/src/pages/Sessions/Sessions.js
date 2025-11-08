import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import CreateSession from './CreateSession';
import './Sessions.css';

const Sessions = () => {
    const { t } = useTranslation('common');
    const { userType } = useAuth();
    const [searchParams] = useSearchParams();
    const patientId = searchParams.get('patientId');
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const navigate = useNavigate();

    // Debug log
    console.log('Sessions - userType:', userType, 'patientId:', patientId, 'should show button:', userType === 'doctor' && patientId);

    const fetchSessions = useCallback(async () => {
        try {
            const token = localStorage.getItem('token');
            let url;
            
            if (patientId) {
                // Doctor viewing specific patient's sessions
                url = `/api/sessions/patient/${patientId}`;
            } else if (userType === 'patient') {
                // Patient viewing their own sessions
                url = '/api/sessions/my-sessions';
            } else {
                // No valid context, return empty
                setSessions([]);
                setLoading(false);
                return;
            }

            const response = await fetch(url, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                // If returns empty array or valid array, it's success
                setSessions(Array.isArray(data) ? data : []);
                setError(null);
            } else if (response.status === 404) {
                // 404 means there are no sessions, not an error
                setSessions([]);
                setError(null);
            } else if (response.status === 403 || response.status === 401) {
                // Authorization error
                const errorData = await response.json().catch(() => ({}));
                if (errorData.detail) {
                    if (errorData.detail.includes("don't have access")) {
                        setError(t('sessions.errors.noAccess'));
                    } else if (errorData.detail.includes('token')) {
                        setError(t('sessions.errors.unauthorized'));
                    } else {
                        setError(t('sessions.errors.unauthorized'));
                    }
                } else {
                    // Might just be that there are no sessions yet, treat as empty list
                    setSessions([]);
                    setError(null);
                }
            } else {
                // Other real error
                setError(t('sessions.errors.loadFailed'));
                setSessions([]);
            }
        } catch (error) {
            // Network error or other unexpected error
            setError(t('sessions.errors.loadFailed'));
            console.error('Error:', error);
            setSessions([]);
        } finally {
            setLoading(false);
        }
    }, [patientId, userType, t]);

    useEffect(() => {
        fetchSessions();
    }, [fetchSessions]);

    const handleCreateSession = () => {
        setShowCreateModal(true);
    };

    const handleSessionCreated = () => {
        setShowCreateModal(false);
        fetchSessions();
    };

    const handleDeleteSession = async (sessionId) => {
        if (!window.confirm(t('sessions.deleteConfirm.message'))) {
            return;
        }

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`/api/sessions/${sessionId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                fetchSessions();
            } else {
                alert(t('sessions.errors.deleteFailed'));
            }
        } catch (error) {
            alert(t('sessions.errors.deleteFailed'));
            console.error('Error:', error);
        }
    };

    const handleStartSession = async (session) => {
        try {
            const token = localStorage.getItem('token');
            
            // First, check the current session status to determine appropriate action
            const statusResponse = await fetch(`/api/sessions/${session.id}/status`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!statusResponse.ok) {
                alert(t('sessions.errors.statusCheckFailed'));
                return;
            }

            const sessionStatus = await statusResponse.json();
            
            // Handle different session states
            if (sessionStatus.status === 'completed') {
                // Session already completed, go to results
                navigate(`/sessions/${session.id}/results`);
                return;
            }
            
            if (sessionStatus.status === 'in_evaluation') {
                // Session activity completed, go directly to evaluation
                // Need to fetch the saved data to reconstruct phase1
                const evalResponse = await fetch(`/api/sessions/${session.id}/evaluation`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (!evalResponse.ok) {
                    alert(t('sessions.errors.loadEvaluationFailed') || 'Failed to load evaluation data');
                    return;
                }

                const evalData = await evalResponse.json();

                if (sessionStatus.mode === 'art_exploration') {
                    const sessionData = {
                        sessionId: sessionStatus.session_id,
                        mode: 'session',
                        interruption: {
                            duration: sessionStatus.interruption_time,
                            completed: true
                        },
                        timestamp: new Date().toISOString()
                    };
                    
                    navigate(`/sessions/${session.id}/art-exploration/evaluation`, {
                        state: { sessionData }
                    });
                } else if (sessionStatus.mode === 'memory_reconstruction' && evalData.memory_reconstruction) {
                    const mr = evalData.memory_reconstruction;
                    
                    // Reconstruct phase1 data from saved memory reconstruction
                    const sessionData = {
                        sessionId: sessionStatus.session_id,
                        mode: 'session',
                        phase1: {
                            story: mr.story,
                            language: mr.language,
                            dataset: mr.dataset,
                            segmentation: mr.segmentation_strategy,
                            sections: mr.sections.map((section) => ({
                                sectionId: section.id,
                                sectionText: section.section_content,
                                imagesShown: section.images.filter(img => img !== null),
                                selectedImage: section.fav_image || {}
                            }))
                        },
                        interruption: {
                            duration: sessionStatus.interruption_time,
                            completed: true
                        },
                        timestamp: new Date().toISOString()
                    };
                    
                    navigate(`/sessions/${session.id}/memory-reconstruction/evaluation`, {
                        state: { sessionData }
                    });
                }
                return;
            }
            
            // For pending or in_progress status, update to in_progress and continue to activity
            if (sessionStatus.status === 'pending') {
                const updateResponse = await fetch(`/api/sessions/${session.id}`, {
                    method: 'PATCH',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        status: 'in_progress',
                        started_at: new Date().toISOString().split('T')[0]
                    })
                });

                if (!updateResponse.ok) {
                    alert(t('sessions.errors.startFailed'));
                    return;
                }
            }

            // Navigate to the appropriate mode based on session mode
            // Pass session data via state to avoid unnecessary fetch
            if (sessionStatus.mode === 'memory_reconstruction') {
                navigate(`/sessions/${session.id}/memory-reconstruction`, {
                    state: {
                        sessionId: sessionStatus.session_id,
                        memoryReconstructionId: sessionStatus.memory_reconstruction_id,
                        interruptionTime: sessionStatus.interruption_time,
                        mode: sessionStatus.mode
                    }
                });
            } else if (sessionStatus.mode === 'art_exploration') {
                navigate(`/sessions/${session.id}/art-exploration`, {
                    state: {
                        sessionId: sessionStatus.session_id,
                        interruptionTime: sessionStatus.interruption_time,
                        mode: sessionStatus.mode
                    }
                });
            }
            
        } catch (error) {
            alert(t('sessions.errors.startFailed'));
            console.error('Error:', error);
        }
    };

    const getStatusClass = (status) => {
        switch (status) {
            case 'pending': return 'status-pending';
            case 'in_progress': return 'status-in-progress';
            case 'in_evaluation': return 'status-in-evaluation';
            case 'completed': return 'status-completed';
            default: return '';
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return '-';
        return new Date(dateString).toLocaleDateString();
    };

    if (loading) {
        return <div className="sessions-loading">{t('common.loading')}</div>;
    }

    return (
        <div className="sessions-container">
            <div className="sessions-header">
                <h1>{patientId ? t('sessions.patientSessions') : t('sessions.mySessions')}</h1>
                {userType === 'doctor' && patientId && (
                    <button className="btn-create-session" onClick={handleCreateSession}>
                        + {t('sessions.createSession')}
                    </button>
                )}
            </div>

            {error && <div className="sessions-error">{error}</div>}

            {/* Show message if doctor but no patient selected */}
            {userType === 'doctor' && !patientId ? (
                <div className="sessions-empty">
                    <p>{t('sessions.selectPatientFirst')}</p>
                </div>
            ) : sessions.length === 0 ? (
                <div className="sessions-empty">
                    <p>{t('sessions.noSessions')}</p>
                </div>
            ) : (
                <div className="sessions-list">
                    {sessions.map(session => (
                        <div key={session.id} className="session-card">
                            <div className="session-header">
                                <h3>{t(`sessions.modes.${session.mode}`)}</h3>
                                <span className={`session-status ${getStatusClass(session.status)}`}>
                                    {t(`sessions.statuses.${session.status}`)}
                                </span>
                            </div>
                            <div className="session-details">
                                <div className="session-detail">
                                    <span className="detail-label">{t('sessions.interruptionTime')}:</span>
                                    <span className="detail-value">{session.interruption_time}s</span>
                                </div>
                                <div className="session-detail">
                                    <span className="detail-label">{t('sessions.createdAt')}:</span>
                                    <span className="detail-value">{formatDate(session.created_at)}</span>
                                </div>
                                {session.started_at && (
                                    <div className="session-detail">
                                        <span className="detail-label">{t('sessions.startedAt')}:</span>
                                        <span className="detail-value">{formatDate(session.started_at)}</span>
                                    </div>
                                )}
                                {session.ended_at && (
                                    <div className="session-detail">
                                        <span className="detail-label">{t('sessions.completedAt')}:</span>
                                        <span className="detail-value">{formatDate(session.ended_at)}</span>
                                    </div>
                                )}
                            </div>
                            <div className="session-actions">
                                {userType === 'patient' && session.status === 'pending' && (
                                    <button 
                                        className="btn-start-session"
                                        onClick={() => handleStartSession(session)}
                                    >
                                        {t('sessions.start')}
                                    </button>
                                )}
                                {userType === 'patient' && session.status === 'in_progress' && (
                                    <button 
                                        className="btn-continue-session"
                                        onClick={() => handleStartSession(session)}
                                    >
                                        {t('sessions.continue')}
                                    </button>
                                )}
                                {userType === 'patient' && session.status === 'in_evaluation' && (
                                    <button 
                                        className="btn-continue-session"
                                        onClick={() => handleStartSession(session)}
                                    >
                                        {t('sessions.continueEvaluation')}
                                    </button>
                                )}
                                {userType === 'patient' && session.status === 'completed' && (
                                    <button 
                                        className="btn-view-session"
                                        disabled={true}
                                        title={t('sessions.resultsComingSoon') || 'Página de resultados em desenvolvimento'}
                                    >
                                        {t('sessions.viewResults')}
                                    </button>
                                )}
                                {userType === 'doctor' && (
                                    <>
                                        <button 
                                            className="btn-view-session"
                                            onClick={() => navigate(`/sessions/${session.id}/results`)}
                                        >
                                            {t('sessions.view')}
                                        </button>
                                        <button 
                                            className="btn-delete-session"
                                            onClick={() => handleDeleteSession(session.id)}
                                        >
                                            {t('sessions.delete')}
                                        </button>
                                    </>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {showCreateModal && (
                <CreateSession
                    patientId={patientId}
                    onClose={() => setShowCreateModal(false)}
                    onSuccess={handleSessionCreated}
                />
            )}
        </div>
    );
};

export default Sessions;
