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
    useStorySave
} from './components';

const ArtExploration = () => {
    const [storyText, setStoryText] = useState('');
    const [language, setLanguage] = useState('en');
    const [dataset, setDataset] = useState('wikiart');

    // Interruption states
    const [showInterruption, setShowInterruption] = useState(false);
    const [savedStoryData, setSavedStoryData] = useState(null);

    const location = useLocation();
    const navigate = useNavigate();

    // For testing, always show interruption. FUTURE: use location.state?.fromSession
    const shouldShowInterruption = true;

    // Custom hooks
    const { images, submitLoading, searchImages } = useImageSearch();
    const { selectedImages, handleImageToggle, clearSelections } = useImageSelection();
    const { generateLoading, responseText, generateStory, copyToClipboard } = useStoryGeneration();
    const { saveMessage, saveStory } = useStorySave();

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

    const handleSaveClick = async () => {
        const result = await saveStory(responseText, selectedImages);
        
        if (result.success && shouldShowInterruption) {
            setSavedStoryData(result.data);
            setShowInterruption(true);
        } else if (result.success) {
            handleProceedToNextStep(result.data);
        }
    };

    // Função chamada quando a interrupção é completada
    const handleInterruptionComplete = () => {
        setShowInterruption(false);
        handleProceedToNextStep(savedStoryData);
    };

    // Função para prosseguir para próxima etapa (preparado para futuras implementações)
    const handleProceedToNextStep = (data) => {
        console.log('Prosseguindo para avaliação (futuro) com:', data);
        // Futuro: navigate('/evaluation/art-exploration', { state: { data } });
        alert('Interrupção concluída — futuramente irá para avaliação.');
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
                onClearSelections={clearSelections}
                isGenerating={generateLoading}
            />

            <GeneratedStory
                responseText={responseText}
                onRegenerate={handleRegenerateClick}
                onCopyToClipboard={handleCopyToClipboard}
                onSave={handleSaveClick}
                isGenerating={generateLoading}
                saveMessage={saveMessage}
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