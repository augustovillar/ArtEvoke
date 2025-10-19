import React from 'react';
import { useTranslation } from 'react-i18next';

const GeneratedStory = ({ 
    responseText, 
    onRegenerate, 
    onCopyToClipboard, 
    onSave, 
    isGenerating, 
    saveMessage,
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
                <button 
                    className="submit-button" 
                    onClick={onCopyToClipboard}
                >
                    {t('artExploration.copyText')}
                </button>
                <button 
                    className="submit-button" 
                    onClick={onSave}
                >
                    {isSessionMode 
                        ? (t('artExploration.continueToEvaluation') || 'Prosseguir para Avaliação')
                        : t('artExploration.saveToAccount')
                    }
                </button>
            </div>
            {saveMessage && <p>{saveMessage}</p>}
        </div>
    );
};

export default GeneratedStory;