import React from 'react';
import { useTranslation } from 'react-i18next';
import SpeechInput from '../../../features/speech';

const StoryInputForm = ({
    storyText,
    onStoryTextChange,
    language,
    onLanguageChange,
    dataset,
    onDatasetChange,
    segmentation,
    onSegmentationChange,
    onSubmit,
    loading
}) => {
    const { t } = useTranslation();

    return (
        <div className="content-box">
            <h1>{t('story.writeStoryTitle')}</h1>
            <div className="input-row">
                <textarea
                    className="story-textbox"
                    placeholder={t('story.textareaPlaceholder')}
                    value={storyText}
                    onChange={(e) => onStoryTextChange(e.target.value)}
                />
                <div className="select-row">
                    <div className="select-group">
                        <label htmlFor="language-select-id" className="select-label">
                            {t('story.selectLanguage')}
                        </label>
                        <select
                            id="language-select-id"
                            className="language-select"
                            value={language}
                            onChange={onLanguageChange}
                        >
                            <option value="en">{t('story.languages.en')}</option>
                            <option value="fr">{t('story.languages.fr')}</option>
                            <option value="nl">{t('story.languages.nl')}</option>
                            <option value="es">{t('story.languages.es')}</option>
                            <option value="pt">{t('story.languages.pt')}</option>
                            <option value="de">{t('story.languages.de')}</option>
                        </select>
                    </div>
                    <div className="select-group">
                        <label htmlFor="dataset-select-id" className="select-label">
                            {t('story.selectDataset')}
                        </label>
                        <select
                            id="dataset-select-id"
                            className="language-select"
                            value={dataset}
                            onChange={onDatasetChange}
                        >
                            <option value="wikiart">Wikiart</option>
                            <option value="semart">SemArt</option>
                            <option value="ipiranga">Ipiranga</option>
                        </select>
                    </div>
                    <div className="select-group">
                        <label htmlFor="segmentation-select-id" className="select-label">
                            {t('story.imageSelection')}
                        </label>
                        <select
                            id="segmentation-select-id"
                            className="language-select"
                            value={segmentation}
                            onChange={onSegmentationChange}
                        >
                            <option value="conservative">{t('story.segmentationOptions.conservative')}</option>
                            <option value="broader">{t('story.segmentationOptions.broader')}</option>
                        </select>
                    </div>
                </div>
            </div>
            <div className='input-buttons'>
                <button 
                    className="submit-button" 
                    onClick={() => onSubmit(1)} 
                    disabled={loading || !storyText.trim()}
                >
                    {loading ? t('story.searching') : t('story.submitButton')}
                </button>
                <SpeechInput onChange={onStoryTextChange} initialValue={storyText} />
            </div>
        </div>
    );
};

export default StoryInputForm;
