import React from 'react';
import { useTranslation } from 'react-i18next';

const GeneratedStory = ({ 
    responseText, 
    onRegenerate, 
    onSave, 
    isGenerating,
    isSaving,
    hasSaved,
    saveMessage,
    isSessionMode,
    onDirectSave 
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
                <button 
                    className="submit-button" 
                    onClick={onDirectSave}
                    disabled={isSaving || hasSaved}
                >
                    {isSaving ? <span className="loading-spinner">◐</span> : t('common.save')}
                </button>
                <button 
                    className="submit-button" 
                    onClick={onSave}
                    disabled={isSessionMode ? isSaving : (isSaving || hasSaved)}
                >
                    {isSessionMode 
                        ? (isSaving ? <span className="loading-spinner">◐</span> : t('artExploration.continueToEvaluation'))
                        : (isSaving ? <span className="loading-spinner">◐</span> : t('common.save'))
                    }
                </button>
            </div>
        </div>
    );
};

export default GeneratedStory;