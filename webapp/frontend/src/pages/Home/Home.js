import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
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
    
    const [expandedMemory, setExpandedMemory] = useState(false);
    const [expandedArt, setExpandedArt] = useState(false);

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
            // Se não logado, expande/recolhe a explicação de forma independente
            if (mode === 'memory') {
                setExpandedMemory(!expandedMemory);
            } else {
                setExpandedArt(!expandedArt);
            }
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
                        className={`option-card ${expandedMemory ? 'expanded' : ''} ${!isLoggedIn ? 'clickable' : ''}`}
                        onClick={() => handleModeClick('memory')}
                    >
                        <div className="option-header">
                            <div className="option-icon-wrapper">
                                <img src={storyImage} alt={t('home.memoryReconstructionDesc')} className="option-icon" />
                            </div>
                            <span className="option-text">{t('home.memoryReconstruction')}</span>
                            <p className="option-brief">{t('home.memoryReconstructionDesc')}</p>
                        </div>

                        {!isLoggedIn && expandedMemory && (
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
                                        <div className="example-story">
                                            <p className="example-text">
                                                {t('home.memoryExampleStory')}
                                            </p>
                                        </div>
                                        <p className="example-description">
                                            {t('home.memoryExampleDesc')}
                                        </p>
                                        <div className="example-sections">
                                            <div className="example-section-item">
                                                <h4>{t('home.section')} 1</h4>
                                                <p className="section-text">{t('home.memorySection1')}</p>
                                                <div className="example-images">
                                                    <div className="example-image-placeholder selected">
                                                        <span>{t('home.selectedImage')}</span>
                                                    </div>
                                                    <div className="example-image-placeholder">
                                                        <span>{t('home.option')} 2</span>
                                                    </div>
                                                    <div className="example-image-placeholder">
                                                        <span>{t('home.option')} 3</span>
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="example-section-item">
                                                <h4>{t('home.section')} 2</h4>
                                                <p className="section-text">{t('home.memorySection2')}</p>
                                                <div className="example-images">
                                                    <div className="example-image-placeholder">
                                                        <span>{t('home.option')} 1</span>
                                                    </div>
                                                    <div className="example-image-placeholder selected">
                                                        <span>{t('home.selectedImage')}</span>
                                                    </div>
                                                    <div className="example-image-placeholder">
                                                        <span>{t('home.option')} 3</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <button 
                                    className="collapse-button"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setExpandedMemory(false);
                                    }}
                                >
                                    {t('home.showLess')}
                                </button>
                            </div>
                        )}

                        {!isLoggedIn && !expandedMemory && (
                            <button className="expand-button">
                                {t('home.learnMore')}
                            </button>
                        )}
                    </div>

                    {/* Art Exploration Card */}
                    <div 
                        className={`option-card ${expandedArt ? 'expanded' : ''} ${!isLoggedIn ? 'clickable' : ''}`}
                        onClick={() => handleModeClick('art')}
                    >
                        <div className="option-header">
                            <div className="option-icon-wrapper">
                                <img src={artImage} alt={t('home.artExplorationDesc')} className="option-icon" />
                            </div>
                            <span className="option-text">{t('home.artExploration')}</span>
                            <p className="option-brief">{t('home.artExplorationDesc')}</p>
                        </div>

                        {!isLoggedIn && expandedArt && (
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
                                        <div className="keywords-section">
                                            <h4>{t('home.keywordsEntered')}</h4>
                                            <div className="keywords-list">
                                                <span className="keyword-tag">{t('home.keyword1')}</span>
                                                <span className="keyword-tag">{t('home.keyword2')}</span>
                                                <span className="keyword-tag">{t('home.keyword3')}</span>
                                            </div>
                                        </div>
                                        <p className="example-description">
                                            {t('home.artSearchDesc')}
                                        </p>
                                        <div className="example-images">
                                            {/* Placeholder para imagens selecionadas */}
                                            <div className="example-image-placeholder selected">
                                                <span>{t('home.selectedImage')} 1</span>
                                            </div>
                                            <div className="example-image-placeholder selected">
                                                <span>{t('home.selectedImage')} 2</span>
                                            </div>
                                            <div className="example-image-placeholder selected">
                                                <span>{t('home.selectedImage')} 3</span>
                                            </div>
                                        </div>
                                        <p className="example-description">
                                            {t('home.artGenerationDesc')}
                                        </p>
                                        <div className="example-story">
                                            <p className="example-text">
                                                {t('home.artExampleStory')}
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                <button 
                                    className="collapse-button"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setExpandedArt(false);
                                    }}
                                >
                                    {t('home.showLess')}
                                </button>
                            </div>
                        )}

                        {!isLoggedIn && !expandedArt && (
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