import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import './ArtExploration.css';
import InterruptionModal from '../../components/interruptionModal';
import { INTERRUPTION_CONFIG } from '../../config/interruption.config';
import {
    InstructionsSection,
    KeywordInputForm,
    ImageSelection,
    GeneratedStory,
    useImageSearch,
    useImageSelection,
    useStoryGeneration,
    useSave
} from './components';

const ArtExplorationSession = () => {
    const { sessionId } = useParams();
    const location = useLocation();
    const navigate = useNavigate();

    const [storyText, setStoryText] = useState('');
    const [dataset, setDataset] = useState('wikiart');

    const [showInterruption, setShowInterruption] = useState(false);
    const [interruptionTime, setInterruptionTime] = useState(10);
    
    const [loadingSession, setLoadingSession] = useState(false);

    const { t, i18n } = useTranslation('common');

    // Get language from i18n - reactive to language changes
    const language = useMemo(() => {
        const lang = i18n.resolvedLanguage || i18n.language || localStorage.getItem('i18nextLng') || 'en';
        return lang.split('-')[0].toLowerCase();
    }, [i18n.language, i18n.resolvedLanguage]);

    const { images, submitLoading, searchImages } = useImageSearch();
    const { selectedImages, handleImageToggle, clearSelections } = useImageSelection();
    const { generateLoading, responseText, storyData, generateStory } = useStoryGeneration();
    const { isSaving, hasSaved, saveStory, resetSaveState } = useSave();

    // Scroll to image selection when search completes
    useEffect(() => {
        if (images.length > 0 && !submitLoading) {
            const imageSelectionElement = document.getElementById('image-selection-section');
            if (imageSelectionElement) {
                setTimeout(() => {
                    imageSelectionElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 100);
            }
        }
    }, [images.length, submitLoading]);

    // Load session data on mount
    useEffect(() => {
        const loadSessionData = async () => {
            if (!sessionId) {
                console.error('No session ID provided');
                navigate('/sessions');
                return;
            }

            // Try to get data from navigation state first (passed from Sessions.js)
            const stateData = location.state;
            
            if (stateData) {
                // Check if data is passed directly or wrapped in sessionData
                const intTime = stateData.interruptionTime || (stateData.sessionData && stateData.sessionData.interruption && stateData.sessionData.interruption.duration);
                
                if (intTime) {
                    // Data was passed via navigation state - use it directly!
                    setInterruptionTime(intTime);
                    setLoadingSession(false);
                    return;
                }
            }

            // Fallback: if no state data, fetch from backend
            // This handles cases like page refresh or direct URL access
            setLoadingSession(true);
            try {
                const token = localStorage.getItem('token');
                
                const sessionResponse = await fetch(`/api/sessions/${sessionId}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (!sessionResponse.ok) {
                    throw new Error('Failed to load session');
                }

                const data = await sessionResponse.json();
                setInterruptionTime(data.interruption_time || 10);

            } catch (error) {
                console.error('Error loading session data:', error);
                alert('Erro ao carregar dados da sessão');
                navigate('/sessions');
            } finally {
                setLoadingSession(false);
            }
        };

        loadSessionData();
    }, [sessionId, navigate, location.state]);

    const handleSubmit = () => {
        searchImages(storyText, language, dataset);
    };

    const handleGenerateStory = () => {
        resetSaveState();
        generateStory(selectedImages, language);
    };

    const handleRegenerateClick = () => {
        handleGenerateStory();
    };

    const handleSave = async () => {
        await saveStory(responseText, selectedImages, dataset, language, storyData, sessionId); 
    };

    const handleContinue = async () => {
        await handleSave();
        setShowInterruption(true);
    };
    const handleClearSelections = () => {
        if (window.confirm(t('artExploration.confirmClearSelections'))) {
            clearSelections();
        }
    };
    const handleInterruptionComplete = () => {
        setShowInterruption(false);
        handleProceedToNextStep();
    };

    const handleProceedToNextStep = async () => {
        try {
            // Create evaluation before navigating
            const token = localStorage.getItem('token');
            const createResponse = await fetch(
                `/api/evaluation/create?session_id=${sessionId}`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    }
                }
            );

            if (!createResponse.ok) {
                throw new Error('Failed to create evaluation');
            }

            const createData = await createResponse.json();
            console.log('Evaluation created:', createData.id);

            const sessionData = {
                sessionId,
                mode: 'session',
                phase1: {
                    query: storyText || '',
                    language: language || 'en',
                    dataset: dataset || 'wikiart',
                    generatedStory: responseText || '',
                    selectedImages: (selectedImages || []).map(img => ({
                        url: img.url,
                        name: img.name,
                        id: img.id
                    }))
                },
                interruption: {
                    duration: interruptionTime || 10,
                    completed: true
                },
                timestamp: new Date().toISOString()
            };

            navigate(`/sessions/${sessionId}/art-exploration/evaluation`, {
                state: {
                    sessionData
                }
            });
        } catch (error) {
            console.error('Error creating evaluation:', error);
            alert('Erro ao iniciar avaliação. Tente novamente.');
        }
    };

    if (loadingSession) {
        return <div className="sessions-loading">{t('common.loading')}</div>;
    }

    return (
        <div>
            {/* Session Mode Banner */}
            <div className="session-mode-banner">
                <div className="banner-icon">🎯</div>
                <div className="banner-content">
                    <h3>{t('artExploration.sessionModeBanner.title')}</h3>
                    <p>{t('artExploration.sessionModeBanner.description')}</p>
                </div>
            </div>

            <InstructionsSection />

            <KeywordInputForm
                storyText={storyText}
                setStoryText={setStoryText}
                dataset={dataset}
                setDataset={setDataset}
                onSubmit={handleSubmit}
                isLoading={submitLoading}
            />

            <ImageSelection
                images={images}
                selectedImages={selectedImages}
                onImageToggle={handleImageToggle}
                onGenerateStory={handleGenerateStory}
                onClearSelections={handleClearSelections}
                isGenerating={generateLoading}
            />

            <GeneratedStory
                responseText={responseText}
                onRegenerate={handleRegenerateClick}
                onContinue={handleContinue}
                isGenerating={generateLoading}
                isSaving={isSaving}
                hasSaved={hasSaved}
                isSessionMode={true} // Session mode
            />

            {/* Interruption Modal */}
            <InterruptionModal
                isOpen={showInterruption}
                duration={interruptionTime}
                translationKey={INTERRUPTION_CONFIG.ART_EXPLORATION.translationKey}
                mode="art-exploration"
                onComplete={handleInterruptionComplete}
            />
        </div>
    );
};

export default ArtExplorationSession;
