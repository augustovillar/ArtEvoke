// src/pages/ArtExploration/ArtExplorationFree.js
import React, { useState, useMemo, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import './ArtExploration.css';
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

const ArtExplorationFree = () => {
    const [storyText, setStoryText] = useState('');
    const [dataset, setDataset] = useState('wikiart');

    const { t, i18n } = useTranslation('common');

    // Get language from i18n - reactive to language changes
    const language = useMemo(() => {
        const lang = i18n.resolvedLanguage || i18n.language || localStorage.getItem('i18nextLng') || 'en';
        return lang.split('-')[0].toLowerCase();
    }, [i18n.language, i18n.resolvedLanguage]);

    // Custom hooks
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
        await saveStory(responseText, selectedImages, dataset, language, storyData);
    };

    // Handler to clear selections
    const handleClearSelections = () => {
        if (window.confirm(t('artExploration.confirmClearSelections'))) {
            clearSelections();
        }
    };

    return (
        <div>
            {/* Practice Mode Banner */}
            <div className="practice-mode-banner">
                <div className="banner-icon">🎨</div>
                <div className="banner-content">
                    <h3>{t('artExploration.practiceModeBanner.title')}</h3>
                    <p>{t('artExploration.practiceModeBanner.description')}</p>
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
                onSave={handleSave}
                isGenerating={generateLoading}
                isSaving={isSaving}
                hasSaved={hasSaved}
                isSessionMode={false} // Free mode = not session mode
            />
        </div>
    );
};

export default ArtExplorationFree;
