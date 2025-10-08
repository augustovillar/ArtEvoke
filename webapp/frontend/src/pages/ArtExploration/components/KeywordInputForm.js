import React from 'react';
import { useTranslation } from 'react-i18next';
import SpeechInput from '../../../features/speech';

const KeywordInputForm = ({ 
    storyText, 
    setStoryText, 
    language, 
    setLanguage, 
    dataset, 
    setDataset, 
    onSubmit, 
    isLoading 
}) => {
    const { t } = useTranslation('common');

    const handleLanguageChange = (event) => {
        setLanguage(event.target.value);
    };

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
                    value={storyText}
                    onChange={(e) => setStoryText(e.target.value)}
                />
                <div className="select-row">
                    <div className="select-group">
                        <label htmlFor="language-select-id" className="select-label">
                            {t('artExploration.selectLanguage')}
                        </label>
                        <select
                            id="language-select-id"
                            className="language-select"
                            value={language}
                            onChange={handleLanguageChange}
                        >
                            <option value="en">English</option>
                            <option value="fr">French</option>
                            <option value="nl">Dutch</option>
                            <option value="es">Spanish</option>
                            <option value="pt">Portuguese</option>
                            <option value="de">German</option>
                        </select>
                    </div>
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
                <SpeechInput onChange={setStoryText} initialValue={storyText} />
            </div>
        </div>
    );
};

export default KeywordInputForm;