// src/ArtExploration.js
import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
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
    const [storyText, setStoryText] = useState('');
    const [language, setLanguage] = useState('en');
    const [dataset, setDataset] = useState('wikiart');

    // Interruption states
    const [showInterruption, setShowInterruption] = useState(false);

    const location = useLocation();
    const navigate = useNavigate();

    // Verifica se está em modo sessão (com interrupção e avaliação)
    // PARA TESTE: deixado como true para sempre mostrar a interrupção
    // FUTURO: quando vier das sessões, trocar por: location.state?.isSessionMode || false
    const isSessionMode = true;

    // Custom hooks
    const { images, submitLoading, searchImages } = useImageSearch();
    const { selectedImages, handleImageToggle, clearSelections } = useImageSelection();
    const { generateLoading, responseText, generateStory, copyToClipboard } = useStoryGeneration();
    const { saveMessage, saveOutOfSessionStory } = useStoryOutOfSessionSave();

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
        const result = await saveOutOfSessionStory(responseText, selectedImages);
        if (result.success) {
            alert('História salva com sucesso!');
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