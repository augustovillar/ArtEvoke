import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import SpeechInput from '../../../features/speech';

const KeywordInputForm = ({ 
    storyText, 
    setStoryText, 
    dataset, 
    setDataset, 
    onSubmit, 
    isLoading 
}) => {
    const { t } = useTranslation('common');
    const [isProcessingText, setIsProcessingText] = useState(false);
    const [displayText, setDisplayText] = useState(storyText);

    // Sync displayText with storyText when it changes externally
    useEffect(() => {
        if (!isProcessingText) {
            setDisplayText(storyText);
        }
    }, [storyText, isProcessingText]);

    const handleDatasetChange = (event) => {
        setDataset(event.target.value);
    };

    return (
        <div className="content-box">
            <h1>{t('artExploration.enterKeywords')}</h1>
            <div className="input-row">
                <textarea
                    className="art-exploration-textbox"
                    placeholder={t('artExploration.placeholder')}
                    value={displayText}
                    onChange={(e) => {
                        setDisplayText(e.target.value);
                        setStoryText(e.target.value);
                    }}
                    style={{
                        opacity: isProcessingText ? 0.6 : 1,
                        transition: 'opacity 0.3s ease'
                    }}
                    disabled={isProcessingText}
                />
                <div className="select-row">
                    <div className="select-group">
                        <label htmlFor="dataset-select-id" className="select-label">
                            {t('artExploration.selectDataset')}
                        </label>
                        <select
                            id="dataset-select-id"
                            className="language-select"
                            value={dataset}
                            onChange={handleDatasetChange}
                        >
                            <option value="wikiart">Wikiart</option>
                            <option value="semart">SemArt</option>
                            <option value="ipiranga">Ipiranga</option>
                        </select>
                    </div>
                </div>
            </div>
            <div className='input-buttons'>
                <button 
                    className="submit-button" 
                    onClick={onSubmit} 
                    disabled={isLoading}
                >
                    {isLoading ? t('artExploration.searching') : t('artExploration.submit')}
                </button>
                <SpeechInput 
                    onChange={(text) => {
                        setDisplayText(text);
                        setStoryText(text);
                    }}
                    initialValue={storyText}
                    onInterimText={(text, processing) => {
                        if (text !== null) {
                            setDisplayText(text);
                            if (!processing) {
                                setStoryText(text);
                            }
                        }
                        setIsProcessingText(processing || false);
                    }}
                    onProcessingChange={setIsProcessingText}
                />
            </div>
        </div>
    );
};

export default KeywordInputForm;