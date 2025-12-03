import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import MemoryReconstructionResults from './components/MemoryReconstructionResults';
import ArtExplorationResults from './components/ArtExplorationResults';
import EvaluationsInfoModal from './components/EvaluationsInfoModal';
import './SessionResults.css';

const SessionResults = () => {
    const { sessionId } = useParams();
    const { t } = useTranslation('common');
    const navigate = useNavigate();
    const { userType } = useAuth();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [results, setResults] = useState(null);
    const [notCompleted, setNotCompleted] = useState(false);
    const [showEvaluationsModal, setShowEvaluationsModal] = useState(false);
    const [preEvaluation, setPreEvaluation] = useState(null);
    const [posEvaluation, setPosEvaluation] = useState(null);
    const [loadingEvaluations, setLoadingEvaluations] = useState(false);

    useEffect(() => {
        const fetchResults = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await fetch(`/api/sessions/${sessionId}/results`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (!response.ok) {
                    if (response.status === 400) {
                        const errorData = await response.json();
                        // Check if error is about session not being completed
                        if (errorData.detail && (
                            errorData.detail.includes('not completed') || 
                            errorData.detail.includes('não foi concluída') ||
                            errorData.detail.includes('not found')
                        )) {
                            setNotCompleted(true);
                            setError(null);
                        } else {
                            throw new Error(errorData.detail || t('results.errors.notCompleted'));
                        }
                    } else if (response.status === 403) {
                        throw new Error(t('results.errors.unauthorized'));
                    } else if (response.status === 404) {
                        const errorData = await response.json();
                        // Check if it's evaluation not found (session exists but no evaluation)
                        if (errorData.detail && errorData.detail.includes('Evaluation not found')) {
                            setNotCompleted(true);
                            setError(null);
                        } else {
                            throw new Error(t('results.errors.notFound'));
                        }
                    } else {
                        throw new Error(t('results.errors.loadFailed'));
                    }
                } else {
                    const data = await response.json();
                    setResults(data);
                    setError(null);
                }
            } catch (err) {
                console.error('Error fetching results:', err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchResults();
    }, [sessionId, t]);

    const handleBack = () => {
        if (userType === 'doctor') {
            // Doctor goes back to patient's sessions
            const patientId = results?.memory_reconstruction_results 
                ? results.memory_reconstruction_results.patient_id 
                : null;
            
            if (patientId) {
                navigate(`/sessions?patientId=${patientId}`);
            } else {
                navigate('/patients');
            }
        } else {
            // Patient goes back to their sessions
            navigate('/sessions');
        }
    };

    const handleViewEvaluations = async () => {
        setLoadingEvaluations(true);
        try {
            const token = localStorage.getItem('token');
            
            // Fetch both evaluations in parallel
            const [preResponse, posResponse] = await Promise.all([
                fetch(`/api/sessions/${sessionId}/pre-evaluation`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                }),
                fetch(`/api/sessions/${sessionId}/pos-evaluation`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                })
            ]);
            
            if (preResponse.ok) {
                const preData = await preResponse.json();
                setPreEvaluation(preData);
            } else {
                setPreEvaluation(null);
            }
            
            if (posResponse.ok) {
                const posData = await posResponse.json();
                setPosEvaluation(posData);
            } else {
                setPosEvaluation(null);
            }
            
            setShowEvaluationsModal(true);
        } catch (err) {
            console.error('Error fetching evaluations:', err);
            alert(t('evaluations.errors.loadFailed'));
        } finally {
            setLoadingEvaluations(false);
        }
    };

    if (loading) {
        return (
            <div className="results-container">
                <div className="results-loading">{t('common.loading')}</div>
            </div>
        );
    }

    if (notCompleted) {
        return (
            <div className="results-container">
                <div className="results-not-completed">
                    <div className="not-completed-icon">⏳</div>
                    <h2>{t('results.notCompleted.title')}</h2>
                    <p>{t('results.notCompleted.message')}</p>
                    <button className="btn-back" onClick={handleBack}>
                        ← {t('common.back')}
                    </button>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="results-container">
                <div className="results-error">
                    <h2>{t('results.errors.title')}</h2>
                    <p>{error}</p>
                    <button className="btn-back" onClick={handleBack}>
                        {t('common.back')}
                    </button>
                </div>
            </div>
        );
    }

    if (!results) {
        return (
            <div className="results-container">
                <div className="results-error">
                    <p>{t('results.errors.noData')}</p>
                    <button className="btn-back" onClick={handleBack}>
                        {t('common.back')}
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="results-container">
            <div className="results-header">
                <button className="btn-back" onClick={handleBack}>
                    ← {t('common.back')}
                </button>
                <h1>{t('results.title')}</h1>
                <button 
                    className="btn-view-evaluations" 
                    onClick={handleViewEvaluations}
                    disabled={loadingEvaluations}
                >
                    {loadingEvaluations ? t('common.loading') : t('evaluations.viewButton')}
                </button>
            </div>

            <div className="results-info">
                <div className="info-item">
                    <span className="info-label">{t('results.mode')}:</span>
                    <span className="info-value">{t(`sessions.modes.${results.mode}`)}</span>
                </div>
                <div className="info-item">
                    <span className="info-label">{t('results.completedAt')}:</span>
                    <span className="info-value">
                        {results.completed_at 
                            ? new Date(results.completed_at).toLocaleString() 
                            : '-'}
                    </span>
                </div>
            </div>

            {results.mode === 'memory_reconstruction' && results.memory_reconstruction_results && (
                <MemoryReconstructionResults data={results.memory_reconstruction_results} />
            )}

            {results.mode === 'art_exploration' && results.art_exploration_results && (
                <ArtExplorationResults data={results.art_exploration_results} />
            )}

            {showEvaluationsModal && (
                <EvaluationsInfoModal
                    sessionId={sessionId}
                    onClose={() => setShowEvaluationsModal(false)}
                    preEvaluation={preEvaluation}
                    posEvaluation={posEvaluation}
                />
            )}
        </div>
    );
};

export default SessionResults;
