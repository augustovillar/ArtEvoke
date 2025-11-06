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

    const { t } = useTranslation('common');

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
            const sessionData = location.state;
            
            if (sessionData && sessionData.artExplorationId && sessionData.interruptionTime) {
                // Data was passed via navigation state - use it directly!
                setArtExplorationId(sessionData.artExplorationId);
                setInterruptionTime(sessionData.interruptionTime);
                setLoadingSession(false);
                return;
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

    // Handle form submission to fetch images
    const handleSubmit = () => {
        searchImages(storyText, language, dataset);
    };

    // Handle story generation from selected images
    const handleGenerateStory = () => {
        resetSaveState();
        generateStory(selectedImages);
    };

    // Regenerate the story
    const handleRegenerateClick = () => {
        handleGenerateStory();
    };

    // Handler for saving in session mode
    const handleSave = async () => {
        await saveStory(responseText, selectedImages, dataset, language, artExplorationId); // Pass artExplorationId for session mode
    };

    // Handler to continue to interruption
    const handleContinue = async () => {
        await handleSave();
        setShowInterruption(true);
    };

    // Handler to clear selections
    const handleClearSelections = () => {
        if (window.confirm(t('artExploration.confirmClearSelections'))) {
            clearSelections();
        }
    };

    // Function called when interruption is completed
    const handleInterruptionComplete = () => {
        setShowInterruption(false);
        handleProceedToNextStep();
    };

    // Function to proceed to next step (evaluation)
    const handleProceedToNextStep = () => {
        navigate(`/sessions/${sessionId}/art-exploration/evaluation`, {
            state: {
                artExplorationId,
                sessionId,
                generatedStory: responseText,
                selectedImages: selectedImages.map(img => ({
                    url: img.url,
                    name: img.name,
                    id: img.id
                }))
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
