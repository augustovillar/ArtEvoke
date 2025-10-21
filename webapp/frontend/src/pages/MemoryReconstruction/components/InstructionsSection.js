import React from 'react';
import { useTranslation } from 'react-i18next';

const InstructionsSection = () => {
    const { t } = useTranslation();

    return (
        <div className="content-box">
            <h1>{t('memoryReconstruction.pageTitle')}</h1>
            <p>
                {t('memoryReconstruction.description')}
                <br />
                <br />
                {t('memoryReconstruction.optionsIntro')}
            </p>
            <ol className="instructions-list">
                <li>{t('memoryReconstruction.instructions.language')}</li>
                <li>{t('memoryReconstruction.instructions.dataset')}</li>
                <li>{t('memoryReconstruction.instructions.segmentation')}</li>
            </ol>
        </div>
    );
};

export default InstructionsSection;
