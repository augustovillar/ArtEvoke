import React from 'react';
import { useTranslation } from 'react-i18next';

const GeneratedStory = ({ 
    responseText, 
    onRegenerate, 
    onSave,
    onContinue,
    isGenerating,
    isSaving,
    hasSaved,
    isSessionMode
}) => {
    const { t } = useTranslation('common');

    if (!responseText) {
        return null;
    }

    return (
        <div id='generated-story' className="content-box">
            <h1>{t('artExploration.aiGeneratedStory')}</h1>
            <p>{responseText}</p>
            <div className="buttons-container">
                <button 
                    className="submit-button" 
                    onClick={onRegenerate} 
                    disabled={isGenerating}
                >
                    {t('artExploration.regenerateStory')}
                </button>
                {isSessionMode ? (
                    // Modo Sessão: apenas botão de continuar para avaliação (já inclui o save)
                    <button
                        className="submit-button"
                        onClick={onContinue}
                        disabled={isSaving}
                    >
                        {isSaving ? <span className="loading-spinner">◐</span> : t('artExploration.continueToEvaluation')}
                    </button>
                ) : (
                    // Modo Livre: botão de salvar
                    <button
                        className="submit-button"
                        onClick={onSave}
                        disabled={isSaving || hasSaved}
                    >
                        {isSaving ? <span className="loading-spinner">◐</span> : (hasSaved ? t('common.saved') : t('common.save'))}
                    </button>
                )}
            </div>
        </div>
    );
};

export default GeneratedStory;