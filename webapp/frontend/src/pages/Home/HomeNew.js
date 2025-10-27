import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18n';
import { useAuth } from '../../contexts';
import { useReadAloud } from '../../contexts/ReadAloudContext';
import './Home.css';
import storyImage from '../../assets/images/storyImage.png';
import artImage from '../../assets/images/artImage.png';

const Home = () => {
    const { t } = useTranslation('common');
    const navigate = useNavigate();
    const { isLoggedIn } = useAuth();
    const contentRef = useRef(null);
    const { registerContent } = useReadAloud();
    
    const [expandedMode, setExpandedMode] = useState(null);

    useEffect(() => {
        registerContent(contentRef, [
            t('home.memoryReconstructionDesc'),
            t('home.artExplorationDesc')
        ]);
        return () => registerContent(null);
    }, [registerContent, t]);

    const handleModeClick = (mode) => {
        if (isLoggedIn) {
            // Se logado, navega para o modo
            navigate(mode === 'memory' ? '/story' : '/artsearch');
        } else {
            // Se não logado, expande/recolhe a explicação
            setExpandedMode(expandedMode === mode ? null : mode);
        }
    };

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
                    {/* Memory Reconstruction Card */}
                    <div 
                        className={`option-card ${expandedMode === 'memory' ? 'expanded' : ''} ${!isLoggedIn ? 'clickable' : ''}`}
                        onClick={() => handleModeClick('memory')}
                    >
                        <div className="option-header">
                            <div className="option-icon-wrapper">
                                <img src={storyImage} alt={t('home.memoryReconstructionDesc')} className="option-icon" />
                            </div>
                            <span className="option-text">{t('home.memoryReconstruction')}</span>
                            <p className="option-brief">{t('home.memoryReconstructionDesc')}</p>
                        </div>

                        {!isLoggedIn && expandedMode === 'memory' && (
                            <div className="option-expanded-content">
                                <div className="expanded-section">
                                    <h3>{t('home.howItWorks')}</h3>
                                    <ol className="how-it-works-list">
                                        <li>{t('home.memoryStep1')}</li>
                                        <li>{t('home.memoryStep2')}</li>
                                        <li>{t('home.memoryStep3')}</li>
                                        <li>{t('home.memoryStep4')}</li>
                                    </ol>
                                </div>

                                <div className="expanded-section">
                                    <h3>{t('home.example')}</h3>
                                    <div className="example-content">
                                        <div className="example-images">
                                            {/* Placeholder para imagens de exemplo */}
                                            <div className="example-image-placeholder">
                                                <span>{t('home.exampleImage')} 1</span>
                                            </div>
                                            <div className="example-image-placeholder">
                                                <span>{t('home.exampleImage')} 2</span>
                                            </div>
                                            <div className="example-image-placeholder">
                                                <span>{t('home.exampleImage')} 3</span>
                                            </div>
                                        </div>
                                        <p className="example-description">
                                            {t('home.memoryExampleDesc')}
                                        </p>
                                    </div>
                                </div>

                                <button 
                                    className="collapse-button"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setExpandedMode(null);
                                    }}
                                >
                                    {t('home.showLess')}
                                </button>
                            </div>
                        )}

                        {!isLoggedIn && expandedMode !== 'memory' && (
                            <button className="expand-button">
                                {t('home.learnMore')}
                            </button>
                        )}
                    </div>

                    {/* Art Exploration Card */}
                    <div 
                        className={`option-card ${expandedMode === 'art' ? 'expanded' : ''} ${!isLoggedIn ? 'clickable' : ''}`}
                        onClick={() => handleModeClick('art')}
                    >
                        <div className="option-header">
                            <div className="option-icon-wrapper">
                                <img src={artImage} alt={t('home.artExplorationDesc')} className="option-icon" />
                            </div>
                            <span className="option-text">{t('home.artExploration')}</span>
                            <p className="option-brief">{t('home.artExplorationDesc')}</p>
                        </div>

                        {!isLoggedIn && expandedMode === 'art' && (
                            <div className="option-expanded-content">
                                <div className="expanded-section">
                                    <h3>{t('home.howItWorks')}</h3>
                                    <ol className="how-it-works-list">
                                        <li>{t('home.artStep1')}</li>
                                        <li>{t('home.artStep2')}</li>
                                        <li>{t('home.artStep3')}</li>
                                        <li>{t('home.artStep4')}</li>
                                    </ol>
                                </div>

                                <div className="expanded-section">
                                    <h3>{t('home.example')}</h3>
                                    <div className="example-content">
                                        <div className="example-story">
                                            <p className="example-text">
                                                {t('home.artExampleStory')}
                                            </p>
                                        </div>
                                        <div className="example-images">
                                            {/* Placeholder para imagens de exemplo */}
                                            <div className="example-image-placeholder">
                                                <span>{t('home.exampleImage')} 1</span>
                                            </div>
                                            <div className="example-image-placeholder">
                                                <span>{t('home.exampleImage')} 2</span>
                                            </div>
                                            <div className="example-image-placeholder">
                                                <span>{t('home.exampleImage')} 3</span>
                                            </div>
                                        </div>
                                        <p className="example-description">
                                            {t('home.artExampleDesc')}
                                        </p>
                                    </div>
                                </div>

                                <button 
                                    className="collapse-button"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setExpandedMode(null);
                                    }}
                                >
                                    {t('home.showLess')}
                                </button>
                            </div>
                        )}

                        {!isLoggedIn && expandedMode !== 'art' && (
                            <button className="expand-button">
                                {t('home.learnMore')}
                            </button>
                        )}
                    </div>
                </div>

                {!isLoggedIn && (
                    <div className="login-prompt">
                        <p>{t('home.loginPrompt')}</p>
                        <button 
                            className="login-prompt-button"
                            onClick={() => navigate('/auth/login-role-selection')}
                        >
                            {t('home.loginButton')}
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Home;
