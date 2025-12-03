import React from 'react';
import { useTranslation } from 'react-i18next';

const ImageSelectionGrid = ({
    sectionsWithImages,
    selectedImagesPerSection,
    onImageClick,
    onInSession,
    onSave,
    onClearSelection,
    isSessionMode,
    loading,
    isSaving,
    hasSaved,
    storyText,
    saveMessage
}) => {
    const { t } = useTranslation();

    if (sectionsWithImages.length === 0) {
        return null;
    }

    return (
        <div id="image-selection-section" className="content-box">
            <h1>{t('memoryReconstruction.chooseImagesTitle')}</h1>
            {sectionsWithImages.map((sectionData, sectionIndex) => (
                <div key={sectionIndex} className="section-images-container">
                    {sectionData.section && (
                        <p>
                            <strong>{t('memoryReconstruction.sectionLabel')}</strong> {sectionData.section}
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
                                    alt={t('memoryReconstruction.imageAlt', { 
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
                {isSessionMode ? (
                    // Modo Sessão: botão de limpar seleção + botão de continuar para interrupção e avaliação
                    <>
                        <button
                            className="submit-button"
                            onClick={onClearSelection}
                            disabled={loading || Object.keys(selectedImagesPerSection).length === 0}
                        >
                            {t('memoryReconstruction.clearSelection') || 'Limpar Seleção'}
                        </button>
                        <button
                            className="submit-button"
                            onClick={onInSession}
                            disabled={
                                loading ||
                                isSaving ||
                                Object.keys(selectedImagesPerSection).length !== sectionsWithImages.length
                            }
                        >
                            {isSaving ? <span className="loading-spinner">◐</span> : (t('memoryReconstruction.continueSession') || 'Continuar Sessão')}
                        </button>
                    </>
                ) : (
                    // Modo Livre: botões de salvar e limpar
                    <>
                        <button
                            className="submit-button"
                            onClick={onClearSelection}
                            disabled={loading || Object.keys(selectedImagesPerSection).length === 0}
                        >
                            {t('memoryReconstruction.clearSelection') || 'Limpar Seleção'}
                        </button>
                        <button
                            className="submit-button"
                            onClick={onSave}
                            disabled={
                                loading || 
                                isSaving ||
                                hasSaved ||
                                Object.keys(selectedImagesPerSection).length !== sectionsWithImages.length
                            }
                        >
                            {isSaving ? <span className="loading-spinner">◐</span> : (hasSaved ? t('common.saved') : t('common.save'))}
                        </button>
                    </>
                )}
            </div>
        </div>
    );
};

export default ImageSelectionGrid;
