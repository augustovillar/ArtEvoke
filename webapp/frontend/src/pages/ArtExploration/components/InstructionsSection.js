import React, { useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useReadAloud } from '../../../contexts/ReadAloudContext';

const InstructionsSection = () => {
    const { t } = useTranslation('common');
    const contentRef = useRef(null);
    const { registerContent } = useReadAloud();

    useEffect(() => {
        registerContent(contentRef, [
            t('artExploration.description')
        ]);
        return () => registerContent(null);
    }, [registerContent, t]);

    return (
        <div className="content-box" ref={contentRef}>
            <div className="mode-title">{t('artExploration.modeTitle')}</div>
            <h1>{t('artExploration.pageTitle')}</h1>
            <p>{t('artExploration.description')}</p>
            <p><strong>{t('artExploration.optionsIntro')}</strong></p>
            <ol className="instructions-list">
                <li>{t('artExploration.instructions.step1')}</li>
                <li>{t('artExploration.instructions.step2')}</li>
                <li>{t('artExploration.instructions.step3')}</li>
                <li>{t('artExploration.instructions.step4')}</li>
            </ol>
        </div>
    );
};

export default InstructionsSection;