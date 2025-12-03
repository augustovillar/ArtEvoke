import React from 'react';
import { useTranslation } from 'react-i18next';

const InstructionsSection = () => {
    const { t } = useTranslation();

    return (
        <div className="content-box">
            <div className="mode-title">{t('memoryReconstruction.modeTitle')}</div>
            <h1>{t('memoryReconstruction.pageTitle')}</h1>
            <p>{t('memoryReconstruction.description')}</p>
            <p><strong>{t('memoryReconstruction.optionsIntro')}</strong></p>
            <ol className="instructions-list">
                <li>{t('memoryReconstruction.instructions.step1')}</li>
                <li>{t('memoryReconstruction.instructions.step2')}</li>
                <li>{t('memoryReconstruction.instructions.step3')}</li>
                <li>{t('memoryReconstruction.instructions.step4')}</li>
            </ol>
        </div>
    );
};

export default InstructionsSection;
