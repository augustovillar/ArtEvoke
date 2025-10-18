import React, { useState, useRef, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
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
import useStorySave from './hooks/useStorySave';

const MemoryReconstruction = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const contentRef = useRef(null);
    const { registerContent } = useReadAloud();

    // Estados locais
    const [storyText, setStoryText] = useState('');
    const [language, setLanguage] = useState('en');
    const [dataset, setDataset] = useState('wikiart');
    const [segmentation, setSegmentation] = useState('conservative');
    const [showInterruption, setShowInterruption] = useState(false);

    // Hooks personalizados
    const { 
        sectionsWithImages, 
        loading, 
        numImagesPerSection, 
        submitStory 
    } = useStorySubmit();

    const { 
        selectedImagesPerSection, 
        selectImage, 
        clearSelection 
    } = useImageSelection();

    const { 
        saveMessage, 
        savedStoryData, 
        saveStory 
    } = useStorySave();

    // Verifica se deve mostrar interrupção 
    // PARA TESTE: deixado como true para sempre mostrar a interrupção
    // FUTURO: quando vier das sessões, trocar por: location.state?.fromSession || false
    const shouldShowInterruption = true;

    useEffect(() => {
        registerContent(contentRef, [
            "In the box below, you can enter text, or click a button to speak the words instead of typing.",
            "To the right of the text box, you can select the language for processing the story.",
            "Finally, there is a submit button to click once you are done inputting the text."
        ]);
        return () => registerContent(null);
    }, [registerContent]);

    const handleSubmit = (k) => {
        clearSelection();
        submitStory(storyText, language, dataset, segmentation, k);
    };

    const handleSaveClick = () => {
        saveStory(
            storyText,
            selectedImagesPerSection,
            sectionsWithImages,
            language,
            dataset,
            segmentation,
            shouldShowInterruption,
            (storyData) => {
                setShowInterruption(true);
            }
        );
    };

    const handleRequestMoreImages = () => {
        handleSubmit(5);
    };

    const handleInterruptionComplete = () => {
        setShowInterruption(false);
        handleProceedToNextStep(savedStoryData);
    };

    const handleProceedToNextStep = (storyData) => {
        console.log("Prosseguindo para próxima etapa (avaliação futura)...");
        console.log("Story Data:", storyData);
        
        // Futuro: navigate('/evaluation/memory-reconstruction', { 
        //     state: { 
        //         storyData,
        //         mode: 'memory_reconstruction'
        //     } 
        // });
        
        alert("Etapa concluída! (Futuramente será redirecionado para avaliação)");
    };

    return (
        <div>
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
                    onRequestMoreImages={handleRequestMoreImages}
                    onSaveClick={handleSaveClick}
                    numImagesPerSection={numImagesPerSection}
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
                onComplete={handleInterruptionComplete}
            />
        </div>
    );
};

export default MemoryReconstruction;
