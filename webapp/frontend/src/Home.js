import React, { useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import './Home.css';
import storyImage from './images/storyImage.png';
import artImage from './images/artImage.png';
import { useReadAloud } from './contexts/ReadAloudContext';

const Home = () => {
    const { t } = useTranslation('common');
    const contentRef = useRef(null);
    const { registerContent } = useReadAloud();

    useEffect(() => {
        registerContent(contentRef, [
            t('home.memoryReconstructionDesc'),
            t('home.artExplorationDesc')
        ]);
        return () => registerContent(null);
    }, [registerContent, t]);

    return (
        <div className="home-container">
            <div className="hero-section" ref={contentRef}>
                <h1 className="hero-title">{t('home.heroTitle')}</h1>
                <p className="hero-description">
                    {t('home.heroDescription')}
                </p>
            </div>

            <div className="options-section">
                <div className="options-grid">
                    <Link to="/story" className="option-card">
                        <div className="option-icon-wrapper">
                            <img src={storyImage} alt={t('home.memoryReconstructionDesc')} className="option-icon" />
                        </div>
                        <span className="option-text">{t('home.memoryReconstruction')}</span>
                        <p>{t('home.memoryReconstructionDesc')}</p>
                    </Link>
                    <Link to="/artsearch" className="option-card">
                        <div className="option-icon-wrapper">
                            <img src={artImage} alt={t('home.artExplorationDesc')} className="option-icon" />
                        </div>
                        <span className="option-text">{t('home.artExploration')}</span>
                        <p>{t('home.artExplorationDesc')}</p>
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default Home;