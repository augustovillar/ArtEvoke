import React, { useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useReadAloud } from '../../../contexts/ReadAloudContext';

const InstructionsSection = () => {
    const { t } = useTranslation('common');
    const contentRef = useRef(null);
    const { registerContent } = useReadAloud();

    useEffect(() => {
        registerContent(contentRef, [
            t('artExploration.description1'),
            t('artExploration.description2')
        ]);
        return () => registerContent(null);
    }, [registerContent, t]);

    return (
        <div className="content-box" ref={contentRef}>
            <h1>{t('artExploration.title')}</h1>
            <p>
                {t('artExploration.description1')}
                <br></br>
                <br></br>
                {t('artExploration.description2')}
                <br></br>
                <br></br>
                {t('artExploration.description3')}
            </p>
            <ol className="instructions-list">
                <li>{t('artExploration.instruction1')}</li>
                <li>{t('artExploration.instruction2')}</li>
            </ol>
        </div>
    );
};

export default InstructionsSection;