// src/pages/ArtExploration/ArtExplorationSession.js
import React, { useState, useEffect } from 'react';
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
    const [language, setLanguage] = useState('en');
    const [dataset, setDataset] = useState('wikiart');

    // Interruption states
    const [showInterruption, setShowInterruption] = useState(false);
    const [interruptionTime, setInterruptionTime] = useState(10);
    
    // Session states
    const [loadingSession, setLoadingSession] = useState(false);
    const [artExplorationId, setArtExplorationId] = useState(null);

    const { t, i18n } = useTranslation('common');

    // Sync language state with i18n language
    useEffect(() => {
        const currentLang = i18n.language.split('-')[0]; // 'pt-BR' -> 'pt'
        if (currentLang === 'en' || currentLang === 'pt') {
            setLanguage(currentLang);
        }
    }, [i18n.language]);

    // Custom hooks
    const { images, submitLoading, searchImages } = useImageSearch();
    const { selectedImages, handleImageToggle, clearSelections } = useImageSelection();
    const { generateLoading, responseText, generateStory } = useStoryGeneration();
    const { isSaving, hasSaved, saveStory, resetSaveState } = useSave();

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
                const artExpId = stateData.artExplorationId || (stateData.sessionData && stateData.sessionData.artExplorationId);
                const intTime = stateData.interruptionTime || (stateData.sessionData && stateData.sessionData.interruption && stateData.sessionData.interruption.duration);
                
                if (artExpId && intTime) {
                    // Data was passed via navigation state - use it directly!
                    setArtExplorationId(artExpId);
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
                setArtExplorationId(data.art_exploration_id);

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
        resetSaveState(); // Reset save state when generating new story
        generateStory(selectedImages, language);
    };

    const handleRegenerateClick = () => {
        handleGenerateStory();
    };

    const handleSave = async () => {
        await saveStory(responseText, selectedImages, dataset, language, artExplorationId); 
    };

    const handleContinue = async () => {
        console.log('handleContinue called - saving and starting interruption');
        await handleSave();
        setShowInterruption(true);
    };
    const handleClearSelections = () => {
        if (window.confirm(t('artExploration.confirmClearSelections'))) {
            clearSelections();
        }
    };
    const handleInterruptionComplete = () => {
        console.log('handleInterruptionComplete called - proceeding to next step');
        setShowInterruption(false);
        handleProceedToNextStep();
    };

    const handleProceedToNextStep = () => {
        // Create sessionData object that matches what ArtEvaluation expects
        const sessionData = {
            sessionId,
            artExplorationId,
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

        console.log('Navigating to evaluation with sessionData:', sessionData);
        console.log('sessionId:', sessionId);
        console.log('artExplorationId:', artExplorationId);
        console.log('responseText:', responseText);
        console.log('selectedImages:', selectedImages);
        
        navigate(`/sessions/${sessionId}/art-exploration/evaluation`, {
            state: {
                sessionData
            }
        });
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
                    <h3>Modo Sessão Ativo</h3>
                    <p>Esta é uma avaliação formal que será salva para revisão médica.</p>
                </div>
            </div>

            <InstructionsSection />

            <KeywordInputForm
                storyText={storyText}
                setStoryText={setStoryText}
                language={language}
                setLanguage={setLanguage}
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
