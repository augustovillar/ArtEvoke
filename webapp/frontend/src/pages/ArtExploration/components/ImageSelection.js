import React from 'react';
import { useTranslation } from 'react-i18next';

const ImageSelection = ({ 
    images, 
    selectedImages, 
    onImageToggle, 
    onGenerateStory, 
    onClearSelections, 
    isGenerating 
}) => {
    const { t } = useTranslation('common');

    if (images.length === 0 && selectedImages.length === 0) {
        return null;
    }

    return (
        <div id="image-selection-section" className="content-box">
            <h1>{t('artExploration.imageSelection')}</h1>
            <p>{t('artExploration.imageSelectionDesc')}</p>
            <div className="images-grid">
                {/* Display currently searched images */}
                {images.map((image) => (
                    <div
                        key={`search-${image.url}`}
                        className={`image-container ${selectedImages.some(img => img.url === image.url) ? 'selected' : ''}`}
                        onClick={() => onImageToggle(image)}
                    >
                        <img
                            src={image.url}
                            alt={t('artExploration.generatedImageAlt', { name: image.name })}
                            className="generated-image"
                        />
                        <span className="image-name">{image.name}</span>
                    </div>
                ))}

                {/* Display already selected images that are NOT in the current search results */}
                {selectedImages.map((selectedImage) => {
                    const isAlreadyDisplayed = images.some(img => img.url === selectedImage.url);
                    if (!isAlreadyDisplayed) {
                        return (
                            <div
                                key={`selected-${selectedImage.url}`}
                                className="image-container selected"
                                onClick={() => onImageToggle(selectedImage)}
                            >
                                <img
                                    src={selectedImage.url}
                                    alt={t('artExploration.selectedImageAlt', { name: selectedImage.name })}
                                    className="generated-image"
                                />
                                <span className="image-name">{selectedImage.name}</span>
                            </div>
                        );
                    }
                    return null;
                })}
            </div>
            <div className="buttons-container">
                <button
                    className="submit-button"
                    onClick={onGenerateStory}
                    disabled={isGenerating || selectedImages.length === 0}
                >
                    {isGenerating ? t('artExploration.generatingStory') : t('artExploration.generateStory', { count: selectedImages.length })}
                </button>
                <button
                    className="submit-button"
                    onClick={onClearSelections}
                    disabled={selectedImages.length === 0}
                >
                    {t('artExploration.clearSelections')}
                </button>
            </div>
        </div>
    );
};

export default ImageSelection;