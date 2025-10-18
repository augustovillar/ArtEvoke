import React from 'react';
import { useTranslation } from 'react-i18next';

const InstructionsSection = () => {
    const { t } = useTranslation();

    return (
        <div className="content-box">
            <h1>{t('story.pageTitle')}</h1>
            <p>
                {t('story.description')}
                <br />
                <br />
                {t('story.optionsIntro')}
            </p>
            <ol className="instructions-list">
                <li>{t('story.instructions.language')}</li>
                <li>{t('story.instructions.dataset')}</li>
                <li>{t('story.instructions.segmentation')}</li>
            </ol>
        </div>
    );
};

export default InstructionsSection;
