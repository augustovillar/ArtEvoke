import React from 'react';
import { useTranslation } from 'react-i18next';
import './About.css';

const About = () => {
    const { t } = useTranslation('common');

    return (
        <div>
            <div className="content-box">
                <h1>{t('about.title')}</h1>
                <p>
                    {t('about.paragraph1')}
                </p>
                <p dangerouslySetInnerHTML={{ __html: t('about.paragraph2') }} />
                <p>
                    {t('about.paragraph3')}
                </p>
                <p>
                    {t('about.paragraph4')}
                </p>
            </div>
        </div>
    );
};

export default About;