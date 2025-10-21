import React from 'react';
import { useTranslation } from 'react-i18next';

const ImageSelectionGrid = ({
    sectionsWithImages,
    selectedImagesPerSection,
    onImageClick,
    onInSession,
    onOutOfSession,
    onClearSelection,
    isSessionMode,
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
                    // Modo Sessão: apenas botão de continuar para interrupção e avaliação
                    <button
                        className="submit-button primary-button"
                        onClick={onInSession}
                        disabled={
                            loading || 
                            Object.keys(selectedImagesPerSection).length !== sectionsWithImages.length
                        }
                    >
                        {t('memoryReconstruction.continueSession') || 'Continuar Sessão'}
                    </button>
                ) : (
                    // Modo Livre: botões de salvar e limpar
                    <>
                        <button
                            className="submit-button secondary-button"
                            onClick={onClearSelection}
                            disabled={loading || Object.keys(selectedImagesPerSection).length === 0}
                        >
                            {t('memoryReconstruction.clearSelection') || 'Limpar Seleção'}
                        </button>
                        <button
                            className="submit-button primary-button"
                            onClick={onOutOfSession}
                            disabled={
                                loading || 
                                Object.keys(selectedImagesPerSection).length !== sectionsWithImages.length
                            }
                        >
                            {t('memoryReconstruction.saveStory') || 'Salvar História'}
                        </button>
                    </>
                )}
            </div>
            {saveMessage && <p>{saveMessage}</p>}
        </div>
    );
};

export default ImageSelectionGrid;
