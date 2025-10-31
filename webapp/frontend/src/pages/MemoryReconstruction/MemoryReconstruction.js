import React, { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import './MemoryReconstruction.css';
import { useReadAloud } from '../../contexts/ReadAloudContext';
import InterruptionModal from '../../components/interruptionModal';
import { INTERRUPTION_CONFIG } from '../../config/interruption.config';

// Componentes
import InstructionsSection from './components/InstructionsSection';
import StoryInputForm from './components/StoryInputForm';
import ImageSelectionGrid from './components/ImageSelectionGrid';

// Hooks
import useStorySubmit from './hooks/useStorySubmit';
import useImageSelection from './hooks/useImageSelection';
import useStoryOutOfSessionSave from './hooks/useStoryOutOfSessionSave';

const MemoryReconstruction = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const contentRef = useRef(null);
    const { registerContent } = useReadAloud();

    // Get sessionId from URL params
    const sessionId = searchParams.get('sessionId');
    const interruptionTime = searchParams.get('interruptionTime');

    // Estados locais
    const [storyText, setStoryText] = useState('');
    const [language, setLanguage] = useState('en');
    const [dataset, setDataset] = useState('wikiart');
    const [segmentation, setSegmentation] = useState('conservative');
    const [showInterruption, setShowInterruption] = useState(false);
    const [loadingSession, setLoadingSession] = useState(false);
    const [evaluationId, setEvaluationId] = useState(null);

    // Hooks personalizados
    const { 
        sectionsWithImages, 
        loading, 
        submitStory 
    } = useStorySubmit();

    const { 
        selectedImagesPerSection, 
        selectImage, 
        clearSelection 
    } = useImageSelection();

    const { 
        saveMessage, 
        saveOutOfSessionStory 
    } = useStoryOutOfSessionSave();

    // Check if in session mode
    const isSessionMode = !!sessionId;

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
                    if (data.memory_reconstruction) {
                        const mr = data.memory_reconstruction;
                        setEvaluationId(mr.id);
                        setStoryText(mr.story || '');
                        setLanguage(mr.language?.toLowerCase() || 'en');
                        setDataset(mr.dataset || 'wikiart');
                        setSegmentation(mr.segmentation_strategy?.toLowerCase() || 'conservative');

                        // If sections exist, pre-populate the story submission
                        if (mr.sections && mr.sections.length > 0) {
                            // Reconstruct sections data for the UI
                            // This will be handled by the useStorySubmit hook
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

    useEffect(() => {
        registerContent(contentRef, [
            "In the box below, you can enter text, or click a button to speak the words instead of typing.",
            "To the right of the text box, you can select the language for processing the story.",
            "Finally, there is a submit button to click once you are done inputting the text."
        ]);
        return () => registerContent(null);
    }, [registerContent]);

    const handleSubmit = () => {
        clearSelection();
        // Sempre mostrar 6 imagens por seção
        submitStory(storyText, language, dataset, segmentation, 6);
    };

    // Handler para modo sessão (inSession): salva e vai para interrupção
    const handleInSession = () => {
        // No save here; just open the interruption modal. The save will be done in MemoryEvaluation.
        setShowInterruption(true);
    };

    // Handler para modo livre (outOfSession): apenas salva
    const handleOutOfSession = async () => {
        const result = await saveOutOfSessionStory(
            storyText,
            selectedImagesPerSection,
            sectionsWithImages,
            language,
            dataset,
            segmentation,
            sessionId,
            evaluationId
        );
        
        if (result.success) {
            if (sessionId) {
                // If in session mode, redirect to sessions page
                alert("Sessão completada com sucesso!");
                navigate('/sessions');
            } else {
                // Practice mode
                alert("História salva com sucesso!");
            }
        }
    };

    // Handler para limpar seleção (modo livre)
    const handleClearSelection = () => {
        if (window.confirm("Tem certeza que deseja limpar todas as seleções?")) {
            clearSelection();
        }
    };

    const handleInterruptionComplete = () => {
        setShowInterruption(false);
        handleProceedToNextStep();
    };

    const handleProceedToNextStep = () => {
        console.log("Prosseguindo para avaliação...");
        // Dados serão montados a partir do estado atual (não do savedStoryData)
        
        // Navegar para página de avaliação com dados da sessão
        navigate('/memory-reconstruction/evaluation', { 
            state: { 
                sessionData: {
                    userId: 'test-user', // TODO: pegar do contexto de autenticação
                    timestamp: new Date().toISOString(),
                    mode: 'session',
                    phase1: {
                        story: storyText,
                        language,
                        dataset,
                        segmentation,
                        sections: sectionsWithImages.map((section, index) => ({
                            sectionId: index,
                            sectionText: section.section,
                            imagesShown: section.images.map(img => ({
                                url: img.url,
                                name: img.name
                            })),
                            selectedImage: {
                                url: selectedImagesPerSection[index],
                                name: section.images.find(img => img.url === selectedImagesPerSection[index])?.name
                            }
                        }))
                    },
                    interruption: {
                        task: INTERRUPTION_CONFIG.MEMORY_RECONSTRUCTION.translationKey,
                        duration: INTERRUPTION_CONFIG.MEMORY_RECONSTRUCTION.duration,
                        completed: true
                    }
                }
            } 
        });
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

            <div ref={contentRef}>
                <InstructionsSection />

                <StoryInputForm
                    storyText={storyText}
                    onStoryTextChange={setStoryText}
                    language={language}
                    onLanguageChange={(e) => setLanguage(e.target.value)}
                    dataset={dataset}
                    onDatasetChange={(e) => setDataset(e.target.value)}
                    segmentation={segmentation}
                    onSegmentationChange={(e) => setSegmentation(e.target.value)}
                    onSubmit={handleSubmit}
                    loading={loading}
                />

                <ImageSelectionGrid
                    sectionsWithImages={sectionsWithImages}
                    selectedImagesPerSection={selectedImagesPerSection}
                    onImageClick={selectImage}
                    onInSession={handleInSession}
                    onOutOfSession={handleOutOfSession}
                    onClearSelection={handleClearSelection}
                    isSessionMode={isSessionMode}
                    loading={loading}
                    storyText={storyText}
                    saveMessage={saveMessage}
                />
            </div>

            {/* Modal de Interrupção */}
            <InterruptionModal
                isOpen={showInterruption}
                duration={INTERRUPTION_CONFIG.MEMORY_RECONSTRUCTION.duration}
                translationKey={INTERRUPTION_CONFIG.MEMORY_RECONSTRUCTION.translationKey}
                mode="memory-reconstruction"
                onComplete={handleInterruptionComplete}
            />
        </div>
    );
};

export default MemoryReconstruction;
