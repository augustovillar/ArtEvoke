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
    const [language, setLanguage] = useState('en');
    const [dataset, setDataset] = useState('wikiart');

    const { t } = useTranslation('common');

    // Custom hooks
    const { images, submitLoading, searchImages } = useImageSearch();
    const { selectedImages, handleImageToggle, clearSelections } = useImageSelection();
    const { generateLoading, responseText, generateStory } = useStoryGeneration();
    const { isSaving, hasSaved, saveStory, resetSaveState } = useSave();

    // Handle form submission to fetch images
    const handleSubmit = () => {
        searchImages(storyText, language, dataset);
    };

    // Handle story generation from selected images
    const handleGenerateStory = () => {
        resetSaveState(); // Reset save state when generating new story
        generateStory(selectedImages);
    };

    // Regenerate the story
    const handleRegenerateClick = () => {
        handleGenerateStory();
    };

    // Handler for saving in free mode (not in session)
    const handleSave = async () => {
        await saveStory(responseText, selectedImages, dataset, language); // No artExplorationId = free mode
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
                    <h3>Modo Prática</h3>
                    <p>Você está praticando. Seus dados serão salvos no seu perfil, mas não fazem parte de uma sessão formal.</p>
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
