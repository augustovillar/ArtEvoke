// src/ArtExploration.js
import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';
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
    useStoryOutOfSessionSave
} from './components';

const ArtExploration = () => {
    const [searchParams] = useSearchParams();
    const location = useLocation();
    const navigate = useNavigate();

    // Get sessionId from URL params
    const sessionId = searchParams.get('sessionId');
    const interruptionTime = searchParams.get('interruptionTime');

    const [storyText, setStoryText] = useState('');
    const [language, setLanguage] = useState('en');
    const [dataset, setDataset] = useState('wikiart');

    // Interruption states
    const [showInterruption, setShowInterruption] = useState(false);
    
    // Session states
    const [loadingSession, setLoadingSession] = useState(false);
    const [evaluationId, setEvaluationId] = useState(null);

    // Check if in session mode
    const isSessionMode = !!sessionId;

    // Custom hooks
    const { images, submitLoading, searchImages } = useImageSearch();
    const { selectedImages, handleImageToggle, clearSelections } = useImageSelection();
    const { generateLoading, responseText, generateStory, copyToClipboard } = useStoryGeneration();
    const { saveMessage, saveOutOfSessionStory } = useStoryOutOfSessionSave();

    // Load existing evaluation data if in session mode
    useEffect(() => {
        const loadSessionData = async () => {
            if (!sessionId) return;

            setLoadingSession(true);
            try {
                const token = localStorage.getItem('token');
                const response = await fetch(`/api/sessions/${sessionId}/evaluation`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.art_exploration) {
                        const ae = data.art_exploration;
                        setEvaluationId(ae.id);
                        setLanguage(ae.language?.toLowerCase() || 'en');
                        setDataset(ae.dataset || 'wikiart');

                        // If images and story exist, pre-populate them
                        if (ae.story_generated) {
                            // This will be handled by the useStoryGeneration hook
                        }
                        if (ae.images && ae.images.length > 0) {
                            // Pre-populate selected images
                        }
                    }
                }
            } catch (error) {
                console.error('Error loading session data:', error);
            } finally {
                setLoadingSession(false);
            }
        };

        loadSessionData();
    }, [sessionId]);

    // Handle form submission to fetch images
    const handleSubmit = () => {
        searchImages(storyText, language, dataset);
    };

    // Handle story generation from selected images
    const handleGenerateStory = () => {
        generateStory(selectedImages);
    };

    // Copy generated story text to clipboard
    const handleCopyToClipboard = async () => {
        const result = await copyToClipboard();
        // Message is handled inside the hook
    };

    // Regenerate the story
    const handleRegenerateClick = () => {
        handleGenerateStory();
    };

    // Handler para modo sessão (inSession): vai para interrupção SEM salvar
    const handleInSession = () => {
        // No save here; just open the interruption modal. The save will be done in ArtEvaluation.
        setShowInterruption(true);
    };

    // Handler para modo livre (outOfSession): apenas salva
    const handleOutOfSession = async () => {
        const result = await saveOutOfSessionStory(responseText, selectedImages, sessionId, evaluationId);
        if (result.success) {
            if (sessionId) {
                // If in session mode, redirect to sessions page
                alert('Sessão completada com sucesso!');
                navigate('/sessions');
            } else {
                // Practice mode
                alert('História salva com sucesso!');
            }
        }
    };

    // Handler para limpar seleção (modo livre)
    const handleClearSelections = () => {
        if (window.confirm("Tem certeza que deseja limpar todas as seleções?")) {
            clearSelections();
        }
    };

    // Função chamada quando a interrupção é completada
    const handleInterruptionComplete = () => {
        setShowInterruption(false);
        handleProceedToNextStep();
    };

    // Função para prosseguir para próxima etapa
    const handleProceedToNextStep = () => {
        // Monta dados mínimos de sessão para avaliação
        const sessionData = {
            userId: 'test-user', // TODO: integrar com auth
            timestamp: new Date().toISOString(),
            mode: 'session',
            phase1: {
                query: storyText,
                language,
                dataset,
                generatedStory: responseText,
                selectedImages: selectedImages.map(img => ({
                    url: img.url,
                    name: img.name,
                    id: img.url
                }))
            },
            interruption: {
                task: INTERRUPTION_CONFIG.ART_EXPLORATION.translationKey,
                duration: INTERRUPTION_CONFIG.ART_EXPLORATION.duration,
                completed: true
            }
        };

        navigate('/art-exploration/evaluation', { state: { sessionData } });
    };

    return (
        <div>
            {/* Session Mode Banner */}
            {isSessionMode && (
                <div className="session-mode-banner">
                    <div className="banner-icon">🎯</div>
                    <div className="banner-content">
                        <h3>Modo Sessão Ativo</h3>
                        <p>Esta é uma avaliação formal que será salva para revisão médica.</p>
                    </div>
                </div>
            )}

            {!isSessionMode && (
                <div className="practice-mode-banner">
                    <div className="banner-icon">🎨</div>
                    <div className="banner-content">
                        <h3>Modo Prática</h3>
                        <p>Você está praticando. Seus dados serão salvos, mas não fazem parte de uma sessão formal.</p>
                    </div>
                </div>
            )}

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
                onCopyToClipboard={handleCopyToClipboard}
                onSave={isSessionMode ? handleInSession : handleOutOfSession}
                isGenerating={generateLoading}
                saveMessage={saveMessage}
                isSessionMode={isSessionMode}
            />

            {/* Modal de Interrupção */}
            <InterruptionModal
                isOpen={showInterruption}
                duration={INTERRUPTION_CONFIG.ART_EXPLORATION.duration}
                translationKey={INTERRUPTION_CONFIG.ART_EXPLORATION.translationKey}
                mode="art-exploration"
                onComplete={handleInterruptionComplete}
            />
        </div>
    );
};

export default ArtExploration;