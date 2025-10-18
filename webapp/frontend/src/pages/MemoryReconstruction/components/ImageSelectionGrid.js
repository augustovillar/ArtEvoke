import React from 'react';
import { useTranslation } from 'react-i18next';

const ImageSelectionGrid = ({
    sectionsWithImages,
    selectedImagesPerSection,
    onImageClick,
    onRequestMoreImages,
    onSaveClick,
    numImagesPerSection,
    loading,
    storyText,
    saveMessage
}) => {
    const { t } = useTranslation();

    if (sectionsWithImages.length === 0) {
        return null;
    }

    return (
        <div className="content-box">
            <h1>{t('story.chooseImagesTitle')}</h1>
            {sectionsWithImages.map((sectionData, sectionIndex) => (
                <div key={sectionIndex} className="section-images-container">
                    {sectionData.section && (
                        <p>
                            <strong>{t('story.sectionLabel')}</strong> {sectionData.section}
                        </p>
                    )}
                    <div className="images-grid">
                        {sectionData.images.map((imageItem, imageIndex) => (
                            <div
                                key={`${sectionIndex}-${imageIndex}`}
                                className={`image-container ${
                                    selectedImagesPerSection[sectionIndex] === imageItem.url 
                                        ? 'selected' 
                                        : ''
                                }`}
                                onClick={() => onImageClick(imageItem, sectionIndex)}
                            >
                                <img
                                    src={imageItem.url}
                                    alt={t('story.imageAlt', { 
                                        sectionIndex: sectionIndex + 1, 
                                        imageIndex: imageIndex + 1 
                                    })}
                                    className="generated-image"
                                />
                                <span className="image-name">{imageItem.name}</span>
                            </div>
                        ))}
                    </div>
                </div>
            ))}
            <div className="buttons-container">
                {numImagesPerSection === 1 && (
                    <button
                        className="submit-button"
                        onClick={onRequestMoreImages}
                        disabled={loading || !storyText.trim()}
                    >
                        {t('story.showMoreImages')}
                    </button>
                )}
                <button
                    className="submit-button"
                    onClick={onSaveClick}
                    disabled={
                        loading || 
                        Object.keys(selectedImagesPerSection).length !== sectionsWithImages.length
                    }
                >
                    {t('story.saveStory')}
                </button>
            </div>
            {saveMessage && <p>{saveMessage}</p>}
        </div>
    );
};

export default ImageSelectionGrid;
