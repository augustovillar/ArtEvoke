import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import './MemoryReconstruction.css';
import { useReadAloud } from '../../contexts/ReadAloudContext';

import InstructionsSection from './components/InstructionsSection';
import StoryInputForm from './components/StoryInputForm';
import ImageSelectionGrid from './components/ImageSelectionGrid';

import useStorySubmit from './hooks/useStorySubmit';
import useImageSelection from './hooks/useImageSelection';
import useSave from './hooks/useSave';

const MemoryReconstructionFree = () => {
    const contentRef = useRef(null);
    const { registerContent } = useReadAloud();
    const { t, i18n } = useTranslation('common');

    const [storyText, setStoryText] = useState('');
    const [dataset, setDataset] = useState('wikiart');
    const [segmentation, setSegmentation] = useState('conservative');

    // Get language from i18n
    const language = i18n.language.split('-')[0]; // 'pt-BR' -> 'pt'

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
    
    const handleImageSelect = (imageObject, sectionIndex) => {
        selectImage(imageObject, sectionIndex);
        resetSaveState();
    };

    const { 
        saveMessage,
        isSaving,
        hasSaved,
        saveStory,
        resetSaveState
    } = useSave();

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
        resetSaveState();
        submitStory(storyText, language, dataset, segmentation, 6);
    };

    const handleSave = async () => {
        await saveStory(
            storyText,
            selectedImagesPerSection,
            sectionsWithImages,
            language,
            dataset,
            segmentation
        );
    };

    const handleClearSelection = () => {
        if (window.confirm(t('memoryReconstruction.confirmClearSelection'))) {
            clearSelection();
        }
    };

    return (
        <div>
            <div className="practice-mode-banner">
                <div className="banner-icon">🎨</div>
                <div className="banner-content">
                    <h3>{t('memoryReconstruction.practiceModeBanner.title')}</h3>
                    <p>{t('memoryReconstruction.practiceModeBanner.description')}</p>
                </div>
            </div>

            <div ref={contentRef}>
                <InstructionsSection />

                <StoryInputForm
                    storyText={storyText}
                    onStoryTextChange={setStoryText}
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
                    onImageClick={handleImageSelect}
                    onSave={handleSave}
                    onClearSelection={handleClearSelection}
                    isSessionMode={false}
                    loading={loading}
                    isSaving={isSaving}
                    hasSaved={hasSaved}
                    storyText={storyText}
                    saveMessage={saveMessage}
                />
            </div>
        </div>
    );
};

export default MemoryReconstructionFree;
