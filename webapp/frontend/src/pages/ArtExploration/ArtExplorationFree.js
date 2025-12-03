// src/pages/ArtExploration/ArtExplorationFree.js
import React, { useState } from 'react';
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

    // Get language from i18n
    const language = i18n.language.split('-')[0]; // 'pt-BR' -> 'pt'

    // Custom hooks
    const { images, submitLoading, searchImages } = useImageSearch();
    const { selectedImages, handleImageToggle, clearSelections } = useImageSelection();
    const { generateLoading, responseText, storyData, generateStory } = useStoryGeneration();
    const { isSaving, hasSaved, saveStory, resetSaveState } = useSave();

    const handleSubmit = () => {
        searchImages(storyText, language, dataset);
    };

    const handleGenerateStory = () => {
        resetSaveState();
        generateStory(selectedImages);
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
